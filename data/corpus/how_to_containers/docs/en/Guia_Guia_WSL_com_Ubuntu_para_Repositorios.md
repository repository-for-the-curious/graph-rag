# 🐧 Guide: WSL + Ubuntu for repositories

Often the same repository will be used on **Linux** and **Windows** Git setups at the same time.

Review below how to get this right and avoid related errors.

## 📑 **QUICK NAVIGATION INDEX**

### 🚀 **INSTALLATION AND CONFIGURATION**
- [🎯 Objective](#-objective)
- [📋 Prerequisites](#-prerequisites)
- [🚀 WSL2 + Ubuntu installation](#-wsl2--ubuntu-installation)
- [🔧 Configuration for repositories](#-configuration-for-repositories)

### ⚠️ **TROUBLESHOOTING**
- [⚠️ Troubleshooting: common errors](#-troubleshooting-common-errors)

### 📁 **ORGANIZATION AND WORKFLOW**
- [📁 Recommended structure](#-recommended-structure)
- [🔄 Recommended workflow](#-recommended-workflow)

### 💡 **RESOURCES AND TIPS**
- [📋 Useful commands](#-useful-commands)
- [✅ Final verification](#-final-verification)
- [💡 Important tips](#-important-tips)

---

## 📋 **DETAILED SUBSECTION INDEX**

### 🚀 **INSTALLATION AND CONFIGURATION - Details**
- [1. Enable WSL (PowerShell as administrator)](#1-enable-wsl-powershell-as-administrator)
- [2. Install WSL2 and Ubuntu](#2-install-wsl2-and-ubuntu)
- [3. Configure Ubuntu (first run)](#3-configure-ubuntu-first-run)
- [Git configuration](#git-configuration)
- [Configure Docker (if needed)](#configure-docker-if-needed)

### ⚠️ **TROUBLESHOOTING - Details**
- [🚨 Error: `/usr/bin/env: 'bash\r': No such file or directory`](#-error-usrbinenv-bashr-no-such-file-or-directory)
- [🚨 Error: permission denied](#-error-permission-denied)
- [🚨 Error: Docker not working](#-error-docker-not-working)
- [🚨 Error: Windows commands on Linux](#-error-windows-commands-on-linux)

### 📁 **ORGANIZATION AND WORKFLOW - Details**
- [Project organization](#project-organization)
- [For new repositories](#for-new-repositories)
- [For existing repositories (with issues)](#for-existing-repositories-with-issues)

---

## ⚡ **QUICK COMMANDS - REFERENCE**

### 🔧 **Initial Git setup**
```bash
# REQUIRED configuration before cloning
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global core.autocrlf false
git config --global core.eol lf
git config --global init.defaultBranch main
git config --global pull.rebase false
```

### 🐧 **WSL2 + Ubuntu installation**
```powershell
# In PowerShell as administrator
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2
wsl --install -d Ubuntu
```

### 🔧 **Ubuntu configuration**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential dos2unix

# Configure Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 🛠️ **Fixing issues**
```bash
# Fix line endings
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;

# Grant execute permission
find . -name "*.sh" -exec chmod +x {} \;

# Check line endings
file file.sh
hexdump -C file.sh | head
```

### 📁 **Project structure**
```bash
# Create recommended layout
cd ~
mkdir projects
cd projects

# Clone repositories
git clone https://github.com/user/repo.git
cd repo
chmod +x *.sh
./build.sh
```

---

## 🆘 **Quick troubleshooting**

### ❌ **Common issues**
- **`/usr/bin/env: 'bash\r': No such file or directory`**: CRLF line endings instead of LF
- **Permission denied**: files without execute permission
- **Docker not working**: Docker Desktop not running or WSL2 integration disabled
- **Windows commands on Linux**: using Windows commands inside WSL

### 🔧 **Quick fixes**
```bash
# Fix line endings
dos2unix file.sh
find . -name "*.sh" -exec dos2unix {} \;

# Grant permissions
chmod +x file.sh
find . -name "*.sh" -exec chmod +x {} \;

# Restart WSL
exit
# In PowerShell: wsl --shutdown
```

### 📞 **Quick help links**
- [⚠️ Troubleshooting: common errors](#-troubleshooting-common-errors)
- [💡 Important tips](#-important-tips)

---

## 💻 **QUICK PRACTICAL EXAMPLES**

### 🚀 **Full setup script**
```bash
#!/bin/bash
# setup-wsl-git.sh - Full WSL + Git setup

echo "🐧 Configuring WSL + Ubuntu for Git repositories..."

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install essential tools
echo "🔧 Installing tools..."
sudo apt install -y git curl wget build-essential dos2unix

# Configure Git
echo "⚙️ Configuring Git..."
read -p "Enter your name: " name
read -p "Enter your email: " email

git config --global user.name "$name"
git config --global user.email "$email"
git config --global core.autocrlf false
git config --global core.eol lf
git config --global init.defaultBranch main
git config --global pull.rebase false

# Create project layout
echo "📁 Creating project layout..."
mkdir -p ~/projects
cd ~/projects

echo "✅ Setup complete!"
echo "📋 Git settings:"
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"

echo ""
echo "🎯 Next steps:"
echo "1. cd ~/projects"
echo "2. git clone https://github.com/user/repo.git"
echo "3. cd repo && chmod +x *.sh && ./build.sh"
```

### 🔍 **Diagnostic script**
```bash
#!/bin/bash
# wsl-git-diagnose.sh - WSL + Git diagnostics

echo "🔍 WSL + Git diagnostics"
echo "======================="

# Check WSL
echo "🐧 WSL:"
wsl --list --verbose

echo ""
echo "📋 Git:"
git --version
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"

echo ""
echo "🔧 Tools:"
which dos2unix
which curl
which wget

echo ""
echo "📁 Layout:"
ls -la ~/projects 2>/dev/null || echo "~/projects directory does not exist"

echo ""
echo "🧪 Line ending test:"
if [ -f "test.sh" ]; then
    file test.sh
    hexdump -C test.sh | head -1
else
    echo "Creating test file..."
    echo '#!/bin/bash' > test.sh
    echo 'echo "Hello World"' >> test.sh
    file test.sh
    hexdump -C test.sh | head -1
    rm test.sh
fi

echo ""
echo "✅ Diagnostics complete!"
```

### 🧹 **Cleanup and fix script**
```bash
#!/bin/bash
# fix-repo.sh - Fix a repository with issues

echo "🧹 Fixing repository..."

# Check we are in a Git repository
if [ ! -d ".git" ]; then
    echo "❌ Not a Git repository!"
    exit 1
fi

# Fix line endings
echo "🔧 Fixing line endings..."
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;
find . -name "*.js" -exec dos2unix {} \;

# Grant execute permission
echo "🔐 Adjusting permissions..."
find . -name "*.sh" -exec chmod +x {} \;

# Verify files
echo "📋 Verifying files..."
echo "Scripts found:"
find . -name "*.sh" -type f

echo ""
echo "Checking line endings:"
for file in $(find . -name "*.sh" -type f); do
    echo -n "$file: "
    file "$file" | grep -q "CRLF" && echo "❌ CRLF" || echo "✅ LF"
done

echo ""
echo "✅ Fix complete!"
echo "🧪 Testing scripts..."
for script in $(find . -name "*.sh" -type f); do
    echo "Testing: $script"
    if bash -n "$script"; then
        echo "✅ $script: syntax OK"
    else
        echo "❌ $script: syntax error"
    fi
done
```

### 🎯 **Repository test script**
```bash
#!/bin/bash
# test-repo.sh - Test the full repository

echo "🎯 Testing repository..."

# Check Git repository
if [ ! -d ".git" ]; then
    echo "❌ Not a Git repository!"
    exit 1
fi

# Check Git configuration
echo "📋 Git configuration:"
git config --global core.autocrlf
git config --global core.eol

# List scripts
echo ""
echo "🔧 Scripts found:"
find . -name "*.sh" -type f

# Test each script
echo ""
echo "🧪 Testing scripts:"
for script in $(find . -name "*.sh" -type f); do
    echo -n "Testing $script: "
    if bash -n "$script" 2>/dev/null; then
        echo "✅ OK"
    else
        echo "❌ ERROR"
    fi
done

# Check line endings
echo ""
echo "📄 Checking line endings:"
for file in $(find . -name "*.sh" -o -name "*.py" -o -name "*.js" | head -5); do
    echo -n "$file: "
    if file "$file" | grep -q "CRLF"; then
        echo "❌ CRLF (problematic)"
    else
        echo "✅ LF (correct)"
    fi
done

echo ""
echo "✅ Test complete!"
```

---

## 🎯 **Objective**
Set up WSL2 + Ubuntu to work with Git repositories without Windows/Linux compatibility issues.

---

## 📋 **Prerequisites**
- Windows 10 version 2004+ or Windows 11
- Administrator permissions
- Internet connection

---

## 🚀 **WSL2 + Ubuntu installation**

### **1. Enable WSL (PowerShell as administrator):**
```powershell
# Enable WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable virtual machine platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart the computer
shutdown /r /t 0
```

### **2. Install WSL2 and Ubuntu:**
```powershell
# Set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu

# Verify installation
wsl --list --verbose
```

### **3. Configure Ubuntu (first run):**
```bash
# You will be prompted to create a user and password
# Example: user "murilo", password of your choice

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential
```

---

## 🔧 **Configuration for repositories**

### **Git configuration:**
Before cloning, configure Git first.
The following commands ensure that:
1. ✅ Files keep Unix-style line endings (LF)
2. ✅ Scripts work on both Windows and WSL
3. ✅ There is no problematic automatic conversion
4. ✅ The repository stays consistent across platforms


```bash
# === REQUIRED CONFIGURATION (BEFORE ANY CLONE) ===
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# CRITICAL: line endings
git config --global core.autocrlf false
git config --global core.eol lf

# Recommended extras
git config --global init.defaultBranch main
git config --global pull.rebase false

# Verify everything
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"
```

```bash
# You can now clone any repository
git clone https://github.com/user/container_monitoramento.git
cd container_monitoramento

# Scripts will work correctly
chmod +x *.sh
./build.sh  # ✅ Success!
```

```bash
# if you cloned before configuring
# 1. Configure Git correctly
git config --global core.autocrlf false
git config --global core.eol lf

# 2. Remove corrupted folder
cd ..
rm -rf old_project

# 3. Clone again
git clone https://github.com/user/project.git
cd project

# ✅ Files will now have correct LF
```
### **Configure Docker (if needed):**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Restart WSL
exit
# In PowerShell: wsl --shutdown
# Reopen Ubuntu
```

---

## ⚠️ **Troubleshooting: common errors**

### **🚨 Error: `/usr/bin/env: 'bash\r': No such file or directory`**

**Cause:** files cloned on Windows have CRLF (`\r\n`) line endings instead of LF (`\n`).

#### **💡 Fixes:**

#### **Option 1: Convert existing files**
```bash
# Single file
dos2unix build.sh

# All .sh files in the directory
find . -name "*.sh" -exec dos2unix {} \;

# Install dos2unix if missing
sudo apt install dos2unix
```

#### **Option 2: Using sed (alternative)**
```bash
# Convert one file
sed -i 's/\r$//' build.sh

# Convert all .sh files
find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
```

#### **Option 3: Reconfigure Git and re-clone**
```bash
# Reconfigure Git
git config --global core.autocrlf false
git config --global core.eol lf

# Re-clone repository
cd /tmp
git clone https://github.com/user/repo.git clean_repo
cd clean_repo

# Verify line endings
file build.sh
# Should show: "Bourne-Again shell script, ASCII text executable"
# Should NOT show: "with CRLF line terminators"
```

---

### **🚨 Error: permission denied**

**Typical message:** `Permission denied` (file without execute permission).

```bash
# Issue: file without execute permission
chmod +x build.sh
chmod +x *.sh

# Multiple files
find . -name "*.sh" -exec chmod +x {} \;
```

---

### **🚨 Error: Docker not working**
```bash
# Check Docker Desktop is running on Windows
# Check WSL2 integration in Docker Desktop

# Test Docker
docker --version
docker run hello-world

# If it fails, restart WSL
# In Windows PowerShell:
wsl --shutdown
# Reopen Ubuntu
```

---

### **🚨 Error: Windows commands on Linux**
```bash
# Issue: trying to use Windows commands in WSL
# ❌ WRONG:
dir
cls

# ✅ CORRECT:
ls
clear
```

---

## 📁 **Recommended structure**

### **Project organization:**
```bash
# Work on the Linux filesystem, NOT under /mnt/c/
cd ~
mkdir projects
cd projects

# Clone repositories here
git clone https://github.com/user/repo.git

# ❌ AVOID working in:
# /mnt/c/Users/user/Desktop/
# (Poor performance + line ending issues)

# ✅ USE:
# ~/projects/ or /home/user/projects/
```

---

## 🔄 **Recommended workflow**

### **For new repositories:**
```bash
# 1. Configure Git correctly
git config --global core.autocrlf false
git config --global core.eol lf

# 2. Clone directly in WSL
cd ~/projects
git clone https://github.com/repo.git

# 3. Develop in WSL
cd repo
chmod +x *.sh
./build.sh
```

### **For existing repositories (with issues):**
```bash
# 1. Clean line endings
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;

# 2. Grant permissions
find . -name "*.sh" -exec chmod +x {} \;

# 3. Test
./build.sh
```

---

## 📋 **Useful commands**

```bash
# Check line endings
file file.sh
hexdump -C file.sh | head

# Convert all text files
find . -type f -exec dos2unix {} \;

# List executable files
find . -type f -executable

# Access Windows files from WSL
cd /mnt/c/Users/$USER/Desktop

# Access WSL files from Windows
# In Explorer: \\wsl$\Ubuntu\home\user
```

---

## ✅ **Final verification**

```bash
# Full test
cd ~/projects
git clone https://github.com/your-repo/container_monitoramento.git
cd container_monitoramento
chmod +x *.sh
ls -la *.sh
file *.sh
./build.sh
```

**If everything runs without errors, your setup is correct! 🎉**

---

## 💡 **Important tips**

- ✅ **Always work in `~/projects/`**, not under `/mnt/c/`
- ✅ **Configure Git before** cloning repositories
- ✅ **Use `dos2unix`** to fix problematic files
- ✅ **Keep Docker Desktop** up to date
- ❌ **Avoid editing** on Windows and running in WSL

---

**🐧 You can now develop comfortably on Ubuntu/WSL! 🚀**

This guide covers line endings (CRLF vs LF) and offers practical ways to work with repositories across Windows and WSL/Ubuntu. 🎯
