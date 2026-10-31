# 🐳 Métodos de Instalação Docker e Docker Compose

Docker é a principal ferramenta de containerização usada e documentada. Já o plugin Docker compose é sua ferramenta mais completa para versionamento e recriação de seus conteúdos.

Com isso, busca-se adotar a prática de versionar e publicar artefatos (imagens, *compose*, etc.) compatíveis com diversas **orquestrações** de *pipelines*.

## 📑 **ÍNDICE DE NAVEGAÇÃO RÁPIDA**

### 🖥️ **INSTALAÇÃO POR SISTEMA**
- [🖥️ Windows](#-windows)
- [🐧 Linux (Ubuntu/Debian)](#-linux-ubuntudebian)
- [🐧 Linux (CentOS/RHEL/Fedora)](#-linux-centosrhelfedora)

### ✅ **VERIFICAÇÃO E CONFIGURAÇÃO**
- [✅ Verificação da Instalação](#-verificação-da-instalação)
- [⚙️ Configuração Pós-Instalação](#️-configuração-pós-instalação)

### 🛠️ **COMANDOS E MANUTENÇÃO**
- [🛠️ Comandos Úteis](#️-comandos-úteis)
- [🔧 Solução de Problemas](#-solução-de-problemas)

### 📊 **REFERÊNCIA RÁPIDA**
- [📊 Resumo Rápido](#-resumo-rápido)

---

## 📋 **ÍNDICE DETALHADO DE SUBSEÇÕES**

### 🖥️ **WINDOWS - Detalhes**
- [Método 1: Docker Desktop (Recomendado)](#método-1-docker-desktop-recomendado)
- [Método 2: WSL2 + Docker (Avançado)](#método-2-wsl2--docker-avançado)

### 🐧 **LINUX (UBUNTU/DEBIAN) - Detalhes**
- [Instalação Rápida](#instalação-rápida)
- [Para ARM64 (Raspberry Pi)](#para-arm64-raspberry-pi)

### 🐧 **LINUX (CENTOS/RHEL/FEDORA) - Detalhes**
- [CentOS/RHEL 8+](#centosrhel-8)
- [Fedora](#fedora)

### ✅ **VERIFICAÇÃO E CONFIGURAÇÃO - Detalhes**
- [Teste Básico](#teste-básico)
- [Teste com Imagem Personalizada](#teste-com-imagem-personalizada)
- [1. Logout/Login](#1-logoutlogin)
- [2. Configurar Docker para iniciar automaticamente](#2-configurar-docker-para-iniciar-automaticamente)
- [3. Configurar proxy (se necessário)](#3-configurar-proxy-se-necessário)

### 🛠️ **COMANDOS E MANUTENÇÃO - Detalhes**
- [Gerenciamento de Containers](#gerenciamento-de-containers)
- [Gerenciamento de Volumes](#gerenciamento-de-volumes)
- [Limpeza Completa](#limpeza-completa)
- [Erro: permissão negada](#erro-permissão-negada)
- [Erro: não conecta ao daemon do Docker](#erro-não-conecta-ao-daemon-do-docker)
- [Erro: porta já em uso](#erro-porta-já-em-uso)

---

## ⚡ **COMANDOS RÁPIDOS - REFERÊNCIA**

### 🔧 **Verificação de Instalação**
```bash
# Verificar versões
docker --version
docker compose version

# Teste básico
docker run hello-world

# Informações do sistema
docker info
```

### 🐳 **Gerenciamento de Containers**
```bash
# Listar containers
docker ps -a

# Parar todos os containers
docker stop $(docker ps -q)

# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune
```

### 📦 **Gerenciamento de Volumes**
```bash
# Listar volumes
docker volume ls

# Remover volumes não utilizados
docker volume prune
```

### 🧹 **Limpeza do Sistema**
```bash
# Limpeza completa (cuidado!)
docker system prune -a --volumes

# Limpeza apenas imagens
docker image prune

# Limpeza apenas containers
docker container prune
```

### 🔍 **Diagnóstico**
```bash
# Status do Docker
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# Verificar portas em uso
sudo netstat -tlnp | grep :8080
```

---

## 🆘 **Solução de problemas rápida**

### ❌ **Problemas Comuns**
- **Permissão negada** (`Permission denied`): usuário não está no grupo `docker`
- **Não conecta ao daemon** (`Cannot connect to daemon`): Docker não está em execução
- **Porta em uso** (`Port already in use`): a porta já está sendo usada por outro processo
- **WSL2 não encontrado** (`WSL2 not found`): o WSL2 não está instalado no Windows

### 🔧 **Soluções Rápidas**
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verificar status
sudo systemctl status docker
```

### 📞 **Links de Ajuda Rápida**
- [🔧 Solução de Problemas](#-solução-de-problemas)
- [📊 Resumo Rápido](#-resumo-rápido)

---

## 💻 **EXEMPLOS PRÁTICOS RÁPIDOS**

### 🚀 **Script de Instalação Automática (Ubuntu/Debian)**
```bash
#!/bin/bash
# install-docker.sh - Instalação automática do Docker

echo "🐳 Instalando Docker e Docker Compose..."

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Adicionar repositório Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

echo "✅ Instalação concluída!"
echo "🔄 Faça logout e login novamente para usar Docker sem sudo"
echo "🧪 Testando instalação..."
docker run hello-world
```

### 🔍 **Script de Diagnóstico**
```bash
#!/bin/bash
# docker-diagnose.sh - Diagnóstico completo do Docker

echo "🔍 Diagnóstico do Docker"
echo "======================="

# Verificar versões
echo "📋 Versões:"
docker --version
docker compose version

echo ""
echo "🔧 Status do serviço:"
sudo systemctl status docker --no-pager

echo ""
echo "🐳 Containers rodando:"
docker ps

echo ""
echo "📦 Imagens disponíveis:"
docker images

echo ""
echo "💾 Volumes:"
docker volume ls

echo ""
echo "🌐 Redes:"
docker network ls

echo ""
echo "📊 Uso de recursos:"
docker system df

echo ""
echo "🧪 Teste de conectividade:"
if docker run --rm hello-world > /dev/null 2>&1; then
    echo "✅ Docker funcionando corretamente!"
else
    echo "❌ Problema na instalação do Docker"
fi
```

### 🧹 **Script de Limpeza**
```bash
#!/bin/bash
# docker-cleanup.sh - Limpeza do Docker

echo "🧹 Limpando Docker..."

# Parar todos os containers
echo "🛑 Parando containers..."
docker stop $(docker ps -q) 2>/dev/null || true

# Remover containers parados
echo "🗑️ Removendo containers parados..."
docker container prune -f

# Remover imagens não utilizadas
echo "🖼️ Removendo imagens não utilizadas..."
docker image prune -f

# Remover volumes não utilizados
echo "💾 Removendo volumes não utilizados..."
docker volume prune -f

# Remover redes não utilizadas
echo "🌐 Removendo redes não utilizadas..."
docker network prune -f

echo "✅ Limpeza concluída!"
echo "📊 Espaço liberado:"
docker system df
```

### 🎯 **Script de Teste de Performance**
```bash
#!/bin/bash
# docker-test.sh - Teste de performance do Docker

echo "🎯 Testando performance do Docker..."

# Teste de pull
echo "📥 Testando download de imagem..."
time docker pull alpine:latest

# Teste de criação de container
echo "🏗️ Testando criação de container..."
time docker run --rm alpine:latest echo "Container criado com sucesso!"

# Teste de build (se Dockerfile existir)
if [ -f "Dockerfile" ]; then
    echo "🔨 Testando build de imagem..."
    time docker build -t test-image .
fi

# Teste de rede
echo "🌐 Testando conectividade de rede..."
docker run --rm alpine:latest ping -c 3 8.8.8.8

echo "✅ Testes concluídos!"
```

---

## **Windows**
### **Método 1: Docker Desktop (Recomendado)**

1. **Baixar Docker Desktop**
   - Acesse: https://www.docker.com/products/docker-desktop/
   - No site, inicie o download para Windows (o botão costuma aparecer como *Download for Windows*).
   - Escolha versão: Windows 10/11 64-bit

2. **Instalar**
   ```bash
   # Execute o arquivo baixado (Docker Desktop Installer.exe)
   # Siga o assistente de instalação
   # Reinicie o computador quando solicitado
   ```

3. **Verificar Instalação**
   ```bash
   # Abra PowerShell como administrador
   docker --version
   docker compose version
   ```

### **Método 2: WSL2 + Docker (Avançado)**

1. **Instalar WSL2**
   ```powershell
   # No PowerShell como administrador
   wsl --install
   ```

2. **Instalar Docker no WSL2**
   ```bash
   # Dentro do WSL2
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

## **Linux (Ubuntu/Debian)**

### **Instalação Rápida**

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Adicionar repositório Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# 6. Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# 7. Verificar instalação
docker --version
docker compose version
```

### **Para ARM64 (Raspberry Pi)**

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Adicionar repositório Docker (ARM64)
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# 6. Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# 7. Verificar instalação
docker --version
docker compose version
```

## **Linux (CentOS/RHEL/Fedora)**

### **CentOS/RHEL 8+**

```bash
# 1. Instalar dependências
sudo dnf install -y dnf-utils

# 2. Adicionar repositório Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. Instalar Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 4. Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# 5. Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# 6. Verificar instalação
docker --version
docker compose version
```

### **Fedora**

```bash
# 1. Instalar Docker
sudo dnf install -y docker docker-compose

# 2. Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# 3. Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# 4. Verificar instalação
docker --version
docker compose version
```

## **Verificação da Instalação**

### **Teste Básico**

```bash
# Verificar versões
docker --version
docker compose version

# Testar com container simples
docker run hello-world

# Verificar se Docker está rodando
docker info
```

### **Teste com Imagem Personalizada**

```bash
# Baixar e executar uma imagem de teste
docker run -it --rm ubuntu:latest bash

# Dentro do container
echo "Docker funcionando!"
exit
```

## **Configuração Pós-Instalação**

### **1. Logout/Login**
```bash
# Após adicionar usuário ao grupo docker
# Faça logout e login novamente
# Ou execute:
newgrp docker
```

### **2. Configurar Docker para iniciar automaticamente**

**Linux:**
```bash
# Já configurado com systemctl enable docker
sudo systemctl status docker
```

**Windows:**
- Docker Desktop inicia automaticamente com o Windows

### **3. Configurar proxy (se necessário)**

**Linux:**
```bash
# Criar diretório de configuração
sudo mkdir -p /etc/systemd/system/docker.service.d

# Criar arquivo de configuração
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf <<EOF
[Service]
Environment="HTTP_PROXY=http://proxy:port"
Environment="HTTPS_PROXY=http://proxy:port"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# Recarregar configuração
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## **Comandos Úteis**

### **Gerenciamento de Containers**
```bash
# Listar containers
docker ps -a

# Parar todos os containers
docker stop $(docker ps -q)

# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune
```

### **Gerenciamento de Volumes**
```bash
# Listar volumes
docker volume ls

# Remover volumes não utilizados
docker volume prune
```

### **Limpeza Completa**
```bash
# Remover tudo (cuidado!)
docker system prune -a --volumes
```

## 🔧 **Solução de problemas**

### **Erro: permissão negada**

Mensagem típica: `Permission denied`.

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
# Ou executar:
newgrp docker
```

### **Erro: não conecta ao daemon do Docker**

Mensagem típica: `Cannot connect to the Docker daemon`.

```bash
# Verificar se Docker está rodando
sudo systemctl status docker

# Iniciar Docker se necessário
sudo systemctl start docker
```

### **Erro: porta já em uso**

Mensagem típica: `Port already in use`.

```bash
# Verificar portas em uso
sudo netstat -tlnp | grep :8080

# Parar processo que está usando a porta
sudo kill -9 <PID>
```

## 📊 **Resumo rápido**

| Sistema | Método | Comando principal |
|---------|--------|-------------------|
| Windows | Docker Desktop | Baixar no site oficial |
| Ubuntu/Debian | Repositório oficial | `sudo apt install docker-ce` |
| ARM64 | Repositório oficial | `sudo apt install docker-ce` |
| CentOS/RHEL | Repositório oficial | `sudo dnf install docker-ce` |
| Fedora | Repositório padrão | `sudo dnf install docker` |

**Após a instalação, sempre execute:**
```bash
docker --version
docker compose version
docker run hello-world
```

**Se todos os comandos funcionarem, a instalação foi bem-sucedida!**