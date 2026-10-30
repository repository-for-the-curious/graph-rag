# 🐧 Leitfaden: WSL + Ubuntu für Repositories

Dasselbe Repository wird oft gleichzeitig in Git-Umgebungen für **Linux** und **Windows** genutzt.

Nachfolgend erfahren Sie, wie Sie das einrichten und damit zusammenhängende Fehler vermeiden.

## 📑 **SCHNELLNAVIGATION**

### 🚀 **INSTALLATION UND KONFIGURATION**
- [🎯 Ziel](#-ziel)
- [📋 Voraussetzungen](#-voraussetzungen)
- [🚀 Installation von WSL2 + Ubuntu](#-installation-von-wsl2--ubuntu)
- [🔧 Konfiguration für Repositories](#-konfiguration-für-repositories)

### ⚠️ **FEHLERBEHEBUNG**
- [⚠️ Fehlerbehebung: häufige Fehler](#-fehlerbehebung-häufige-fehler)

### 📁 **ORGANISATION UND ARBEITSABLAUF**
- [📁 Empfohlene Struktur](#-empfohlene-struktur)
- [🔄 Empfohlener Arbeitsablauf](#-empfohlener-arbeitsablauf)

### 💡 **RESSOURCEN UND TIPPS**
- [📋 Nützliche Befehle](#-nützliche-befehle)
- [✅ Abschließende Prüfung](#-abschließende-prüfung)
- [💡 Wichtige Hinweise](#-wichtige-hinweise)

---

## 📋 **DETAILLIERTES INHALTSVERZEICHNIS DER UNTERABSCHNITTE**

### 🚀 **INSTALLATION UND KONFIGURATION – Details**
- [1. WSL aktivieren (PowerShell als Administrator)](#1-wsl-aktivieren-powershell-als-administrator)
- [2. WSL2 und Ubuntu installieren](#2-wsl2-und-ubuntu-installieren)
- [3. Ubuntu konfigurieren (erster Start)](#3-ubuntu-konfigurieren-erster-start)
- [Git-Konfiguration](#git-konfiguration)
- [Docker einrichten (falls erforderlich)](#docker-einrichten-falls-erforderlich)

### ⚠️ **FEHLERBEHEBUNG – Details**
- [🚨 Fehler: `/usr/bin/env: 'bash\r': No such file or directory`](#-fehler-usrbinenv-bashr-no-such-file-or-directory)
- [🚨 Fehler: Zugriff verweigert](#-fehler-zugriff-verweigert)
- [🚨 Fehler: Docker funktioniert nicht](#-fehler-docker-funktioniert-nicht)
- [🚨 Fehler: Windows-Befehle unter Linux](#-fehler-windows-befehle-unter-linux)

### 📁 **ORGANISATION UND ARBEITSABLAUF – Details**
- [Projektorganisation](#projektorganisation)
- [Für neue Repositories](#für-neue-repositories)
- [Für bestehende Repositories (mit Problemen)](#für-bestehende-repositories-mit-problemen)

---

## ⚡ **KURZBEFEHLE – REFERENZ**

### 🔧 **Erstkonfiguration von Git**
```bash
# OBLIGATORISCHE Konfiguration vor dem Klonen
git config --global user.name "Ihr Name"
git config --global user.email "ihre@email.com"
git config --global core.autocrlf false
git config --global core.eol lf
git config --global init.defaultBranch main
git config --global pull.rebase false
```

### 🐧 **Installation WSL2 + Ubuntu**
```powershell
# In PowerShell als Administrator
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2
wsl --install -d Ubuntu
```

### 🔧 **Ubuntu konfigurieren**
```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Wesentliche Werkzeuge installieren
sudo apt install -y git curl wget build-essential dos2unix

# Docker einrichten (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 🛠️ **Problembehebung**
```bash
# Zeilenenden korrigieren
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;

# Ausführungsrechte setzen
find . -name "*.sh" -exec chmod +x {} \;

# Zeilenenden prüfen
file datei.sh
hexdump -C datei.sh | head
```

### 📁 **Projektstruktur**
```bash
# Empfohlene Struktur anlegen
cd ~
mkdir projekte
cd projekte

# Repositories klonen
git clone https://github.com/benutzer/repo.git
cd repo
chmod +x *.sh
./build.sh
```

---

## 🆘 **Schnelle Fehlerbehebung**

### ❌ **Häufige Probleme**
- **`/usr/bin/env: 'bash\r': No such file or directory`**: Zeilenenden CRLF statt LF
- **Zugriff verweigert** (`Permission denied`): Dateien ohne Ausführungsrecht
- **Docker funktioniert nicht**: Docker Desktop läuft nicht oder WSL2-Integration ist deaktiviert
- **Windows-Befehle unter Linux**: Windows-Befehle im WSL verwenden

### 🔧 **Schnelle Lösungen**
```bash
# Zeilenenden korrigieren
dos2unix datei.sh
find . -name "*.sh" -exec dos2unix {} \;

# Rechte setzen
chmod +x datei.sh
find . -name "*.sh" -exec chmod +x {} \;

# WSL neu starten
exit
# In PowerShell: wsl --shutdown
```

### 📞 **Schnellhilfe-Links**
- [⚠️ Fehlerbehebung: häufige Fehler](#-fehlerbehebung-häufige-fehler)
- [💡 Wichtige Hinweise](#-wichtige-hinweise)

---

## 💻 **KURZE PRAKTISCHE BEISPIELE**

### 🚀 **Skript für die vollständige Einrichtung**
```bash
#!/bin/bash
# setup-wsl-git.sh - Vollständige Einrichtung von WSL + Git

echo "🐧 Richte WSL + Ubuntu für Git-Repositories ein..."

# System aktualisieren
echo "📦 Aktualisiere das System..."
sudo apt update && sudo apt upgrade -y

# Wesentliche Werkzeuge installieren
echo "🔧 Installiere Werkzeuge..."
sudo apt install -y git curl wget build-essential dos2unix

# Git konfigurieren
echo "⚙️ Konfiguriere Git..."
read -p "Geben Sie Ihren Namen ein: " name
read -p "Geben Sie Ihre E-Mail-Adresse ein: " email

git config --global user.name "$name"
git config --global user.email "$email"
git config --global core.autocrlf false
git config --global core.eol lf
git config --global init.defaultBranch main
git config --global pull.rebase false

# Projektstruktur anlegen
echo "📁 Lege Projektstruktur an..."
mkdir -p ~/projekte
cd ~/projekte

echo "✅ Einrichtung abgeschlossen!"
echo "📋 Git-Einstellungen:"
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"

echo ""
echo "🎯 Nächste Schritte:"
echo "1. cd ~/projekte"
echo "2. git clone https://github.com/benutzer/repo.git"
echo "3. cd repo && chmod +x *.sh && ./build.sh"
```

### 🔍 **Diagnose-Skript**
```bash
#!/bin/bash
# wsl-git-diagnose.sh - Diagnose für WSL + Git

echo "🔍 Diagnose WSL + Git"
echo "======================="

# WSL prüfen
echo "🐧 WSL:"
wsl --list --verbose

echo ""
echo "📋 Git:"
git --version
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"

echo ""
echo "🔧 Werkzeuge:"
which dos2unix
which curl
which wget

echo ""
echo "📁 Struktur:"
ls -la ~/projekte 2>/dev/null || echo "Verzeichnis ~/projekte existiert nicht"

echo ""
echo "🧪 Test der Zeilenenden:"
if [ -f "test.sh" ]; then
    file test.sh
    hexdump -C test.sh | head -1
else
    echo "Lege Testdatei an..."
    echo '#!/bin/bash' > test.sh
    echo 'echo "Hello World"' >> test.sh
    file test.sh
    hexdump -C test.sh | head -1
    rm test.sh
fi

echo ""
echo "✅ Diagnose abgeschlossen!"
```

### 🧹 **Bereinigungs- und Korrekturskript**
```bash
#!/bin/bash
# fix-repo.sh - Repository mit Problemen korrigieren

echo "🧹 Korrigiere Repository..."

# Prüfen, ob wir in einem Git-Repository sind
if [ ! -d ".git" ]; then
    echo "❌ Kein Git-Repository!"
    exit 1
fi

# Zeilenenden korrigieren
echo "🔧 Korrigiere Zeilenenden..."
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;
find . -name "*.js" -exec dos2unix {} \;

# Ausführungsrechte setzen
echo "🔐 Passe Berechtigungen an..."
find . -name "*.sh" -exec chmod +x {} \;

# Dateien prüfen
echo "📋 Prüfe Dateien..."
echo "Gefundene Skripte:"
find . -name "*.sh" -type f

echo ""
echo "Prüfe Zeilenenden:"
for file in $(find . -name "*.sh" -type f); do
    echo -n "$file: "
    file "$file" | grep -q "CRLF" && echo "❌ CRLF" || echo "✅ LF"
done

echo ""
echo "✅ Korrektur abgeschlossen!"
echo "🧪 Teste Skripte..."
for script in $(find . -name "*.sh" -type f); do
    echo "Teste: $script"
    if bash -n "$script"; then
        echo "✅ $script: Syntax OK"
    else
        echo "❌ $script: Syntaxfehler"
    fi
done
```

### 🎯 **Skript zum Testen eines Repositories**
```bash
#!/bin/bash
# test-repo.sh - Vollständigen Repository-Test ausführen

echo "🎯 Teste Repository..."

# Prüfen, ob es ein Git-Repository ist
if [ ! -d ".git" ]; then
    echo "❌ Kein Git-Repository!"
    exit 1
fi

# Git-Konfiguration prüfen
echo "📋 Git-Konfiguration:"
git config --global core.autocrlf
git config --global core.eol

# Skripte prüfen
echo ""
echo "🔧 Gefundene Skripte:"
find . -name "*.sh" -type f

# Jedes Skript testen
echo ""
echo "🧪 Teste Skripte:"
for script in $(find . -name "*.sh" -type f); do
    echo -n "Teste $script: "
    if bash -n "$script" 2>/dev/null; then
        echo "✅ OK"
    else
        echo "❌ FEHLER"
    fi
done

# Zeilenenden prüfen
echo ""
echo "📄 Prüfe Zeilenenden:"
for file in $(find . -name "*.sh" -o -name "*.py" -o -name "*.js" | head -5); do
    echo -n "$file: "
    if file "$file" | grep -q "CRLF"; then
        echo "❌ CRLF (problematisch)"
    else
        echo "✅ LF (korrekt)"
    fi
done

echo ""
echo "✅ Test abgeschlossen!"
```

---

## 🎯 **Ziel**
WSL2 + Ubuntu so einrichten, dass Sie mit Git-Repositories ohne Windows/Linux-Kompatibilitätsprobleme arbeiten können.

---

## 📋 **Voraussetzungen**
- Windows 10 Version 2004 oder höher bzw. Windows 11
- Administratorrechte
- Internetverbindung

---

## 🚀 **Installation von WSL2 + Ubuntu**

### **1. WSL aktivieren (PowerShell als Administrator):**
```powershell
# WSL aktivieren
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Virtual Machine Platform aktivieren
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Computer neu starten
shutdown /r /t 0
```

### **2. WSL2 und Ubuntu installieren:**
```powershell
# WSL2 als Standard festlegen
wsl --set-default-version 2

# Ubuntu installieren
wsl --install -d Ubuntu

# Installation prüfen
wsl --list --verbose
```

### **3. Ubuntu konfigurieren (erster Start):**
```bash
# Sie werden aufgefordert, Benutzer und Passwort anzulegen
# Beispiel: Benutzer „murilo“, Passwort nach Ihrer Wahl

# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Wesentliche Werkzeuge installieren
sudo apt install -y git curl wget build-essential
```

---

## 🔧 **Konfiguration für Repositories**

### **Git-Konfiguration:**
Klonen Sie erst, nachdem Sie Git konfiguriert haben.
Die folgenden Befehle stellen sicher, dass:
1. ✅ Dateien Unix-konforme Zeilenenden (LF) behalten
2. ✅ Skripte sowohl unter Windows als auch unter WSL funktionieren
3. ✅ keine problematische automatische Konvertierung erfolgt
4. ✅ das Repository plattformübergreifend konsistent bleibt


```bash
# === OBLIGATORISCHE KONFIGURATION (VOR JEDEM KLON) ===
git config --global user.name "Ihr Name"
git config --global user.email "ihre@email.com"

# KRITISCH: Zeilenenden
git config --global core.autocrlf false
git config --global core.eol lf

# Empfohlene Zusatzeinstellungen
git config --global init.defaultBranch main
git config --global pull.rebase false

# Alles prüfen
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"
```

```bash
# Jetzt können Sie jedes Repository klonen
git clone https://github.com/user/container_monitoramento.git
cd container_monitoramento

# Skripte funktionieren korrekt
chmod +x *.sh
./build.sh  # ✅ Erfolg!
```

```bash
# falls Sie vor der Konfiguration geklont haben
# 1. Git korrekt konfigurieren
git config --global core.autocrlf false
git config --global core.eol lf

# 2. beschädigtes Verzeichnis entfernen
cd ..
rm -rf altes_projekt

# 3. erneut klonen
git clone https://github.com/user/projekt.git
cd projekt

# ✅ Dateien haben nun korrektes LF
```
### **Docker einrichten (falls erforderlich):**
```bash
# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# WSL neu starten
exit
# In PowerShell: wsl --shutdown
# Ubuntu erneut öffnen
```

---

## ⚠️ **Fehlerbehebung: häufige Fehler**

### **🚨 Fehler: `/usr/bin/env: 'bash\r': No such file or directory`**

**Ursache:** Unter Windows geklonte Dateien haben Zeilenenden in CRLF (`\r\n`) statt LF (`\n`).

#### **💡 Lösungen:**

#### **Option 1: Vorhandene Dateien konvertieren**
```bash
# Eine bestimmte Datei
dos2unix build.sh

# Alle .sh-Dateien im Verzeichnis
find . -name "*.sh" -exec dos2unix {} \;

# dos2unix installieren, falls nicht vorhanden
sudo apt install dos2unix
```

#### **Option 2: Mit sed (Alternative)**
```bash
# Eine Datei konvertieren
sed -i 's/\r$//' build.sh

# Alle .sh-Dateien
find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
```

#### **Option 3: Git neu konfigurieren und erneut klonen**
```bash
# Git neu konfigurieren
git config --global core.autocrlf false
git config --global core.eol lf

# Repository erneut klonen
cd /tmp
git clone https://github.com/benutzer/repo.git repo_sauber
cd repo_sauber

# Zeilenenden prüfen
file build.sh
# Sollte anzeigen: „Bourne-Again shell script, ASCII text executable“
# Sollte NICHT anzeigen: „with CRLF line terminators“
```

---

### **🚨 Fehler: Zugriff verweigert**

**Typische Meldung:** `Permission denied` (Datei ohne Ausführungsrecht).

```bash
# Problem: Datei ohne Ausführungsrecht
chmod +x build.sh
chmod +x *.sh

# Für mehrere Dateien
find . -name "*.sh" -exec chmod +x {} \;
```

---

### **🚨 Fehler: Docker funktioniert nicht**
```bash
# Prüfen, ob Docker Desktop unter Windows läuft
# WSL2-Integration in Docker Desktop prüfen

# Docker testen
docker --version
docker run hello-world

# Bei Fehler WSL neu starten
# In Windows-PowerShell:
wsl --shutdown
# Ubuntu erneut öffnen
```

---

### **🚨 Fehler: Windows-Befehle unter Linux**
```bash
# Problem: Windows-Befehle im WSL verwenden
# ❌ FALSCH:
dir
cls

# ✅ RICHTIG:
ls
clear
```

---

## 📁 **Empfohlene Struktur**

### **Projektorganisation:**
```bash
# Im Linux-Dateisystem arbeiten, NICHT unter /mnt/c/
cd ~
mkdir projekte
cd projekte

# Repositories hier klonen
git clone https://github.com/benutzer/repo.git

# ❌ Vermeiden Sie die Arbeit unter:
# /mnt/c/Users/benutzer/Desktop/
# (schlechte Performance + Probleme mit Zeilenenden)

# ✅ VERWENDEN SIE:
# ~/projekte/ oder /home/benutzer/projekte/
```

---

## 🔄 **Empfohlener Arbeitsablauf**

### **Für neue Repositories:**
```bash
# 1. Git korrekt konfigurieren
git config --global core.autocrlf false
git config --global core.eol lf

# 2. Direkt im WSL klonen
cd ~/projekte
git clone https://github.com/repo.git

# 3. Entwicklung im WSL
cd repo
chmod +x *.sh
./build.sh
```

### **Für bestehende Repositories (mit Problemen):**
```bash
# 1. Zeilenenden bereinigen
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;

# 2. Rechte setzen
find . -name "*.sh" -exec chmod +x {} \;

# 3. Testen
./build.sh
```

---

## 📋 **Nützliche Befehle**

```bash
# Zeilenenden prüfen
file datei.sh
hexdump -C datei.sh | head

# Alle Textdateien konvertieren
find . -type f -exec dos2unix {} \;

# Alle ausführbaren Dateien anzeigen
find . -type f -executable

# Windows-Dateien vom WSL aus
cd /mnt/c/Users/$USER/Desktop

# WSL-Dateien von Windows aus
# Im Explorer: \\wsl$\Ubuntu\home\benutzer
```

---

## ✅ **Abschließende Prüfung**

```bash
# Vollständiger Test
cd ~/projekte
git clone https://github.com/ihr-repo/container_monitoramento.git
cd container_monitoramento
chmod +x *.sh
ls -la *.sh
file *.sh
./build.sh
```

**Wenn alles ohne Fehler läuft, ist die Konfiguration korrekt! 🎉**

---

## 💡 **Wichtige Hinweise**

- ✅ **Arbeiten Sie stets in `~/projekte/`**, nicht unter `/mnt/c/`
- ✅ **Konfigurieren Sie Git**, bevor Sie Repositories klonen
- ✅ **Verwenden Sie `dos2unix`**, um problematische Dateien zu korrigieren
- ✅ **Halten Sie Docker Desktop** aktuell
- ❌ **Vermeiden Sie**, unter Windows zu bearbeiten und im WSL auszuführen

---

**🐧 Jetzt können Sie beruhigt unter Ubuntu/WSL entwickeln! 🚀**

Dieser Leitfaden behandelt das Thema Zeilenenden (CRLF vs. LF) und bietet praktische Lösungen für die Arbeit mit Repositories zwischen Windows und WSL/Ubuntu. 🎯
