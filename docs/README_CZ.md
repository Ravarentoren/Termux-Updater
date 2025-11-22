<p align="center">
  <img src="images/termux_updater_banner_github-1.png" width="650">
</p><p align="center">
  <a href="https://github.com/Ravarentoren/Termux-Updater/releases"><img src="https://img.shields.io/github/v/release/Ravarentoren/Termux-Updater?color=5cb85c&label=Latest%20Release&style=for-the-badge"></a>
  <a href="https://github.com/Ravarentoren/Termux-Updater/stargazers"><img src="https://img.shields.io/github/stars/Ravarentoren/Termux-Updater?style=for-the-badge"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT%20%2B%20Apache--2.0-blue.svg?style=for-the-badge"></a>
  <a href="docs/README_CZ.md"><img src="https://img.shields.io/badge/Docs-Czech-green?style=for-the-badge"></a>
</p>
---

Termux-Updater Pro (česky) is an advanced, fully automated update and maintenance system
for the Termux environment.

It updates pkg, system pip, and multiple virtual environments (venv) simultaneously,
handles conflicts intelligently, generates structured JSON reports,
and ensures long-term stability for demanding or professional workflows.


---

🚀 Key Features

Automatic updates for:

Termux pkg packages

Termux system pip packages

All pip packages across any number of virtual environments


Independent update pipelines (pkg / pip / venv)

Intelligent conflict detection and resolution

Lock system to prevent multiple parallel runs

JSON reporting:

Aktualizator_seznam.json — clean inventory of updated packages

Aktualizator_issue.json — warnings, conflicts, errors


Fully autonomous daily operation

Designed for long-term project reliability and reproducibility



---

⭐ Installation

1. Clone the repository

git clone https://github.com/Ravarentoren/Termux-Updater.git
cd Termux-Updater

2. Make the updater executable

chmod +x aktualizator/Termux-Updater-Pro.py

3. Create a global Termux command

ln -sf $(pwd)/aktualizator/Termux-Updater-Pro.py ~/bin/aktualizator


---

🛠 Usage

Basic run

aktualizator

Run with custom configuration

aktualizator --mode C --verbose --venv-dir ~/venv

Dry-run mode (no changes applied)

aktualizator --dry-run --verbose


---

🧠 Update Modes Overview

A — Termux pkg only
B — pkg + system pip
C — pkg + system pip + all venv pip environments
D — Full autonomous mode (recommended)


---

📄 JSON Output Files

Aktualizator_seznam.json — clean list of updated items
Aktualizator_issue.json — warnings, conflicts, errors

Both files are always stored in:
~/storage/downloads/


---

📘 Documentation

Czech documentation: docs/README_CZ.md


---

📝 License

This project is dual-licensed under:

MIT License

Apache License 2.0


You may freely choose either license as needed.


---

🤝 Contributing

Contributions, ideas, improvements, tests, and bug reports are welcome.
The project is designed to be open, transparent, and community-friendly.


---

❤️ Credits

Termux-Updater Pro (česky) is a collaboration between
Ravarentoren and ChatGPT (OpenAI),
built to create one of the most reliable Termux automation and update systems.
