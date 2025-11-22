#!/usr/bin/env python3
"""
Termux-Updater Pro — univerzální automatický aktualizátor pro Termux pkg + system pip + venv pip,
s detailním self-repair módem.

Režimy:
  A = pouze pkg
  B = pkg + systémový pip
  C = pkg + systémový pip + všechny venv (výchozí)
  D = jako C + provede skutečné pip upgrade

Výstupy:
  - Aktualizator_seznam.json        : čistý inventář
  - Aktualizator_issue.json         : všechny varování/chyby
  - Aktualizator_repair_log.json    : log z opravného běhu

JSON se ukládají do:
  ~/storage/downloads/  pokud existuje,
  jinak ~/Downloads/
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import fcntl
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# -------------------------------------------------------------
# Základní cesty & logging
# -------------------------------------------------------------

HOME = os.path.expanduser("~")

# Detekce download adresáře
DEFAULT_DOWNLOADS = os.path.join(HOME, "storage", "downloads")
if not os.path.isdir(DEFAULT_DOWNLOADS):
    DEFAULT_DOWNLOADS = os.path.join(HOME, "Downloads")

OUT_INVENTORY = os.path.join(DEFAULT_DOWNLOADS, "Aktualizator_seznam.json")
OUT_ISSUES = os.path.join(DEFAULT_DOWNLOADS, "Aktualizator_issue.json")
OUT_REPAIR_LOG = os.path.join(DEFAULT_DOWNLOADS, "Aktualizator_repair_log.json")

LOCKFILE = os.path.join(HOME, ".aktualizator.lock")

# Termux PREFIX (umístění apt konfigurace)
PREFIX = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
APT_DIR = os.path.join(PREFIX, "etc", "apt")
APT_SOURCES = [
    os.path.join(APT_DIR, "sources.list"),
    os.path.join(APT_DIR, "sources.list.d", "game.list"),
    os.path.join(APT_DIR, "sources.list.d", "science.list"),
    os.path.join(APT_DIR, "sources.list.d", "x11.list"),
]

LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
logger = logging.getLogger("Aktualizator")
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)

# -------------------------------------------------------------
# Helper funkce
# -------------------------------------------------------------

def timestamp_now_iso() -> str:
    """Vrátí aktuální čas jako timezone-aware ISO string (UTC)."""
    return datetime.now(timezone.utc).isoformat()


def run_cmd(
    cmd: List[str],
    dry_run: bool = False,
    capture: bool = True,
) -> Tuple[int, str, str]:
    """
    Spustí příkaz a vrátí (rc, stdout, stderr).

    Pokud je dry_run True, příkaz se nespustí a rc = -1.
    """
    if dry_run:
        return -1, "[dry-run] " + " ".join(cmd), ""

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except Exception as e:  # pragma: no cover (Termux-specific)
        return 255, "", str(e)


def safe_write_json(path: str, data: Any) -> None:
    """Bezpečné (atomické) zapsání JSON souboru."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    logger.info("Writing %s", path)


def file_lock(fd) -> bool:
    """Exkluzivní zámek na file descriptoru."""
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return True
    except Exception as e:
        logger.error("Unable to acquire lock: %s", e)
        return False

# -------------------------------------------------------------
# Detekce prostředí
# -------------------------------------------------------------

def detect_package_manager() -> str:
    """Preferuje Termux 'pkg', fallback na apt/apk/pacman."""
    for cmd in ("pkg", "apt", "apk", "pacman"):
        if shutil.which(cmd):
            return cmd
    return "pkg"


def find_system_pip() -> Optional[str]:
    for name in ("pip3", "pip"):
        path = shutil.which(name)
        if path:
            return path
    return None


def find_venv_pips(venv_root: str) -> List[str]:
    """
    Najde pip exáče ve virtuálních prostředích pod venv_root.
    Očekává layout ~/venv/<jmeno>/bin/pip3.
    """
    pips: List[str] = []
    if not os.path.isdir(venv_root):
        return pips

    for name in os.listdir(venv_root):
        full = os.path.join(venv_root, name)
        if not os.path.isdir(full):
            continue
        cand = os.path.join(full, "bin", "pip3")
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            pips.append(cand)
    return pips

