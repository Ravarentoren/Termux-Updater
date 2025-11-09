#!/data/data/com.termux/files/usr/bin/bash

# =======================
# Termux-Updater v1.0.4-test
# =======================

set -euo pipefail
IFS=$'\n\t'

DEBUG=1
LOG_DIR="$HOME/.update-config/logs"
TMP_DIR="$HOME/tmp"
TOKEN_FILE="$HOME/.update-config/token"
TOKEN_EXPIRY_FILE="$HOME/.update-config/token_expiry"
REPO="Ravarentoren/termux-updater"   # tvůj repozitář
EXPECTED_HASH=""

mkdir -p "$LOG_DIR" "$TMP_DIR"

log() {
    local level=$1
    shift
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')][$level] $*"
    echo "$msg" | tee -a "$LOG_DIR/run_$(date '+%Y%m%d_%H%M%S').log"
}

# -----------------------
# Načtení GitHub tokenu
# -----------------------
if [ ! -f "$TOKEN_FILE" ]; then
    log ERROR "No token found at $TOKEN_FILE"
    exit 2
fi
TOKEN=$(<"$TOKEN_FILE")
log DEBUG "Token read successfully (masked): ${TOKEN:0:10}..."

# -----------------------
# Ověření tokenu a expirace
# -----------------------
TMP_HEADERS=$(mktemp)
curl -sI -H "Authorization: token $TOKEN" https://api.github.com/ > "$TMP_HEADERS"

expiry_raw=$(grep -i 'github-authentication-token-expiration' "$TMP_HEADERS" | awk '{print $2" "$3" "$4}')
if [ -z "$expiry_raw" ]; then
    log WARN "GitHub token expiration header not found."
    days_left=-1
else
    expiry_epoch=$(date -d "$expiry_raw" +%s)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    log DEBUG "Token expires on $expiry_raw (approximately $days_left days left)"
    echo "$expiry_raw" > "$TOKEN_EXPIRY_FILE"
fi

# Upozornění podle dnů
if [ "$days_left" -le 7 ] && [ "$days_left" -gt 3 ]; then
    log WARN "Token expires in $days_left days (7-day warning)."
elif [ "$days_left" -le 3 ] && [ "$days_left" -gt 1 ]; then
    log WARN "Token expires in $days_left days (3-day warning)."
elif [ "$days_left" -le 1 ]; then
    log WARN "Token expires in $days_left days (1-day warning)."
fi

# -----------------------
# Vytvoření GitHub Issue při expiraci
# -----------------------
if [ "$days_left" -le 0 ]; then
    log INFO "Token expired. Creating GitHub issue..."
    ISSUE_TITLE="⚠️ Token expired: $(date '+%Y-%m-%d')"
    ISSUE_BODY="Token stored in Termux-Updater has expired or will expire today."
    curl -s -X POST \
        -H "Authorization: token $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/repos/$REPO/issues \
        -d "{\"title\":\"$ISSUE_TITLE\",\"body\":\"$ISSUE_BODY\"}" \
        && log INFO "GitHub issue created successfully."
fi

# -----------------------
# Regenerace manifestu
# -----------------------
if [ -f "$HOME/Termux-Updater/update.sh" ]; then
    CURRENT_HASH=$(sha256sum "$HOME/Termux-Updater/update.sh" | awk '{print $1}')
    if [ "$CURRENT_HASH" != "$EXPECTED_HASH" ]; then
        log DEBUG "Manifest hash mismatch, regenerating..."
        EXPECTED_HASH=$CURRENT_HASH
        log DEBUG "Manifest regenerated. Hash: $EXPECTED_HASH"
    fi
fi

# -----------------------
# Kontrola závislostí
# -----------------------
for dep in jq curl git; do
    if ! command -v $dep >/dev/null 2>&1; then
        log ERROR "Dependency missing: $dep"
        exit 3
    else
        log INFO "Dependency present: $dep"
    fi
done

# -----------------------
# Aktualizace systémových balíků
# -----------------------
log INFO "Updating system packages..."
pkg update -y && pkg upgrade -y
log INFO "System packages updated."

# -----------------------
# Cleanup
# -----------------------
log INFO "Cleaning old logs and temp files..."
rm -rf "$LOG_DIR"/*.log.old
rm -rf "$TMP_DIR"/* /data/data/com.termux/files/usr/tmp/* 2>/dev/null || true
log INFO "Cleanup done."

log INFO "Termux-Updater finished successfully."
exit 0
