#!/data/data/com.termux/files/usr/bin/bash
echo "[TEST] Checking required directories..."
for d in bin config docs examples modules logs scripts tests tmp; do
    [ -d "$d" ] && echo "OK: $d" || echo "MISSING: $d"
done
