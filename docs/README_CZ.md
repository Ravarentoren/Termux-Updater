<p align="center">
  <img src="../images/termux_updater_banner_github-1.png" width="650">
</p><p align="center">
  <a href="https://github.com/Ravarentoren/Termux-Updater/releases"><img src="https://img.shields.io/github/v/release/Ravarentoren/Termux-Updater?color=5cb85c&label=Latest%20Release&style=for-the-badge"></a>
  <a href="https://github.com/Ravarentoren/Termux-Updater/stargazers"><img src="https://img.shields.io/github/stars/Ravarentoren/Termux-Updater?style=for-the-badge"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT%20%2B%20Apache--2.0-blue.svg?style=for-the-badge"></a>
  <a href="README_CZ.md"><img src="https://img.shields.io/badge/Docs-Czech-green?style=for-the-badge"></a>
</p>
---

Termux-Updater Pro je pokročilý, plně automatizovaný systém pro aktualizaci a údržbu prostředí Termux.

Aktualizuje pkg, system pip i více virtuálních prostředí (venv) současně,
inteligentně řeší konflikty, generuje strukturované JSON reporty
a zajišťuje dlouhodobou stabilitu pro vývojové i produkční nasazení.


---

🚀 Klíčové vlastnosti

Automatická aktualizace:

Termux balíčků (pkg)

systémových pip balíčků (system pip)

pip balíčků uvnitř libovolného počtu virtuálních prostředí


Nezávislé aktualizační pipeline pro pkg / pip / venv

Inteligentní detekce a řešení konfliktů

Ochrana proti paralelnímu běhu – process-lock

JSON výstupy:

Aktualizator_seznam.json — čistý seznam aktualizovaných položek

Aktualizator_issue.json — varování, konflikty a chyby


Plně autonomní každodenní provoz

Navrženo pro dlouhodobou udržitelnost projektů a reprodukovatelnost



---

⭐ Instalace

1. Naklonování repozitáře

git clone https://github.com/Ravarentoren/Termux-Updater.git
cd Termux-Updater

2. Zpřístupnění updateru

chmod +x aktualizator/Termux-Updater-Pro.py

3. Vytvoření globálního příkazu Termuxu

ln -sf $(pwd)/aktualizator/Termux-Updater-Pro.py ~/bin/aktualizator


---

🛠 Použití

Základní spuštění:

aktualizator

Vlastní konfigurace:

aktualizator --mode C --verbose --venv-dir ~/venv

Testovací běh (bez změn):

aktualizator --dry-run --verbose


---

🧠 Přehled aktualizačních módů

Mód	Popis

A	Pouze Termux pkg
B	pkg + system pip
C	pkg + system pip + všechny venv pip prostředí
D	Plně autonomní režim (doporučeno pro každodenní použití)



---

📄 JSON výstupní soubory

Soubor	Popis

Aktualizator_seznam.json	Čistý seznam aktualizovaných položek
Aktualizator_issue.json	Varování, chyby, konflikty


Oba soubory se ukládají do:

~/storage/downloads/


---

📘 Dokumentace

Česká dokumentace: docs/README_CZ.md

Anglická dokumentace: hlavní README.md



---

📝 Licence

Projekt je duálně licencován pod:

MIT License

Apache License 2.0


Je možné si svobodně zvolit tu, která vyhovuje více.


---

🤝 Přispívání

Příspěvky, nápady, vylepšení i hlášení chyb jsou vítány.
Cílem je dlouhodobě udržitelný, otevřený a komunitní projekt.


---

❤️ Autoři

Termux-Updater Pro je společný projekt
Ravarentorena a ChatGPT (OpenAI)
s cílem vytvořit nejspolehlivější automatizovaný aktualizační systém pro Termux.
