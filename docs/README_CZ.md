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

### Termux-Updater

📘 Termux-Updater Pro — Dokumentace (CZ)

🧩 Přehled

Termux-Updater Pro je pokročilý, plně automatizovaný aktualizační a údržbový systém
pro prostředí Termux.

Aktualizuje zároveň:

balíčky pkg

system pip

libovolný počet virtuálních prostředí (venv)


Automaticky řeší konflikty, generuje strukturované JSON reporty
a zajišťuje dlouhodobou stabilitu i u náročných projektů.


---

🚀 Klíčové funkce

Automatická aktualizace:

Termux pkg balíčků

Termux system pip balíčků

všech pip balíčků uvnitř libovolného počtu venv


Plně oddělené aktualizační pipelines

Inteligentní detekce chyb a konfliktů

Lock-file ochrana proti více současným spuštěním

Export JSON:

Aktualizator_seznam.json — čistý inventář aktualizací

Aktualizator_issue.json — chyby, varování, konflikty


Každodenní plně autonomní provoz

Navrženo pro dlouhodobě běžící projekty a spolehlivost

---

⭐ Instalace

1. Naklonování repozitáře

git clone https://github.com/Ravarentoren/Termux-Updater.git
cd Termux-Updater

2. Nastavení práv

chmod +x aktualizator/Termux-Updater-Pro.py

3. Vytvoření globálního příkazu aktualizator

ln -sf $(pwd)/aktualizator/Termux-Updater-Pro.py ~/bin/aktualizator

Nyní můžeš spustit updater odkudkoliv v Termux jednoduše:

aktualizator


---

🛠 Použití

Základní spuštění

aktualizator

Spuštění s argumenty

aktualizator --mode C --verbose --venv-dir ~/venv

Testovací režim (bez provedení změn)

aktualizator --dry-run --verbose


---

🧠 Přehled aktualizačních módů

Mód	Popis

A	pouze Termux pkg
B	pkg + system pip
C	pkg + system pip + všechny venv
D	plně autonomní režim (doporučeno pro denní používání)



---

📄 JSON výstupní soubory

Soubor	Popis

Aktualizator_seznam.json	Čistý seznam aktualizovaných položek
Aktualizator_issue.json	Chyby, varování, konflikty, logy


Oba soubory jsou vždy zapisovány sem:

~/storage/downloads/


---

📘 Dokumentace

🇨🇿 Tento dokument: docs/README_CZ.md

🇬🇧 English version: docs/README_EN.md



---

📝 Licence

Tento projekt je duálně licencován pod:

MIT License

Apache License 2.0


Uživatelé si mohou svobodně zvolit, kterou licenci chtějí použít.

Tato kombinace zajišťuje:

maximální svobodu pro použití, úpravy a integraci

použití v komerčních i nekomerčních projektech

kompatibilitu s většinou OS a vývojářských ekosystémů

žádnou povinnost vracet změny zpět (na rozdíl od GPL)



---

🤝 Přispívání

Příspěvky, nápady, vylepšení, testování i hlášení chyb jsou vítány.

Projekt je navržen tak, aby byl:

snadno pochopitelný i pro nové spolupracovníky

rozšiřitelný

stabilní a udržitelný pro mnoho let dopředu



---

❤️ Autoři

Termux-Updater Pro je společná práce:

Ravarentoren and ChatGPT (OpenAI)

Cílem je vytvořit nejspolehlivější automatizační a aktualizační systém pro Termux.


---