# -------------------------------------------------------------
# Mirror / APT helpery
# -------------------------------------------------------------

_MIRROR_ERROR_HINTS = ("is not signed", "NO_PUBKEY", "EXPKEYSIG")


def extract_bad_mirror_hosts(stderr: str) -> List[str]:
    """
    Z apt stderr se pokusí vytáhnout hostname mirrorů, jejichž repo není podepsané.
    """
    hosts: set[str] = set()

    for line in stderr.splitlines():
        if "The repository" in line and "InRelease" in line:
            if not any(hint in line for hint in _MIRROR_ERROR_HINTS):
                continue
            # Příklad:
            # E: The repository 'https://mirror.mwt.me/termux/main stable InRelease' is not signed.
            m = re.search(r"'(https?://[^'\s]+)", line)
            if not m:
                continue
            url = m.group(1)
            host_match = re.match(r"https?://([^/]+)", url)
            if host_match:
                hosts.add(host_match.group(1))

    return sorted(hosts)


def sanitize_apt_sources(bad_hosts: List[str]) -> List[Dict[str, str]]:
    """
    Zakomentuje řádky v APT sources, které odkazují na problematické mirror hostname.

    Vrací seznam změn:
        [{"file": path, "line": původní_řádek}, ...]
    """
    changes: List[Dict[str, str]] = []
    if not bad_hosts:
        return changes

    for path in APT_SOURCES:
        if not os.path.isfile(path):
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            continue

        modified = False
        new_lines: List[str] = []

        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                new_lines.append(line)
                continue

            if any(host in line for host in bad_hosts):
                # tento řádek zakomentujeme
                new_lines.append("# disabled by Termux-Updater (bad mirror)\n")
                new_lines.append("# " + line)
                modified = True
                changes.append({"file": path, "line": line.strip()})
            else:
                new_lines.append(line)

        if modified:
            try:
                backup = path + ".bak"
                shutil.copy2(path, backup)
            except Exception:
                pass
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            except Exception:
                # když zápis selže, necháme původní stav
                continue

    return changes

# -------------------------------------------------------------
# Operace pkg / pip
# -------------------------------------------------------------

