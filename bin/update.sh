#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

LOG_DIR="$HOME/.update-config/logs"
mkdir -p "$LOG_DIR"
RUN_LOG="$LOG_DIR/run_$(date +%Y%m%d_%H%M%S).log"

function log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')][$1] $2" | tee -a "$RUN_LOG"
}

log "INFO" "Termux-Updater script started (dry-run mode)"
log "DEBUG" "Loading token from ~/.update-config/token"

TOKEN_FILE="$HOME/.update-config/token"
if [ ! -f "$TOKEN_FILE" ]; then
    log "ERROR" "Token file not found at $TOKEN_FILE"
    exit 2
fi

TOKEN=$(head -n 1 "$TOKEN_FILE")
MASKED_TOKEN="${TOKEN:0:8}... (hidden)"

log "DEBUG" "Token read successfully (masked): $MASKED_TOKEN"

# Check GitHub token validity
log "INFO" "Checking token validity..."
GH_API="https://api.github.com/user"
RESPONSE=$(curl -s -H "Authorization: token $TOKEN" "$GH_API")

if echo "$RESPONSE" | grep -q '"login":'; then
    LOGIN=$(echo "$RESPONSE" | jq -r '.login')
    log "INFO" "Token is valid for GitHub user: $LOGIN"
else
    log "ERROR" "Token invalid or not reachable"
    exit 3
fi

# Check expiration header
EXPIRY_HEADER=$(curl -sI -H "Authorization: token $TOKEN" https://api.github.com/ | grep -i "github-authentication-token-expiration:" | tail -n1 | awk '{print $2,$3,$4,$5,$6}')
if [ -n "$EXPIRY_HEADER" ]; then
    TOKEN_EXPIRY=$(date -d "$EXPIRY_HEADER" +%s)
    DAYS_LEFT=$(( (TOKEN_EXPIRY - $(date +%s)) / 86400 ))
    log "INFO" "Token expires on: $EXPIRY_HEADER ($DAYS_LEFT days left)"
    if [ "$DAYS_LEFT" -le 7 ]; then
        log "WARN" "Token expires within 7 days!"
    fi
    if [ "$DAYS_LEFT" -le 3 ]; then
        log "WARN" "Token expires within 3 days!"
    fi
    if [ "$DAYS_LEFT" -le 1 ]; then
        log "WARN" "Token expires within 1 day!"
        log "INFO" "[DRY-RUN] Would create GitHub issue for token renewal"
    fi
else
    log "WARN" "Token expiration header not found"
fi

# Cleanup old logs
log "INFO" "Cleaning old logs and temp files..."
find "$LOG_DIR" -type f -mtime +30 -exec rm -f {} \; || true
rm -rf "$HOME/.update-config/tmp/*" || true
log "INFO" "Cleanup done"

log "INFO" "Termux-Updater finished successfully"
