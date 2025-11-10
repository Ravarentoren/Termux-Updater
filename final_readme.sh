#!/usr/bin/env bash
# final_readme.sh - Auto-generate README.md with badges and dynamic links
set -euo pipefail

REPO_DIR="${GITHUB_WORKSPACE:-$(pwd)}"
README_FILE="$REPO_DIR/README.md"
LOG_FILE="$REPO_DIR/.readme_update.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

get_latest_commit_link() {
    echo "https://github.com/Ravarentoren/Termux-Updater/commit/$(git rev-parse HEAD)"
}

get_latest_issue_link() {
    ISSUE_NUMBER=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
        "https://api.github.com/repos/Ravarentoren/Termux-Updater/issues?state=open&per_page=1" \
        | jq -r '.[0].number')
    if [ "$ISSUE_NUMBER" != "null" ]; then
        echo "https://github.com/Ravarentoren/Termux-Updater/issues/$ISSUE_NUMBER"
    else
        echo "No open issues"
    fi
}

LATEST_COMMIT=$(get_latest_commit_link)
LATEST_ISSUE=$(get_latest_issue_link)

cat > "$README_FILE" << README_EOF
# Termux-Updater

Automated README update by CI.

## Repository Status

- Latest commit: [$LATEST_COMMIT]($LATEST_COMMIT)
- Latest open issue: [$LATEST_ISSUE]($LATEST_ISSUE)

## Structure

- bin/
- config/
- scripts/
- docs/
- examples/
- modules/
- tests/
- tmp/

## License

Manifest + MIT

## Contributors

- Ravarentoren
- ChatGPT (GPT-5-mini)

## CI Status

![CI](https://github.com/Ravarentoren/Termux-Updater/actions/workflows/update_readme.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-0%25-red)

## Notes

This README is automatically updated by GitHub Actions.
README_EOF

log "INFO" "README.md generated successfully"
