#!/usr/bin/env python3
"""
Termux-Aktualizator (refaktor) — univerzální automatický aktualizátor pro Termux a Python venv.

Funkce:
 - Režimy:
    A = jen pkg (Termux)
    B = pkg + systémový pip
    C = pkg + systémový pip + venv pipy (výchozí)
    D = plný režim (pokud není --dry-run provede skutečné upgrade)
 - Vytvoří JSON inventář (Aktualizator_seznam.json) a JSON issues (Aktualizator_issue.json)
   v ~/storage/downloads/ (pokud existuje), jinak v ~/Downloads/.
 - Podpora --dry-run a --verbose.
 - Zámek běhu pomocí fcntl (safeguard).
"""

from __future__ import annotations
import argparse
import subprocess
import json
import os
import sys
import logging
import shutil
import time
import fcntl
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# Try optionally to use rich for nicer terminal output (not required)
try:
    from rich import print as rprint
    RICH = True
except Exception:
    RICH = False

# ---------- Konfigurace výstupu ----------
HOME = os.path.expanduser("~")
DEFAULT_DOWNLOADS = os.path.join(HOME, "storage", "downloads")
if not os.path.isdir(DEFAULT_DOWNLOADS):
    DEFAULT_DOWNLOADS = os.path.join(HOME, "Downloads")
OUT_INVENTORY = os.path.join(DEFAULT_DOWNLOADS, "Aktualizator_seznam.json")
OUT_ISSUES = os.path.join(DEFAULT_DOWNLOADS, "Aktualizator_issue.json")
LOCKFILE = os.path.join(HOME, ".aktualizator.lock")
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

# ---------- Logging ----------
logger = logging.getLogger("Aktualizator")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ---------- Helpery ----------
def run_cmd(cmd: List[str], dry_run: bool=False, capture: bool=True, check: bool=False, cwd: Optional[str]=None) -> Tuple[int, str, str]:
    """
    Spustí příkaz, vrátí (rc, stdout, stderr).
    Pokud dry_run True, neprovádí příkaz a vrací -1 / info.
    """
    logger.debug("Run cmd: %s (dry_run=%s)", " ".join(cmd), dry_run)
    if dry_run:
        return -1, f"[dry-run] {' '.join(cmd)}", ""
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None, check=False, cwd=cwd, text=True)
        out = proc.stdout or ""
        err = proc.stderr or ""
        logger.debug("Cmd rc=%s out=%d bytes err=%d bytes", proc.returncode, len(out), len(err))
        if check and proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd, output=out, stderr=err)
        return proc.returncode, out, err
    except FileNotFoundError as e:
        logger.warning("Command not found: %s", cmd[0])
        return 127, "", str(e)
    except Exception as e:
        logger.exception("Unexpected error running command: %s", cmd)
        return 255, "", str(e)

def file_lock(fd):
    """Zajistí exkluzivní flock (blocking)."""
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return True
    except Exception as e:
        logger.error("Unable to acquire lock: %s", e)
        return False

def safe_write_json(path: str, data: Any):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    logger.info("Writing %s", path)

def timestamp_now_iso() -> str:
    # timezone-aware would be better; keep simple UTC ISOZ
    return datetime.utcnow().isoformat() + "Z"

# ---------- Detekce prostředí ----------
def detect_package_manager() -> str:
    """Pro Termux doporučujeme 'pkg' (wrapper apt). Vrací název příkazu."""
    # prefer pkg, fallback apt or apk
    for cmd in ("pkg", "apt", "apk", "pacman"):
        if shutil.which(cmd):
            return cmd
    return "pkg"  # fallback

def find_system_pip() -> Optional[str]:
    # prefer pip3, else pip in PATH
    for name in ("pip3", "pip"):
        path = shutil.which(name)
        if path:
            return path
    return None

def find_venv_pips(venv_root: str) -> List[str]:
    """Prohledá adresář venv_root a najde bin/pip nebo Scripts/pip pro každý venv"""
    pips = []
    if not os.path.isdir(venv_root):
        return pips
    for name in os.listdir(venv_root):
        full = os.path.join(venv_root, name)
        if os.path.isdir(full):
            cand1 = os.path.join(full, "bin", "pip3")
            cand2 = os.path.join(full, "bin", "pip")
            cand3 = os.path.join(full, "Scripts", "pip.exe")
            for c in (cand1, cand2, cand3):
                if os.path.isfile(c) and os.access(c, os.X_OK):
                    pips.append(c)
                    break
    return pips

