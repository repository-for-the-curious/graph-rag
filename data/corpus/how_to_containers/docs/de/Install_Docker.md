# Docker und Docker Compose installieren

Docker ist das wichtigste hier verwendete und dokumentierte Containerisierungswerkzeug. Das Docker-Compose-Plugin ist das vollständigste Mittel, Umgebungen zu versionieren und neu aufzubauen.

Ziel ist es, Artefakte (Images, *Compose*-Dateien usw.) zu versionieren und zu veröffentlichen, die mit verschiedenen **Orchestrierungen** von *Pipelines* kompatibel sind.

# Installationsmethoden

## **Windows**

### **Methode 1: Docker Desktop (empfohlen)**

1. **Docker Desktop herunterladen**
   - Website: https://www.docker.com/products/docker-desktop/
   - Auf der Seite den Download für Windows startieren (Schaltfläche oft *Download for Windows*).
   - Version wählen: Windows 10/11 64-bit

2. **Installieren**
   ```bash
   # Heruntergeladene Datei ausführen (Docker Desktop Installer.exe)
   # Installationsassistenten folgen
   # Computer bei Aufforderung neu starten
   ```

3. **Installation prüfen**
   ```bash
   # PowerShell als Administrator öffnen
   docker --version
   docker compose version
   ```

### **Methode 2: WSL2 + Docker (fortgeschritten)**

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

# 3. Docker-Repository (ARM64)
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

## **Installation prüfen**

### **Basistest**

```bash
# Versionen prüfen
docker --version
docker compose version

# Einfacher Container-Test
docker run hello-world

# Prüfen, ob Docker läuft
docker info
```

### **Test mit eigenem Image**

```bash
# Test-Image ausführen
docker run -it --rm ubuntu:latest bash

# Im Container
echo "Docker funktioniert!"
exit
```

## **Konfiguration nach der Installation**

### **1. Ab- und Anmeldung**

```bash
# Nach Hinzufügen des Benutzers zur Gruppe docker
# Ab- und wieder anmelden
# Oder ausführen:
newgrp docker
```

### **2. Docker automatisch starten**

**Linux:**
```bash
# Bereits mit systemctl enable docker eingerichtet
sudo systemctl status docker
```

**Windows:**
- Docker Desktop startet automatisch mit Windows

### **3. Proxy konfigurieren (falls nötig)**

**Linux:**
```bash
# Konfigurationsverzeichnis anlegen
sudo mkdir -p /etc/systemd/system/docker.service.d

# Konfigurationsdatei erstellen
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

## 🔧 **Fehlerbehebung**

### **Fehler: Zugriff verweigert**

Typische Meldung: `Permission denied`.

```bash
# Benutzer zur Gruppe docker hinzufügen
sudo usermod -aG docker $USER

# Ab- und wieder anmelden
# Oder ausführen:
newgrp docker
```

### **Fehler: Keine Verbindung zum Docker-Daemon**

Typische Meldung: `Cannot connect to the Docker daemon`.

```bash
# Prüfen, ob Docker läuft
sudo systemctl status docker

# Docker ggf. starten
sudo systemctl start docker
```

### **Fehler: Port bereits belegt**

Typische Meldung: `Port already in use`.

```bash
# Belegte Ports prüfen
sudo netstat -tlnp | grep :8080

# Prozess beenden, der den Port nutzt
sudo kill -9 <PID>
```

## 📊 **Kurzüberblick**

| System | Methode | Hauptbefehl |
|--------|---------|-------------|
| Windows | Docker Desktop | Von offizieller Website laden |
| Ubuntu/Debian | Offizielles Repository | `sudo apt install docker-ce` |
| ARM64 | Offizielles Repository | `sudo apt install docker-ce` |
| CentOS/RHEL | Offizielles Repository | `sudo dnf install docker-ce` |
| Fedora | Standard-Repository | `sudo dnf install docker` |

**Nach der Installation immer ausführen:**
```bash
docker --version
docker compose version
docker run hello-world
```

**Wenn alle Befehle funktionieren, war die Installation erfolgreich.**