def pkg_update_and_list(pkg_cmd: str, dry_run: bool) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Spustí pkg update/upgrade a list-installed.

    Vrací:
        (packages, issues)
        packages: [{name, version}]
        issues : list dictů s category/cmd/rc/stderr
    """
    issues: List[Dict[str, Any]] = []
    packages: List[Dict[str, str]] = []

    # update
    rc_upd, out_upd, err_upd = run_cmd([pkg_cmd, "update", "-y"], dry_run)
    if rc_upd not in (-1, 0):
        issues.append({
            "category": "pkg_update",
            "cmd": [pkg_cmd, "update", "-y"],
            "rc": rc_upd,
            "stderr": err_upd,
        })

    # upgrade
    rc_upg, out_upg, err_upg = run_cmd([pkg_cmd, "upgrade", "-y"], dry_run)
    if rc_upg not in (-1, 0):
        issues.append({
            "category": "pkg_upgrade",
            "cmd": [pkg_cmd, "upgrade", "-y"],
            "rc": rc_upg,
            "stderr": err_upg,
        })

    # list-installed
    rc_list, out_list, err_list = run_cmd([pkg_cmd, "list-installed"], dry_run)
    if rc_list in (-1, 0):
        if not dry_run:
            for line in out_list.splitlines():
                line = line.strip()
                if not line:
                    continue
                token = line.split()[0]
                if "/" in token:
                    name = token.split("/")[0]
                    version = "unknown"
                elif "-" in token:
                    i = token.rfind("-")
                    name = token[:i]
                    version = token[i + 1 :]
                else:
                    name = token
                    version = "unknown"
                packages.append({"name": name, "version": version})
    else:
        issues.append({
            "category": "pkg_list",
            "cmd": [pkg_cmd, "list-installed"],
            "rc": rc_list,
            "stderr": err_list,
        })

    return packages, issues


def pip_list(pip_exe: str, dry_run: bool) -> Tuple[List[Dict[str, str]], Optional[Dict[str, Any]]]:
    """
    `pip list --format=json`
    """
    cmd = [pip_exe, "list", "--format=json"]
    rc, out, err = run_cmd(cmd, dry_run)
    if rc in (-1, 0):
        if dry_run:
            return [], None
        try:
            data = json.loads(out)
        except Exception as e:
            return [], {
                "category": "pip_list_parse",
                "cmd": cmd,
                "rc": rc,
                "stderr": f"parse error: {e}; raw: {out[:200]}",
            }
        pkgs = [{"name": p.get("name"), "version": p.get("version")} for p in data]
        return pkgs, None

    return [], {"category": "pip_exec", "cmd": cmd, "rc": rc, "stderr": err}


def pip_upgrade(pip_exe: str, dry_run: bool) -> Optional[Dict[str, Any]]:
    """
    `pip install --upgrade` pro všechny nainstalované balíčky.
    Používá se jen v režimu D a nikdy s --dry-run.
    """
    if dry_run:
        return None

    pkgs, issue = pip_list(pip_exe, dry_run=False)
    if issue:
        return issue
    if not pkgs:
        return None

    names = [p["name"] for p in pkgs if p.get("name")]
    if not names:
        return None

    cmd = [pip_exe, "install", "--upgrade"] + names
    rc, out, err = run_cmd(cmd, dry_run=False)
    if rc != 0:
        return {"category": "pip_upgrade", "cmd": cmd, "rc": rc, "stderr": err}
    return None

# -------------------------------------------------------------
# Repair systém – důkladná oprava Termux prostředí
# -------------------------------------------------------------

def run_repair_routines() -> Dict[str, Any]:
    """
    Důkladná opravná sekvence pro Termux-Updater prostředí.

    - Spustí pkg update/upgrade a zachytí chyby mirrorů.
    - Zkusí detekovat a zakomentovat rozbité mirrory (not signed, bad key).
    - Vyčistí pip cache a dočasné adresáře Termuxu.
    - Opraví ~/bin/aktualizator symlink a executable bit.
    """
    results: Dict[str, Any] = {
        "timestamp": timestamp_now_iso(),
        "steps": [],
    }

    def _log(msg: str) -> None:
        logger.info(msg)
        results["steps"].append(msg)

    _log("==> Repair: starting Termux-Updater repair sequence")

    bad_hosts: List[str] = []

    # 1. pkg update / upgrade, chyby uložíme
    _log("[step] pkg update/upgrade via 'pkg'")
    rc_upd, out_upd, err_upd = run_cmd(["pkg", "update", "-y"], dry_run=False)
    if rc_upd != 0:
        _log(f"[warn] pkg update failed (rc={rc_upd}):\n{err_upd[:400]}")
        bad_hosts.extend(extract_bad_mirror_hosts(err_upd))

    rc_upg, out_upg, err_upg = run_cmd(["pkg", "upgrade", "-y"], dry_run=False)
    if rc_upg != 0:
        _log(f"[warn] pkg upgrade failed (rc={rc_upg}):\n{err_upg[:400]}")
        bad_hosts.extend(extract_bad_mirror_hosts(err_upg))

    # 1b. Pokud jsme našli špatné mirrory – upravíme APT sources a zkusíme to znovu
    unique_bad = sorted(set(bad_hosts))
    if unique_bad:
        _log(f"[step] Detected problematic mirrors: {', '.join(unique_bad)}")
        changes = sanitize_apt_sources(unique_bad)
        if changes:
            for ch in changes:
                _log(f"[fix] Disabled mirror in {ch['file']}: {ch['line']}")
            _log("[step] Retrying pkg update/upgrade after mirror fix...")
            rc2, _, err2 = run_cmd(["pkg", "update", "-y"], dry_run=False)
            if rc2 != 0:
                _log(f"[warn] pkg update still failing after mirror fix (rc={rc2}):\n{err2[:400]}")
            rc3, _, err3 = run_cmd(["pkg", "upgrade", "-y"], dry_run=False)
            if rc3 != 0:
                _log(f"[warn] pkg upgrade still failing after mirror fix (rc={rc3}):\n{err3[:400]}")
        else:
            _log("[info] No APT source files modified while sanitizing mirrors.")

    # 2. Vyčištění pip cache
    _log("[step] Cleaning pip caches...")
    for cache in ["~/.cache/pip", "~/.cache/jupyter", "~/.cache/pip-tools"]:
        path = os.path.expanduser(cache)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            _log(f"[clean] Removed cache: {path}")

    # 3. Vyčištění dočasných adresářů Termuxu
    _log("[step] Cleaning Termux temporary directories...")
    for tmpdir in ["~/tmp", "/data/data/com.termux/files/usr/tmp"]:
        path = os.path.expanduser(tmpdir)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            _log(f"[clean] Removed tmp: {path}")

    # 4. Oprava symlinku ~/bin/aktualizator + executable bit
    _log("[step] Repairing aktualizator symlink and executable bit...")
    exe = os.path.join(HOME, "Termux-Updater", "aktualizator", "Termux-Updater-Pro.py")
    bindir = os.path.join(HOME, "bin")
    os.makedirs(bindir, exist_ok=True)
    symlink = os.path.join(bindir, "aktualizator")

    try:
        if os.path.islink(symlink) or os.path.isfile(symlink):
            os.remove(symlink)
        os.symlink(exe, symlink)
        _log(f"[ok] Recreated symlink: {symlink} -> {exe}")
    except Exception as e:
        _log(f"[warn] Failed to repair symlink: {e}")

    try:
        os.chmod(exe, 0o755)
        _log(f"[ok] Ensured executable bit on: {exe}")
    except Exception as e:
        _log(f"[warn] Failed to chmod main script: {e}")

    _log("==> Repair: completed")

    # Repair log uložíme i standardně
    safe_write_json(OUT_REPAIR_LOG, results)
    return results

# -------------------------------------------------------------
# Orchestr – inventář
# -------------------------------------------------------------

def build_inventory_and_issues(
    mode: str,
    venv_dir: str,
    dry_run: bool,
    verbose: bool,
    do_upgrade: bool,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Orchestruje pkg + pip + venv inventář a upgrady.

    mode: 'A'|'B'|'C'|'D'
    do_upgrade: pokud True a mode == 'D', provede pip upgrade (nikdy s --dry-run).
    """
    inventory: Dict[str, Any] = {
        "timestamp": timestamp_now_iso(),
        "mode": mode,
        "host": os.uname().nodename if hasattr(os, "uname") else "termux",
        "pkg": [],
        "system_pip": [],
        "venvs": {},
    }
    issues: List[Dict[str, Any]] = []

    pkg_cmd = detect_package_manager()
    logger.info("Using package manager: %s", pkg_cmd)

    # Krok 1: pkg
    pkgs, pkg_issues = pkg_update_and_list(pkg_cmd, dry_run=dry_run)
    inventory["pkg"] = pkgs
    issues.extend(pkg_issues)

    # Krok 2: system pip (B, C, D)
    if mode in ("B", "C", "D"):
        sys_pip = find_system_pip()
        if sys_pip:
            logger.info("Using system pip at %s", sys_pip)
            pkgs_sys, issue_sys = pip_list(sys_pip, dry_run=dry_run)
            inventory["system_pip"] = pkgs_sys
            if issue_sys:
                issues.append(issue_sys)

            if mode == "D" and do_upgrade and not dry_run:
                up_issue = pip_upgrade(sys_pip, dry_run=False)
                if up_issue:
                    issues.append(up_issue)
        else:
            issues.append({
                "category": "system_pip_missing",
                "cmd": ["which pip3"],
                "rc": 127,
                "stderr": "system pip not found in PATH",
            })

    # Krok 3: venv pipy (C, D)
    if mode in ("C", "D"):
        venv_pips = find_venv_pips(venv_dir)
        logger.info("Found %d venv pip executables under %s", len(venv_pips), venv_dir)
        for pip_exe in venv_pips:
            vname = os.path.basename(os.path.dirname(os.path.dirname(pip_exe)))
            pkgs_venv, issue_venv = pip_list(pip_exe, dry_run=dry_run)
            inventory["venvs"][vname] = {
                "pip": pip_exe,
                "packages": pkgs_venv,
            }
            if issue_venv:
                issue_venv = dict(issue_venv)
                issue_venv["venv"] = vname
                issues.append(issue_venv)

            if mode == "D" and do_upgrade and not dry_run:
                up_issue = pip_upgrade(pip_exe, dry_run=False)
                if up_issue:
                    up_issue = dict(up_issue)
                    up_issue["venv"] = vname
                    issues.append(up_issue)

    return inventory, issues

