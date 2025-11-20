# Termux-Updater Pro

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

## 📦 Project Structure

Termux-Updater/ │── aktualizator/ │     └── Termux-Updater-Pro.py │ │── docs/ │     ├── README_CZ.md │     └── README_EN.md │ │── images/ │     └── diagram.png       (placeholder for system structure diagram) │ │── LICENSE └── README.md

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
