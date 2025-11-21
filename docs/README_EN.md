<p align="center">
  2   <img src="images/termux_updater
    _banner_github-1.png" width="650"
    >
  3 </p>
  4
  5 <p align="center">
  6   <a href="https://github.com/Rav
    arentoren/Termux-Updater/releases
    "><img src="https://img.shields.i
    o/github/v/release/Ravarentoren/T
    ermux-Updater?color=5cb85c&label=
    Latest%20Release&style=for-the-ba
    dge"></a>
  7   <a href="https://github.com/Rav
    arentoren/Termux-Updater/stargaze
    rs"><img src="https://img.shields
    .io/github/stars/Ravarentoren/Ter
    mux-Updater?style=for-the-badge">
    </a>
  8   <a href="LICENSE"><img src="htt
    ps://img.shields.io/badge/License
    -MIT%20%2B%20Apache--2.0-blue.svg
    ?style=for-the-badge"></a>
  9   <a href="docs/README_EN.md"><im
    g src="https://img.shields.io/bad
    ge/Docs-English-green?style=for-t
    he-badge"></a>
 10   <a href="docs/README_CZ.md"><im
    g src="https://img.shields.io/bad
    ge/Docs-Czech-green?style=for-the
    -badge"></a>
 11 </p>

### Termux-Updater Pro

**Termux-Updater Pro** is an advanced, fully automated update and maintenance system
for the Termux environment.  
It updates **pkg**, **system pip**, and **all virtual environments (venv)** simultaneously,
handles conflicts intelligently, generates structured JSON reports,
and ensures long-term stability for demanding development workflows.

---

## 🚀 Key Features

- Automatic update of:
  - Termux **pkg** packages  
  - Termux **system pip** packages  
  - All pip packages inside **any number of virtual environments**  
- Independent update pipelines for pkg / pip / venv  
- Intelligent conflict detection & handling  
- Lock-file protection against parallel runs  
- JSON reports:
  - `Aktualizator_seznam.json` — clean inventory of updated packages  
  - `Aktualizator_issue.json` — warnings, conflicts, errors  
- Designed for long-term project stability  
- Suitable for daily autonomous maintenance

---

## [BOX] Project Structure

<p align="center">
  <img src="../images/termux_project_structure.svg" alt="Project structure — Termux Updater" width="950"/>
</p>

## [BOX] Architecture Diagram

<p align="center">
  <img src="../images/termux_updater_diagram.svg" alt="Termux Updater Diagram" width="850"/>
</p>

---

## ⭐ Installation

### 1. Clone the repository

```bash
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

Run with custom options

aktualizator --mode C --verbose --venv-dir ~/venv

Dry-run test (no changes applied)

aktualizator --dry-run --verbose


---

🧠 Update Modes Overview

Mode	Description

A	Update Termux pkg only
B	Update pkg + system pip
C	Update pkg + system pip + all venv environments
D	Full autonomous mode (daily use) — recommended



---

📄 JSON Output Files

File	Description

Aktualizator_seznam.json	Clean list of all updated components
Aktualizator_issue.json	All warnings, conflicts, errors


Output location (always):

~/storage/downloads/


---

📘 Documentation

Czech documentation: docs/README_CZ.md

English documentation: docs/README_EN.md



---

📝 License

This project is dual-licensed under:

MIT License

Apache License 2.0


Users may freely choose either license based on their needs.


---

🤝 Contributing

Contributions, ideas, improvements, testing and bug reports are welcome.
The project is designed to be open, transparent, and community-friendly.


---

❤️ Credits

Termux-Updater Pro is a collaboration between
Ravarentoren and ChatGPT,
designed to create the world’s most reliable Termux automation and update system.