# -------------------------------------------------------------
# CLI
# -------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Termux-Aktualizator — pkg + pip + venv aktualizátor s repair módem."
    )

    p.add_argument(
        "--mode",
        choices=["A", "B", "C", "D"],
        default="C",
        help="Režim: A=pkg, B=pkg+sys-pip, C=+venvs (výchozí), D=full upgrade",
    )
    p.add_argument(
        "--venv-dir",
        default=os.path.join(HOME, "venv"),
        help="Adresář kde hledat venvs (default: ~/venv)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Pouze simulace, bez změn.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Detailní DEBUG výstup.",
    )
    p.add_argument(
        "--no-lock",
        action="store_true",
        help="Nepoužívat zámek (pouze pro ladění).",
    )
    p.add_argument(
        "--out-inventory",
        default=OUT_INVENTORY,
        help="Cesta pro inventární JSON (výchozí: downloads).",
    )
    p.add_argument(
        "--out-issues",
        default=OUT_ISSUES,
        help="Cesta pro issues JSON (výchozí: downloads).",
    )
    p.add_argument(
        "--repair",
        action="store_true",
        help="Spustit důkladnou opravu před aktualizací.",
    )
    p.add_argument(
        "--repair-only",
        action="store_true",
        help="Spustit pouze repair a skončit (bez aktualizace).",
    )
    p.add_argument(
        "--repair-log",
        default=OUT_REPAIR_LOG,
        help="Cesta pro repair log JSON (výchozí: downloads).",
    )

    return p.parse_args()

