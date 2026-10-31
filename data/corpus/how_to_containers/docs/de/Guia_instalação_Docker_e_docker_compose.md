# 🐳 Installationsmethoden für Docker und Docker Compose

Docker ist das wichtigste hier verwendete und dokumentierte Werkzeug zur Containerisierung. Das Docker-Compose-Plugin ist Ihr vollständigstes Mittel, um Inhalte zu versionieren und neu aufzubauen.

Damit soll die Praxis etabliert werden, Artefakte (Images, *Compose* usw.) zu versionieren und zu veröffentlichen, die mit verschiedenen **Orchestrierungen** von *Pipelines* kompatibel sind.

## 📑 **KURZNAVIGATION**

### 🖥️ **INSTALLATION NACH BETRIEBSSYSTEM**
- [🖥️ Windows](#windows)
- [🐧 Linux (Ubuntu/Debian)](#linux-ubuntudebian)
- [🐧 Linux (CentOS/RHEL/Fedora)](#linux-centosrhelfedora)

### ✅ **ÜBERPRÜFUNG UND KONFIGURATION**
- [✅ Installation überprüfen](#installation-überprüfen)
- [⚙️ Konfiguration nach der Installation](#konfiguration-nach-der-installation)

### 🛠️ **BEFEHLE UND WARTUNG**
- [🛠️ Nützliche Befehle](#nützliche-befehle)
- [🔧 Problembehebung](#problembehebung)

### 📊 **KURZREFERENZ**
- [📊 Kurzüberblick](#kurzüberblick)

---

## 📋 **DETAILLIERTES INHALTSVERZEICHNIS DER UNTERABSCHNITTE**

### 🖥️ **WINDOWS – DETAILS**
- [Methode 1: Docker Desktop (Empfohlen)](#methode-1-docker-desktop-empfohlen)
- [Methode 2: WSL2 + Docker (Fortgeschritten)](#methode-2-wsl2--docker-fortgeschritten)

### 🐧 **LINUX (UBUNTU/DEBIAN) – DETAILS**
- [Schnellinstallation](#schnellinstallation)
- [Für ARM64 (Raspberry Pi)](#für-arm64-raspberry-pi)

### 🐧 **LINUX (CENTOS/RHEL/FEDORA) – DETAILS**
- [CentOS/RHEL 8+](#centosrhel-8)
- [Fedora](#fedora)

### ✅ **ÜBERPRÜFUNG UND KONFIGURATION – DETAILS**
- [Basistest](#basistest)
- [Test mit eigenem Image](#test-mit-eigenem-image)
- [1. Ab- und Wiederanmeldung](#1-ab--und-wiederanmeldung)
- [2. Docker für automatischen Start konfigurieren](#2-docker-für-automatischen-start-konfigurieren)
- [3. Proxy konfigurieren (falls erforderlich)](#3-proxy-konfigurieren-falls-erforderlich)

### 🛠️ **BEFEHLE UND WARTUNG – DETAILS**
- [Container-Verwaltung](#container-verwaltung-1)
- [Volume-Verwaltung](#volume-verwaltung-1)
- [Vollständige Bereinigung](#vollständige-bereinigung)
- [Fehler: Zugriff verweigert](#fehler-zugriff-verweigert)
- [Fehler: Keine Verbindung zum Docker-Daemon](#fehler-keine-verbindung-zum-docker-daemon)
- [Fehler: Port bereits belegt](#fehler-port-bereits-belegt)

---

## ⚡ **SCHNELLBEFEHLE – REFERENZ**

### 🔧 **Überprüfung der Installation (Kurzreferenz)**
```bash
# Versionen prüfen
docker --version
docker compose version

# Basistest
docker run hello-world

# Systeminformationen
docker info
```

### 🐳 **Container-Verwaltung**
```bash
# Container auflisten
docker ps -a

# Alle Container stoppen
docker stop $(docker ps -q)

# Gestoppte Container entfernen
docker container prune

# Ungenutzte Images entfernen
docker image prune
```

### 📦 **Volume-Verwaltung**
```bash
# Volumes auflisten
docker volume ls

# Ungenutzte Volumes entfernen
docker volume prune
```

### 🧹 **Systembereinigung**
```bash
# Vollständige Bereinigung (Vorsicht!)
docker system prune -a --volumes

# Nur Images bereinigen
docker image prune

# Nur Container bereinigen
docker container prune
```

### 🔍 **Diagnose**
```bash
# Docker-Status
sudo systemctl status docker

# Docker starten
sudo systemctl start docker

# Belegte Ports prüfen
sudo netstat -tlnp | grep :8080
```

---

## 🆘 **Schnelle Problembehebung**

### ❌ **Häufige Probleme**
- **Zugriff verweigert** (`Permission denied`): Ihr Benutzer ist nicht in der Gruppe `docker`
- **Keine Verbindung zum Daemon** (`Cannot connect to daemon`): Docker läuft nicht
- **Port belegt** (`Port already in use`): Der Port wird bereits von einem anderen Prozess verwendet
- **WSL2 nicht gefunden** (`WSL2 not found`): WSL2 ist unter Windows nicht installiert

### 🔧 **Schnelle Lösungen**
```bash
# Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER
newgrp docker

# Docker starten
sudo systemctl start docker
sudo systemctl enable docker

# Status prüfen
sudo systemctl status docker
```

### 📞 **Kurze Hilfelinks**
- [🔧 Problembehebung](#problembehebung)
- [📊 Kurzüberblick](#kurzüberblick)

---

## 💻 **KURZE PRAKTISCH BEISPIELE**

### 🚀 **Skript zur automatischen Installation (Ubuntu/Debian)**
```bash
#!/bin/bash
# install-docker.sh – automatische Docker-Installation

echo "🐳 Installiere Docker und Docker Compose..."

# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Abhängigkeiten installieren
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker-Repository hinzufügen
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker installieren
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# Docker starten und aktivieren
sudo systemctl start docker
sudo systemctl enable docker

echo "✅ Installation abgeschlossen!"
echo "🔄 Melden Sie sich ab und wieder an, um Docker ohne sudo zu nutzen"
echo "🧪 Teste die Installation..."
docker run hello-world
```

### 🔍 **Diagnose-Skript**
```bash
#!/bin/bash
# docker-diagnose.sh – vollständige Docker-Diagnose

echo "🔍 Docker-Diagnose"
echo "======================="

# Versionen prüfen
echo "📋 Versionen:"
docker --version
docker compose version

echo ""
echo "🔧 Dienststatus:"
sudo systemctl status docker --no-pager

echo ""
echo "🐳 Laufende Container:"
docker ps

echo ""
echo "📦 Verfügbare Images:"
docker images

echo ""
echo "💾 Volumes:"
docker volume ls

echo ""
echo "🌐 Netzwerke:"
docker network ls

echo ""
echo "📊 Ressourcennutzung:"
docker system df

echo ""
echo "🧪 Konnektivitätstest:"
if docker run --rm hello-world > /dev/null 2>&1; then
    echo "✅ Docker funktioniert einwandfrei!"
else
    echo "❌ Problem mit der Docker-Installation"
fi
```

### 🧹 **Bereinigungs-Skript**
```bash
#!/bin/bash
# docker-cleanup.sh – Docker bereinigen

echo "🧹 Bereinige Docker..."

# Alle Container stoppen
echo "🛑 Stoppe Container..."
docker stop $(docker ps -q) 2>/dev/null || true

# Gestoppte Container entfernen
echo "🗑️ Entferne gestoppte Container..."
docker container prune -f

# Ungenutzte Images entfernen
echo "🖼️ Entferne ungenutzte Images..."
docker image prune -f

# Ungenutzte Volumes entfernen
echo "💾 Entferne ungenutzte Volumes..."
docker volume prune -f

# Ungenutzte Netzwerke entfernen
echo "🌐 Entferne ungenutzte Netzwerke..."
docker network prune -f

echo "✅ Bereinigung abgeschlossen!"
echo "📊 Freigegebener Speicher:"
docker system df
```

### 🎯 **Performance-Test-Skript**
```bash
#!/bin/bash
# docker-test.sh – Docker-Performance testen

echo "🎯 Teste Docker-Performance..."

# Pull-Test
echo "📥 Teste Image-Download..."
time docker pull alpine:latest

# Container-Erstellung
echo "🏗️ Teste Container-Erstellung..."
time docker run --rm alpine:latest echo "Container erfolgreich erstellt!"

# Build-Test (falls Dockerfile vorhanden)
if [ -f "Dockerfile" ]; then
    echo "🔨 Teste Image-Build..."
    time docker build -t test-image .
fi

# Netzwerktest
echo "🌐 Teste Netzwerkkonnektivität..."
docker run --rm alpine:latest ping -c 3 8.8.8.8

echo "✅ Tests abgeschlossen!"
```

---

## **Windows**
### **Methode 1: Docker Desktop (Empfohlen)**

1. **Docker Desktop herunterladen**
   - Besuchen Sie: https://www.docker.com/products/docker-desktop/
   - Starten Sie auf der Website den Download für Windows (die Schaltfläche heißt oft *Download for Windows*).
   - Version wählen: Windows 10/11 64-bit

2. **Installieren**
   ```bash
   # Heruntergeladene Datei ausführen (Docker Desktop Installer.exe)
   # Dem Installationsassistenten folgen
   # Computer bei Aufforderung neu starten
   ```

3. **Installation prüfen**
   ```bash
   # PowerShell als Administrator öffnen
   docker --version
   docker compose version
   ```

### **Methode 2: WSL2 + Docker (Fortgeschritten)**

1. **WSL2 installieren**
   ```powershell
   # PowerShell als Administrator
   wsl --install
   ```

2. **Docker in WSL2 installieren**
   ```bash
   # Innerhalb von WSL2
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

## **Linux (Ubuntu/Debian)**

### **Schnellinstallation**

```bash
# 1. System aktualisieren
sudo apt update && sudo apt upgrade -y

# 2. Abhängigkeiten installieren
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Docker-Repository hinzufügen
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Docker installieren
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# 6. Docker starten und aktivieren
sudo systemctl start docker
sudo systemctl enable docker

# 7. Installation prüfen
docker --version
docker compose version
```

### **Für ARM64 (Raspberry Pi)**

```bash
# 1. System aktualisieren
sudo apt update && sudo apt upgrade -y

# 2. Abhängigkeiten installieren
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Docker-Repository hinzufügen (ARM64)
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Docker installieren
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# 6. Docker starten und aktivieren
sudo systemctl start docker
sudo systemctl enable docker

# 7. Installation prüfen
docker --version
docker compose version
```

## **Linux (CentOS/RHEL/Fedora)**

### **CentOS/RHEL 8+**

```bash
# 1. Abhängigkeiten installieren
sudo dnf install -y dnf-utils

# 2. Docker-Repository hinzufügen
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. Docker installieren
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 4. Docker starten und aktivieren
sudo systemctl start docker
sudo systemctl enable docker

# 5. Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# 6. Installation prüfen
docker --version
docker compose version
```

### **Fedora**

```bash
# 1. Docker installieren
sudo dnf install -y docker docker-compose

# 2. Docker starten und aktivieren
sudo systemctl start docker
sudo systemctl enable docker

# 3. Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# 4. Installation prüfen
docker --version
docker compose version
```

## **Installation überprüfen**

### **Basistest**

```bash
# Versionen prüfen
docker --version
docker compose version

# Mit einfachem Container testen
docker run hello-world

# Prüfen, ob Docker läuft
docker info
```

### **Test mit eigenem Image**

```bash
# Test-Image herunterladen und ausführen
docker run -it --rm ubuntu:latest bash

# Innerhalb des Containers
echo "Docker funktioniert!"
exit
```

## **Konfiguration nach der Installation**

### **1. Ab- und Wiederanmeldung**
```bash
# Nach dem Hinzufügen des Benutzers zur Gruppe docker
# Ab- und Wiederanmeldung durchführen
# Oder ausführen:
newgrp docker
```

### **2. Docker für automatischen Start konfigurieren**

**Linux:**
```bash
# Bereits mit systemctl enable docker eingerichtet
sudo systemctl status docker
```

**Windows:**
- Docker Desktop startet automatisch mit Windows

### **3. Proxy konfigurieren (falls erforderlich)**

**Linux:**
```bash
# Konfigurationsverzeichnis anlegen
sudo mkdir -p /etc/systemd/system/docker.service.d

# Konfigurationsdatei anlegen
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=http://proxy:port"
Environment="HTTPS_PROXY=http://proxy:port"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# Konfiguration neu laden
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## **Nützliche Befehle**

### **Container-Verwaltung**
```bash
# Container auflisten
docker ps -a

# Alle Container stoppen
docker stop $(docker ps -q)

# Gestoppte Container entfernen
docker container prune

# Ungenutzte Images entfernen
docker image prune
```

### **Volume-Verwaltung**
```bash
# Volumes auflisten
docker volume ls

# Ungenutzte Volumes entfernen
docker volume prune
```

### **Vollständige Bereinigung**
```bash
# Alles entfernen (Vorsicht!)
docker system prune -a --volumes
```

## 🔧 **Problembehebung**

### **Fehler: Zugriff verweigert**

Typische Meldung: `Permission denied`.

```bash
# Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# Ab- und Wiederanmeldung durchführen
# Oder ausführen:
newgrp docker
```

### **Fehler: Keine Verbindung zum Docker-Daemon**

Typische Meldung: `Cannot connect to the Docker daemon`.

```bash
# Prüfen, ob Docker läuft
sudo systemctl status docker

# Docker bei Bedarf starten
sudo systemctl start docker
```

### **Fehler: Port bereits belegt**

Typische Meldung: `Port already in use`.

```bash
# Belegte Ports prüfen
sudo netstat -tlnp | grep :8080

# Prozess beenden, der den Port verwendet
sudo kill -9 <PID>
```

## 📊 **Kurzüberblick**

| System | Methode | Hauptbefehl |
|---------|--------|----------------|
| Windows | Docker Desktop | Von der offiziellen Website herunterladen |
| Ubuntu/Debian | Offizielles Repository | `sudo apt install docker-ce` |
| ARM64 | Offizielles Repository | `sudo apt install docker-ce` |
| CentOS/RHEL | Offizielles Repository | `sudo dnf install docker-ce` |
| Fedora | Standard-Repository | `sudo dnf install docker` |

**Nach der Installation führen Sie stets aus:**
```bash
docker --version
docker compose version
docker run hello-world
```

**Wenn alle Befehle funktionieren, war die Installation erfolgreich.**
