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
  <!-- DONATION BUTTONS -->
<a href="https://www.paypal.com/donate/?hosted_button_id=TZR7VNGUEDE7L">
  <img src="https://img.shields.io/badge/Donate-PayPal-0070ba?style=for-the-badge&logo=paypal">
</a>

<a href="https://ko-fi.com/ravarentoren">
  <img src="https://ko-fi.com/img/githubbutton_sm.svg" />
</a>

<a href="https://liberapay.com/Ravarentoren/">
  <img src="https://img.shields.io/liberapay/patrons/Ravarentoren.svg?style=for-the-badge&logo=liberapay">
</a>
  <a href="https://ko-fi.com/rava
<!-- NO-TRANSLATE-END -->Termux-Updater Pro is an advanced, fully automated update and maintenance system
for the Termux environment.

It updates pkg, system pip, and multiple virtual environments (venv) simultaneously,
handles conflicts intelligently, generates structured JSON reports,
and ensures long-term stability for professional and long-term development workflows.


---

🚀 Key Features

Automatic update of:

Termux pkg packages

Termux system pip packages

All pip packages inside any number of virtual environments


Independent update pipelines for pkg / pip / venvs

Intelligent conflict detection and resolution

Process lock protection (no parallel runs)

JSON reports:

Aktualizator_seznam.json — clean inventory of updated packages

Aktualizator_issue.json — warnings, conflicts, errors


Fully autonomous daily operation

Designed for long-term project survival and reproducibility



---

⭐ Installation

1. Clone the repository

<!-- NO-TRANSLATE-START -->git clone https://github.com/Ravarentoren/Termux-Updater.git
cd Termux-Updater

<!-- NO-TRANSLATE-END -->2. Make the updater executable

<!-- NO-TRANSLATE-START -->chmod +x aktualizator/Termux-Updater-Pro.py

<!-- NO-TRANSLATE-END -->3. Create a global Termux command

<!-- NO-TRANSLATE-START -->ln -sf $(pwd)/aktualizator/Termux-Updater-Pro.py ~/bin/aktualizator

<!-- NO-TRANSLATE-END -->
---

🛠 Usage

Basic run aktualizator

Run with custom configuration
<!-- NO-TRANSLATE-START -->
aktualizator --mode C --verbose --venv-dir ~/venv<!-- NO-TRANSLATE-END -->

Dry-run test (no changes applied)
<!-- NO-TRANSLATE-START -->
aktualizator --dry-run --verbose<!-- NO-TRANSLATE-END -->
---

🧠 Update Modes Overview

<!-- NO-TRANSLATE-START -->Mode	Description<!-- NO-TRANSLATE-END -->

A<!-- NO-TRANSLATE-START -->Termux pkg<!-- NO-TRANSLATE-END --> only
B	pkg + system pip
C	pkg + system pip +<!-- NO-TRANSLATE-START --> all venv pip<!-- NO-TRANSLATE-END --> environments
D	Full autonomous mode (daily use) — recommended
---

📄 JSON Output Files

File Description
<!-- NO-TRANSLATE-START -->
Aktualizator_seznam.json <!-- NO-TRANSLATE-END -->Clean list of updated items
<!-- NO-TRANSLATE-START -->
Aktualizator_issue.json <!-- NO-TRANSLATE-END -->All warnings, conflicts, error.
Both files are always stored in:

<!-- NO-TRANSLATE-START -->~/storage/downloads/

<!-- NO-TRANSLATE-END -->
---

📘 Documentation

Czech documentation: docs/README_CZ.md



---

📝 License

This project is dual-licensed under:

MIT License

Apache License 2.0


You may freely choose either license according to your needs.


---

🤝 Contributing

Contributions, ideas, improvements, tests, and bug reports are welcome.
The project is designed to be open, transparent, and community-friendly.


---

❤️ Credits

Termux-Updater Pro is a collaboration between
Ravarentoren and ChatGPT (OpenAI),
built to create the world’s most reliable Termux automation and update system.