# -------------------------------------------------------------
# main()
# -------------------------------------------------------------

def main() -> None:
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug("Starting Aktualizator, args: %s", vars(args))

    # Repair mód (bez locku – aby šel spustit i při rozbitém zámku)
    if args.repair or args.repair_only:
        logger.info("Running repair routines (requested by user)...")
        repair_result = run_repair_routines()
        safe_write_json(args.repair_log, repair_result)
        logger.info("Repair log written to %s", args.repair_log)
        if args.repair_only:
            logger.info("Repair-only mode, exiting.")
            return

    # Standardní běh se zámkem
    lock_fd = None
    if not args.no_lock:
        try:
            lock_fd = open(LOCKFILE, "w")
            if not file_lock(lock_fd):
                logger.error("Unable to obtain lock, exiting.")
                sys.exit(1)
        except Exception as e:
            logger.error("Lockfile error: %s", e)
            sys.exit(2)

    try:
        inventory, issues = build_inventory_and_issues(
            mode=args.mode,
            venv_dir=args.venv_dir,
            dry_run=args.dry_run,
            verbose=args.verbose,
            do_upgrade=(args.mode == "D"),
        )

        out_inventory = {
            "generated": timestamp_now_iso(),
            "mode": args.mode,
            "dry_run": bool(args.dry_run),
            "inventory": inventory,
        }
        out_issues = {
            "generated": timestamp_now_iso(),
            "issues": issues,
        }

        safe_write_json(args.out_inventory, out_inventory)
        safe_write_json(args.out_issues, out_issues)

        if issues:
            logger.warning("Package manager issues: %d", len(issues))
            for it in issues:
                logger.warning(json.dumps(it, ensure_ascii=False))
        else:
            logger.info("No issues detected.")

        logger.info("Aktualizator finished.")
    finally:
        if lock_fd:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