# ---------- Operace aktualizací a seznamu ----------
def pkg_update_and_list(pkg_cmd: str, dry_run: bool) -> Tuple[List[Dict[str,str]], List[Dict[str,Any]]]:
    """
    Spustí update/upgrade a vrátí tuple (installed_list, issues).
    installed_list: [{name, version}, ...]
    issues: [{category, cmd, rc, stderr}, ...]
    """
    issues = []
    installed = []
    # update & upgrade (režim záleží na dry_run)
    rc, out, err = run_cmd([pkg_cmd, "update", "-y"], dry_run=dry_run)
    if rc not in (-1, 0):
        issues.append({"category":"pkg_update", "cmd":[pkg_cmd, "update", "-y"], "rc":rc, "stderr":err})
    rc2, out2, err2 = run_cmd([pkg_cmd, "upgrade", "-y"], dry_run=dry_run)
    if rc2 not in (-1, 0):
        issues.append({"category":"pkg_upgrade", "cmd":[pkg_cmd, "upgrade", "-y"], "rc":rc2, "stderr":err2})
    # list installed packages
    rc3, out3, err3 = run_cmd([pkg_cmd, "list-installed"], dry_run=dry_run)
    if rc3 in (-1, 0):
        # parse if real output, otherwise if dry-run fill placeholder
        if dry_run:
            installed = []
        else:
            # format: name-version <arch> (varies). We'll try robust parse
            for line in out3.splitlines():
                line = line.strip()
                if not line:
                    continue
                # try "name-package-version" patterns
                parts = line.split()
                # typical Termux: "package/version arch [installed]" or "package-1.2.3"
                token = parts[0]
                # attempt to split token into name and version
                if "/" in token:
                    # e.g. "bash/5.1.4-3 aarch64 [installed]"
                    name_ver = token.split("/",1)[0]
                    # fallback: keep whole token
                    name = name_ver
                    version = "unknown"
                elif "-" in token:
                    # naive split: last '-' separates version
                    idx = token.rfind("-")
                    name = token[:idx] if idx>0 else token
                    version = token[idx+1:] if idx>0 else "unknown"
                else:
                    name = token
                    version = "unknown"
                installed.append({"name":name, "version":version, "raw":line})
    else:
        issues.append({"category":"pkg_list", "cmd":[pkg_cmd, "list-installed"], "rc":rc3, "stderr":err3})
    return installed, issues

def pip_list(pip_exe: str, dry_run: bool) -> Tuple[List[Dict[str,str]], Optional[Dict[str,Any]]]:
    """
    Vrací list pip packages [{name, version}, ...] a případnou issue dict.
    """
    issues = None
    cmd = [pip_exe, "list", "--format=json"]
    rc, out, err = run_cmd(cmd, dry_run=dry_run)
    if rc in (-1, 0):
        if dry_run:
            return [], None
        try:
            data = json.loads(out)
            pkgs = [{"name":p.get("name"), "version":p.get("version")} for p in data]
            return pkgs, None
        except Exception as e:
            issues = {"category":"pip_list_parse", "cmd":cmd, "rc":rc, "stderr":f"parse error: {e}; raw:{out[:200]}"}
            return [], issues
    else:
        issues = {"category":"pip_exec", "cmd":cmd, "rc":rc, "stderr":err}
        return [], issues

def pip_upgrade(pip_exe: str, dry_run: bool) -> Optional[Dict[str,Any]]:
    """Pokud není dry_run, provede `pip install --upgrade` pro všechny nainstalované balíčky."""
    if dry_run:
        return None
    # získat seznam
    pkgs, issue = pip_list(pip_exe, dry_run=False)
    if issue:
        return issue
    if not pkgs:
        return None
    names = [p["name"] for p in pkgs if p.get("name")]
    if not names:
        return None
    # pip install --upgrade pkg1 pkg2 ...
    cmd = [pip_exe, "install", "--upgrade"] + names
    rc, out, err = run_cmd(cmd, dry_run=False, capture=True)
    if rc != 0:
        return {"category":"pip_upgrade", "cmd":cmd, "rc":rc, "stderr":err}
    return None

