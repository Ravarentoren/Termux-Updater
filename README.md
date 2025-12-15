<p align="center">
  <img src="images/termux_updater_banner_github-1.png" width="650">
</p>

<p align="center">
  <a href="https://github.com/Ravarentoren/Termux-Updater/releases">
    <img src="https://img.shields.io/github/v/release/Ravarentoren/Termux-Updater?color=5cb85c&label=Latest%20Release&style=for-the-badge">
  </a>
  <a href="https://github.com/Ravarentoren/Termux-Updater/stargazers">
    <img src="https://img.shields.io/github/stars/Ravarentoren/Termux-Updater?style=for-the-badge">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT%20%2B%20Apache--2.0-blue.svg?style=for-the-badge">
  </a>
  <a href="docs/README_CZ.md">
    <img src="https://img.shields.io/badge/Docs-Czech-green?style=for-the-badge">
  </a>
</p>

<p align="center">
  <!-- DONATION BUTTONS -->
  <a href="https://www.paypal.com/donate/?hosted_button_id=TZR7VNGUEDE7L">
    <img src="https://img.shields.io/badge/Donate-PayPal-0070ba?style=for-the-badge&logo=paypal">
  </a>
  <a href="https://ko-fi.com/ravarentoren">
    <img src="https://ko-fi.com/img/githubbutton_sm.svg">
  </a>
  <a href="https://liberapay.com/Ravarentoren/">
    <img src="https://img.shields.io/liberapay/patrons/Ravarentoren.svg?style=for-the-badge&logo=liberapay">
  </a>
</p>

<!-- NO-TRANSLATE-START -->
## Termux-Updater Pro

**Termux-Updater Pro** is an advanced, fully automated update and maintenance system
for the **Termux** environment.

It is designed for long-term, professional, and reproducible workflows where
system stability matters more than blind updates.

<!-- NO-TRANSLATE-END -->


---

## 🚀 Quick Install (Termux)

Run this command directly in Termux:

<!-- NO-TRANSLATE-START -->
  bash:
<!-- NO-TRANSLATE-END -->

<!-- NO-TRANSLATE-START -->
pkg install git -y && \
git clone https://github.com/Ravarentoren/Termux-Updater.git && \
cd Termux-Updater && \
chmod +x aktualizator/Termux-Updater-Pro.py && \
mkdir -p ~/bin && \
ln -sf "$(pwd)/aktualizator/Termux-Updater-Pro.py" ~/bin/aktualizator
<!-- NO-TRANSLATE-END -->


After installation, simply run:

<!-- NO-TRANSLATE-START -->
aktualizator
<!-- NO-TRANSLATE-END -->


## ⚡ One-line Installation (Recommended)

For Termux users who want a fast and safe installation:

<!-- NO-TRANSLATE-START -->
   bash:
<!-- NO-TRANSLATE-END -->
pkg install -y curl
curl -fsSL https://raw.githubusercontent.com/Ravarentoren/Termux-Updater/main/scripts/install_termux_updater.sh | bash
<!-- NO-TRANSLATE-END -->

This will:

install required dependencies

clone or update Termux-Updater Pro

create a global aktualizator command

keep everything inside your home directory (no root)


After installation, simply run:
<!-- NO-TRANSLATE-START -->
aktualizator
<!-- NO-TRANSLATE-END -->


---

## 🚀 Key Features

- Automatic update of:
  - Termux `pkg` packages
  - Termux **system pip**
  - All `pip` packages inside any number of **virtual environments (venv)**

- Independent update pipelines for:
  -  pkg
  -  system pip
  -  venv pip

- Intelligent conflict detection and reporting  
- Safe process locking (no parallel runs)  
- Fully autonomous operation (ideal for daily or scheduled use)

### JSON Reports

- `Aktualizator_seznam.json` — clean inventory of updated packages
- `Aktualizator_issue.json` — warnings, conflicts, and errors

All reports are always stored in:

~/storage/downloads/



---

## ⭐ Installation

### 1. Clone the repository

<!-- NO-TRANSLATE-START -->
git clone https://github.com/Ravarentoren/Termux-Updater.git
cd Termux-Updater
<!-- NO-TRANSLATE-END -->

### 2. Make the updater executable

<!-- NO-TRANSLATE-START -->
chmod +x aktualizator/Termux-Updater-Pro.py
<!-- NO-TRANSLATE-END -->

### 3. Create a global Termux command

<!-- NO-TRANSLATE-START -->
ln -sf "$(pwd)/aktualizator/Termux-Updater-Pro.py" ~/bin/aktualizator
<!-- NO-TRANSLATE-END -->



---

## 🛠 Usage

### Basic run

<!-- NO-TRANSLATE-START -->
aktualizator
<!-- NO-TRANSLATE-END -->


### Custom configuration

<!-- NO-TRANSLATE-START -->
aktualizator --mode C --verbose --venv-dir ~/venv
<!-- NO-TRANSLATE-END -->


### Dry-run test (no changes applied)

<!-- NO-TRANSLATE-START -->
aktualizator --dry-run --verbose
<!-- NO-TRANSLATE-END -->



---

## 🧠 Update Modes Overview

### Mode	Description:



A) 	Termux pkg only

B) 	pkg + system pip

C) 	pkg + system pip + all venv pip

D) 	Full autonomous mode (recommended)



---

## 📘 Documentation

Czech documentation:
docs/README_CZ.md



---

## 📝 License

### This project is dual-licensed under:

MIT License

Apache License 2.0


You may freely choose either license according to your needs.


---

## 🤝 Contributing

Contributions, ideas, improvements, tests, and bug reports are welcome.
The project is designed to be open, transparent, and community-friendly.


---

## ❤️ Credits

Termux-Updater Pro is a collaboration between
Ravarentoren and ChatGPT (OpenAI),
created to build a robust, reliable, and future-proof automation system for the Termux ecosystem.
