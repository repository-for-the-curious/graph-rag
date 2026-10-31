# 🐳 Docker and Docker Compose installation methods

Docker is the main containerization tool used and documented here. The Docker Compose plugin is the most complete tool for versioning and recreating your workloads.

With that in mind, the practice is to version and publish artifacts (images, *compose* files, etc.) compatible with various **orchestration** setups for pipelines.

## 📑 **Quick navigation index**

### 🖥️ **Installation by platform**
- [🖥️ Windows](#windows)
- [🐧 Linux (Ubuntu/Debian)](#linux-ubuntudebian)
- [🐧 Linux (CentOS/RHEL/Fedora)](#linux-centosrhelfedora)

### ✅ **Verification and configuration**
- [✅ Installation verification](#installation-verification)
- [⚙️ Post-installation configuration](#post-installation-configuration)

### 🛠️ **Commands and maintenance**
- [🛠️ Useful commands](#useful-commands)
- [🔧 Troubleshooting](#troubleshooting)

### 📊 **Quick reference**
- [📊 Quick summary](#quick-summary)

---

## 📋 **Detailed subsection index**

### 🖥️ **WINDOWS – Details**
- [Method 1: Docker Desktop (recommended)](#method-1-docker-desktop-recommended)
- [Method 2: WSL2 + Docker (advanced)](#method-2-wsl2-docker-advanced)

### 🐧 **LINUX (UBUNTU/DEBIAN) – Details**
- [Quick install](#quick-install)
- [For ARM64 (Raspberry Pi)](#for-arm64-raspberry-pi)

### 🐧 **LINUX (CENTOS/RHEL/FEDORA) – Details**
- [CentOS/RHEL 8+](#centosrhel-8)
- [Fedora](#fedora)

### ✅ **VERIFICATION AND CONFIGURATION – Details**
- [Basic test](#basic-test)
- [Test with a custom image](#test-with-a-custom-image)
- [1. Logout/Login](#1-logoutlogin)
- [2. Configure Docker to start automatically](#2-configure-docker-to-start-automatically)
- [3. Configure proxy (if needed)](#3-configure-proxy-if-needed)

### 🛠️ **COMMANDS AND MAINTENANCE – Details**
- [Container management](#container-management)
- [Volume management](#volume-management)
- [Full cleanup](#full-cleanup)
- [Error: permission denied](#error-permission-denied)
- [Error: cannot connect to the Docker daemon](#error-cannot-connect-to-the-docker-daemon)
- [Error: port already in use](#error-port-already-in-use)

---

## ⚡ **Quick commands – reference**

### 🔧 **Verify installation (quick)**
```bash
# Check versions
docker --version
docker compose version

# Basic test
docker run hello-world

# System information
docker info
```

### 🐳 **Container management — quick reference**
```bash
# List containers
docker ps -a

# Stop all containers
docker stop $(docker ps -q)

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune
```

### 📦 **Volume management — quick reference**
```bash
# List volumes
docker volume ls

# Remove unused volumes
docker volume prune
```

### 🧹 **System cleanup**
```bash
# Full cleanup (careful!)
docker system prune -a --volumes

# Images only
docker image prune

# Containers only
docker container prune
```

### 🔍 **Diagnostics**
```bash
# Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Check ports in use
sudo netstat -tlnp | grep :8080
```

---

## 🆘 **Quick troubleshooting**

### ❌ **Common issues**
- **Permission denied** (`Permission denied`): user is not in the `docker` group
- **Cannot connect to daemon** (`Cannot connect to daemon`): Docker is not running
- **Port in use** (`Port already in use`): the port is already used by another process
- **WSL2 not found** (`WSL2 not found`): WSL2 is not installed on Windows

### 🔧 **Quick fixes**
```bash
# Add user to the docker group
sudo usermod -aG docker $USER
newgrp docker

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### 📞 **Quick help links**
- [🔧 Troubleshooting](#troubleshooting)
- [📊 Quick summary](#quick-summary)

---

## 💻 **Quick practical examples**

### 🚀 **Automated install script (Ubuntu/Debian)**
```bash
#!/bin/bash
# install-docker.sh - Automated Docker installation

echo "🐳 Installing Docker and Docker Compose..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to the docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

echo "✅ Installation complete!"
echo "🔄 Log out and log in again to use Docker without sudo"
echo "🧪 Testing installation..."
docker run hello-world
```

### 🔍 **Diagnostic script**
```bash
#!/bin/bash
# docker-diagnose.sh - Full Docker diagnostics

echo "🔍 Docker diagnostics"
echo "======================="

# Check versions
echo "📋 Versions:"
docker --version
docker compose version

echo ""
echo "🔧 Service status:"
sudo systemctl status docker --no-pager

echo ""
echo "🐳 Running containers:"
docker ps

echo ""
echo "📦 Available images:"
docker images

echo ""
echo "💾 Volumes:"
docker volume ls

echo ""
echo "🌐 Networks:"
docker network ls

echo ""
echo "📊 Resource usage:"
docker system df

echo ""
echo "🧪 Connectivity test:"
if docker run --rm hello-world > /dev/null 2>&1; then
    echo "✅ Docker is working correctly!"
else
    echo "❌ Problem with the Docker installation"
fi
```

### 🧹 **Cleanup script**
```bash
#!/bin/bash
# docker-cleanup.sh - Docker cleanup

echo "🧹 Cleaning up Docker..."

# Stop all containers
echo "🛑 Stopping containers..."
docker stop $(docker ps -q) 2>/dev/null || true

# Remove stopped containers
echo "🗑️ Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "🖼️ Removing unused images..."
docker image prune -f

# Remove unused volumes
echo "💾 Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "🌐 Removing unused networks..."
docker network prune -f

echo "✅ Cleanup complete!"
echo "📊 Space freed:"
docker system df
```

### 🎯 **Performance test script**
```bash
#!/bin/bash
# docker-test.sh - Docker performance test

echo "🎯 Testing Docker performance..."

# Pull test
echo "📥 Testing image download..."
time docker pull alpine:latest

# Container creation test
echo "🏗️ Testing container creation..."
time docker run --rm alpine:latest echo "Container created successfully!"

# Build test (if Dockerfile exists)
if [ -f "Dockerfile" ]; then
    echo "🔨 Testing image build..."
    time docker build -t test-image .
fi

# Network test
echo "🌐 Testing network connectivity..."
docker run --rm alpine:latest ping -c 3 8.8.8.8

echo "✅ Tests complete!"
```

---

## **Windows**
### **Method 1: Docker Desktop (recommended)**

1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop/
   - On the site, start the download for Windows (the button is usually labeled *Download for Windows*).
   - Choose version: Windows 10/11 64-bit

2. **Install**
   ```bash
   # Run the downloaded file (Docker Desktop Installer.exe)
   # Follow the installation wizard
   # Restart the computer when prompted
   ```

3. **Verify installation**
   ```bash
   # Open PowerShell as administrator
   docker --version
   docker compose version
   ```

### **Method 2: WSL2 + Docker (advanced)**

1. **Install WSL2**
   ```powershell
   # In PowerShell as administrator
   wsl --install
   ```

2. **Install Docker in WSL2**
   ```bash
   # Inside WSL2
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

## **Linux (Ubuntu/Debian)**

### **Quick install**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Add user to the docker group
sudo usermod -aG docker $USER

# 6. Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# 7. Verify installation
docker --version
docker compose version
```

### **For ARM64 (Raspberry Pi)**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Add Docker repository (ARM64)
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Add user to the docker group
sudo usermod -aG docker $USER

# 6. Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# 7. Verify installation
docker --version
docker compose version
```

## **Linux (CentOS/RHEL/Fedora)**

### **CentOS/RHEL 8+**

```bash
# 1. Install dependencies
sudo dnf install -y dnf-utils

# 2. Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. Install Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 4. Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# 5. Add user to the docker group
sudo usermod -aG docker $USER

# 6. Verify installation
docker --version
docker compose version
```

### **Fedora**

```bash
# 1. Install Docker
sudo dnf install -y docker docker-compose

# 2. Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# 3. Add user to the docker group
sudo usermod -aG docker $USER

# 4. Verify installation
docker --version
docker compose version
```

## **Installation verification**

### **Basic test**

```bash
# Check versions
docker --version
docker compose version

# Test with a simple container
docker run hello-world

# Check whether Docker is running
docker info
```

### **Test with a custom image**

```bash
# Pull and run a test image
docker run -it --rm ubuntu:latest bash

# Inside the container
echo "Docker is working!"
exit
```

## **Post-installation configuration**

### **1. Logout/Login**
```bash
# After adding the user to the docker group
# Log out and log in again
# Or run:
newgrp docker
```

### **2. Configure Docker to start automatically**

**Linux:**
```bash
# Already configured with systemctl enable docker
sudo systemctl status docker
```

**Windows:**
- Docker Desktop starts automatically with Windows

### **3. Configure proxy (if needed)**

**Linux:**
```bash
# Create configuration directory
sudo mkdir -p /etc/systemd/system/docker.service.d

# Create configuration file
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=http://proxy:port"
Environment="HTTPS_PROXY=http://proxy:port"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# Reload configuration
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## **Useful commands**

### **Container management**
```bash
# List containers
docker ps -a

# Stop all containers
docker stop $(docker ps -q)

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune
```

### **Volume management**
```bash
# List volumes
docker volume ls

# Remove unused volumes
docker volume prune
```

### **Full cleanup**
```bash
# Remove everything (careful!)
docker system prune -a --volumes
```

## 🔧 **Troubleshooting**

### **Error: permission denied**

Typical message: `Permission denied`.

```bash
# Add user to the docker group
sudo usermod -aG docker $USER

# Log out and log in again
# Or run:
newgrp docker
```

### **Error: cannot connect to the Docker daemon**

Typical message: `Cannot connect to the Docker daemon`.

```bash
# Check whether Docker is running
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker
```

### **Error: port already in use**

Typical message: `Port already in use`.

```bash
# Check ports in use
sudo netstat -tlnp | grep :8080

# Stop the process using the port
sudo kill -9 <PID>
```

## 📊 **Quick summary**

| System | Method | Main step |
|--------|--------|-----------|
| Windows | Docker Desktop | Download from the official site |
| Ubuntu/Debian | Official repository | `sudo apt install docker-ce` |
| ARM64 | Official repository | `sudo apt install docker-ce` |
| CentOS/RHEL | Official repository | `sudo dnf install docker-ce` |
| Fedora | Default repository | `sudo dnf install docker` |

**After installation, always run:**
```bash
docker --version
docker compose version
docker run hello-world
```

**If all commands succeed, the installation was successful!**