# ---------- Hlavní orchestr ----------
def build_inventory_and_issues(mode: str, venv_dir: str, dry_run: bool, verbose: bool, do_upgrade: bool) -> Tuple[Dict[str,Any], List[Dict[str,Any]]]:
    """
    mode: 'A'|'B'|'C'|'D'
    do_upgrade: pokud True, provádí pip upgrade a pkg upgrade (pokud --dry-run False)
    """
    inventory: Dict[str,Any] = {
        "timestamp": timestamp_now_iso(),
        "mode": mode,
        "host": os.uname().nodename if hasattr(os, "uname") else "termux",
        "pkg": [],
        "system_pip": [],
        "venvs": {}
    }
    issues: List[Dict[str,Any]] = []
    pkg_cmd = detect_package_manager()
    logger.info("Using package manager: %s", pkg_cmd)
    # Režimy A/B/C/D:
    # A = only pkg
    # B = pkg + system pip list
    # C = pkg + system pip + venvs
    # D = full (like C but will do upgrades when do_upgrade True)
    # Krok 1: pkg update/list
    try:
        pkgs, pkg_issues = pkg_update_and_list(pkg_cmd, dry_run=dry_run and not do_upgrade)
        inventory["pkg"] = pkgs
        if pkg_issues:
            issues.extend(pkg_issues)
    except Exception as e:
        issues.append({"category":"pkg_exception", "cmd":[pkg_cmd,"update/upgrade/list"], "rc":255, "stderr":str(e)})
    # Krok 2: system pip (mode B/C/D)
    if mode in ("B","C","D"):
        system_pip = find_system_pip()
        if system_pip:
            logger.info("Using system pip at %s", system_pip)
            pkgs_sys, issue_sys = pip_list(system_pip, dry_run=dry_run)
            if pkgs_sys is not None:
                inventory["system_pip"] = pkgs_sys
            if issue_sys:
                issues.append(issue_sys)
            # upgrade system pip if requested (D and not dry_run)
            if mode == "D" and do_upgrade and not dry_run:
                up_issue = pip_upgrade(system_pip, dry_run=False)
                if up_issue:
                    issues.append(up_issue)
        else:
            issues.append({"category":"system_pip_missing", "cmd":["which pip3"], "rc":127, "stderr":"system pip not found"})
    # Krok 3: venv pips (mode C/D)
    if mode in ("C","D"):
        venv_pips = find_venv_pips(venv_dir)
        inventory["venvs"] = {}
        logger.info("Found %d venv pip executables under %s", len(venv_pips), venv_dir)
        for pip_exe in venv_pips:
            vname = os.path.basename(os.path.dirname(os.path.dirname(pip_exe)))  # try parent folder name
            pkgs_venv, issue_venv = pip_list(pip_exe, dry_run=dry_run)
            inventory["venvs"][vname] = {"pip": pip_exe, "packages": pkgs_venv}
            if issue_venv:
                issues.append({"venv": vname, **issue_venv})
            if mode == "D" and do_upgrade and not dry_run:
                up_ven = pip_upgrade(pip_exe, dry_run=False)
                if up_ven:
                    issues.append({"venv": vname, **up_ven})
    return inventory, issues

# ---------- CLI ----------
def parse_args():
    p = argparse.ArgumentParser(description="Termux-Aktualizator (refaktor).")
    p.add_argument("--mode", choices=["A","B","C","D"], default="C", help="Režim: A=pkg, B=pkg+sys-pip, C=+venvs, D=full (upgrade) (default C)")
    p.add_argument("--venv-dir", default=os.path.join(HOME, "venv"), help="Adresář, kde hledat venvs (default ~/venv)")
    p.add_argument("--dry-run", action="store_true", help="Neprovádět změny; pouze simulace")
    p.add_argument("--verbose", action="store_true", help="Verbose logging")
    p.add_argument("--no-lock", action="store_true", help="Nepoužívat zámek (pro debug)")
    p.add_argument("--out-inventory", default=OUT_INVENTORY, help="Cesta k inventárnímu JSON (výstup)")
    p.add_argument("--out-issues", default=OUT_ISSUES, help="Cesta k issues JSON")
    return p.parse_args()

def main():
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug("Starting Aktualizator, args: %s", vars(args))
    # Acquire lock
    lock_fd = None
    if not args.no_lock:
        try:
            lock_fd = open(LOCKFILE, "w")
            if not file_lock(lock_fd):
                logger.error("Unable to lock, exiting.")
                sys.exit(1)
            logger.debug("Acquired process lock %s", LOCKFILE)
        except Exception as e:
            logger.error("Lockfile error: %s", e)
            sys.exit(2)
    try:
        inventory, issues = build_inventory_and_issues(mode=args.mode, venv_dir=args.venv_dir, dry_run=args.dry_run, verbose=args.verbose, do_upgrade=(args.mode=="D"))
        # Always make sure timestamps and metadata are included
        inventory_meta = {
            "generated": timestamp_now_iso(),
            "mode": args.mode,
            "dry_run": bool(args.dry_run),
            "inventory": inventory
        }
        # Remove stderr text from inventory (inventory must be "clean and without error messages")
        # issues keep all error details.
        # Write outputs
        try:
            os.makedirs(os.path.dirname(args.out_inventory), exist_ok=True)
            os.makedirs(os.path.dirname(args.out_issues), exist_ok=True)
        except Exception:
            pass
        safe_write_json(args.out_inventory, inventory_meta)
        safe_write_json(args.out_issues, {"generated": timestamp_now_iso(), "issues": issues})
        # Print summary to terminal (issues only to terminal)
        if issues:
            logger.warning("Package manager issues: %d", len(issues))
            for it in issues:
                logger.warning(json.dumps(it, ensure_ascii=False))
        else:
            logger.info("No issues detected.")
        logger.info("Aktualizator finished.")
    finally:
        # release lock
        if lock_fd:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
                logger.debug("Released lock.")
            except Exception:
                pass

if __name__ == "__main__":
    main()
