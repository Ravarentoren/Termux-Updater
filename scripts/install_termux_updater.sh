#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_URL="https://github.com/Ravarentoren/Termux-Updater.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/Termux-Updater}"
CMD_NAME="${CMD_NAME:-aktualizator}"

echo "==> Termux-Updater Pro installer (Termux)"
echo ""

echo "==> Updating package lists..."
pkg update -y || true

echo "==> Installing required packages..."
pkg install -y git python || true

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "==> Repository already exists, updating..."
  cd "$INSTALL_DIR"
  git pull --ff-only || git pull
else
  echo "==> Cloning repository into: $INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

echo "==> Making updater executable..."
chmod +x aktualizator/Termux-Updater-Pro.py

echo "==> Creating ~/bin and global command symlink..."
mkdir -p "$HOME/bin"
ln -sf "$INSTALL_DIR/aktualizator/Termux-Updater-Pro.py" "$HOME/bin/$CMD_NAME"

if ! echo "$PATH" | grep -q "$HOME/bin"; then
  echo ""
  echo "⚠️  NOTE:"
  echo "Add ~/bin to your PATH by adding this line to ~/.bashrc:"
  echo 'export PATH="$HOME/bin:$PATH"'
fi

echo ""
echo "✅ Installation finished."
echo "You can now run:"
echo "  $CMD_NAME"
echo ""
