# Install Docker and Docker Compose

Docker is the main containerization tool used and documented here. The Docker Compose plugin is the most complete way to version and recreate your environments.

The goal is to adopt the practice of versioning and publishing artifacts (images, *compose* files, etc.) compatible with various **orchestrations** of *pipelines*.

# Installation methods

## **Windows**

### **Method 1: Docker Desktop (recommended)**

1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop/
   - On the site, start the download for Windows (the button is often labeled *Download for Windows*).
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

# 5. Add user to docker group
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

# 5. Add user to docker group
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

# 5. Add user to docker group
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

# 3. Add user to docker group
sudo usermod -aG docker $USER

# 4. Verify installation
docker --version
docker compose version
```

## **Verify installation**

### **Basic test**

```bash
# Check versions
docker --version
docker compose version

# Simple container test
docker run hello-world

# Check Docker is running
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

## **Post-install configuration**

### **1. Log out / log in**

```bash
# After adding the user to the docker group
# Log out and log in again
# Or run:
newgrp docker
```

### **2. Start Docker automatically**

**Linux:**
```bash
# Already configured with systemctl enable docker
sudo systemctl status docker
```

**Windows:**
- Docker Desktop starts automatically with Windows

### **3. Configure a proxy (if needed)**

**Linux:**
```bash
# Create config directory
sudo mkdir -p /etc/systemd/system/docker.service.d

# Create config file
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
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log in again
# Or run:
newgrp docker
```

### **Error: cannot connect to Docker daemon**

Typical message: `Cannot connect to the Docker daemon`.

```bash
# Check if Docker is running
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

| System | Method | Main command |
|--------|--------|--------------|
| Windows | Docker Desktop | Download from official site |
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

**If all commands succeed, installation was successful.**
