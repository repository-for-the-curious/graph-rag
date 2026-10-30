# Instalar Docker e Docker Compose
Docker é a principal ferramenta de containerização usada e documentada. Já o plugin Docker compose é sua ferramenta mais completa para versionamento e recriação de seus conteúdos.

Com isso, busca-se adotar a prática de versionar e publicar artefatos (imagens, *compose*, etc.) compatíveis com diversas **orquestrações** de *pipelines*.

# Métodos de Instalação
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