# 🐧 Guia: WSL + Ubuntu para Repositórios

Muitas vezes o mesmo repositório será usado em sistemas Git para **Linux** e **Windows** ao mesmo tempo.

Verifique abaixo como deixar isso pronto e evitar erros relacionados.

## 📑 **ÍNDICE DE NAVEGAÇÃO RÁPIDA**

### 🚀 **INSTALAÇÃO E CONFIGURAÇÃO**
- [🎯 Objetivo](#-objetivo)
- [📋 Pré-requisitos](#-pré-requisitos)
- [🚀 Instalação do WSL2 + Ubuntu](#-instalação-do-wsl2--ubuntu)
- [🔧 Configuração para Repositórios](#-configuração-para-repositórios)

### ⚠️ **SOLUÇÃO DE PROBLEMAS**
- [⚠️ Solução de problemas: erros comuns](#-solução-de-problemas-erros-comuns)

### 📁 **ORGANIZAÇÃO E FLUXO DE TRABALHO**
- [📁 Estrutura recomendada](#-estrutura-recomendada)
- [🔄 Fluxo de trabalho recomendado](#-fluxo-de-trabalho-recomendado)

### 💡 **RECURSOS E DICAS**
- [📋 Comandos Úteis](#-comandos-úteis)
- [✅ Verificação Final](#-verificação-final)
- [💡 Dicas Importantes](#-dicas-importantes)

---

## 📋 **ÍNDICE DETALHADO DE SUBSEÇÕES**

### 🚀 **INSTALAÇÃO E CONFIGURAÇÃO - Detalhes**
- [1. Habilitar WSL (PowerShell como administrador)](#1-habilitar-wsl-powershell-como-administrador)
- [2. Instalar WSL2 e Ubuntu](#2-instalar-wsl2-e-ubuntu)
- [3. Configurar Ubuntu (primeira execução)](#3-configurar-ubuntu-primeira-execução)
- [Configuração do Git](#configuração-do-git)
- [Configurar Docker (se necessário)](#configurar-docker-se-necessário)

### ⚠️ **SOLUÇÃO DE PROBLEMAS - Detalhes**
- [🚨 Erro: `/usr/bin/env: 'bash\r': No such file or directory`](#-erro-usrbinenv-bashr-no-such-file-or-directory)
- [🚨 Erro: permissão negada](#-erro-permissão-negada)
- [🚨 Erro: Docker não funciona](#-erro-docker-não-funciona)
- [🚨 Erro: Comandos Windows no Linux](#-erro-comandos-windows-no-linux)

### 📁 **ORGANIZAÇÃO E FLUXO DE TRABALHO - Detalhes**
- [Organização de Projetos](#organização-de-projetos)
- [Para Novos Repositórios](#para-novos-repositórios)
- [Para Repositórios Existentes (com problemas)](#para-repositórios-existentes-com-problemas)

---

## ⚡ **COMANDOS RÁPIDOS - REFERÊNCIA**

### 🔧 **Configuração Inicial do Git**
```bash
# Configuração OBRIGATÓRIA antes de clonar
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git config --global core.autocrlf false
git config --global core.eol lf
git config --global init.defaultBranch main
git config --global pull.rebase false
```

### 🐧 **Instalação WSL2 + Ubuntu**
```powershell
# No PowerShell como administrador
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2
wsl --install -d Ubuntu
```

### 🔧 **Configuração Ubuntu**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas essenciais
sudo apt install -y git curl wget build-essential dos2unix

# Configurar Docker (opcional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 🛠️ **Correção de Problemas**
```bash
# Corrigir finais de linha
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;

# Dar permissões de execução
find . -name "*.sh" -exec chmod +x {} \;

# Verificar finais de linha
file arquivo.sh
hexdump -C arquivo.sh | head
```

### 📁 **Estrutura de Projetos**
```bash
# Criar estrutura recomendada
cd ~
mkdir projetos
cd projetos

# Clonar repositórios
git clone https://github.com/usuario/repo.git
cd repo
chmod +x *.sh
./build.sh
```

---

## 🆘 **Solução de problemas rápida**

### ❌ **Problemas comuns**
- **`/usr/bin/env: 'bash\r': No such file or directory`**: finais de linha em CRLF em vez de LF
- **Permissão negada** (`Permission denied`): arquivos sem permissão de execução
- **Docker não funciona**: Docker Desktop não está rodando ou integração WSL2 desabilitada
- **Comandos Windows no Linux**: Usar comandos Windows no WSL

### 🔧 **Soluções Rápidas**
```bash
# Corrigir finais de linha
dos2unix arquivo.sh
find . -name "*.sh" -exec dos2unix {} \;

# Dar permissões
chmod +x arquivo.sh
find . -name "*.sh" -exec chmod +x {} \;

# Reiniciar WSL
exit
# No PowerShell: wsl --shutdown
```

### 📞 **Links de ajuda rápida**
- [⚠️ Solução de problemas: erros comuns](#-solução-de-problemas-erros-comuns)
- [💡 Dicas Importantes](#-dicas-importantes)

---

## 💻 **EXEMPLOS PRÁTICOS RÁPIDOS**

### 🚀 **Script de Configuração Completa**
```bash
#!/bin/bash
# setup-wsl-git.sh - Configuração completa do WSL + Git

echo "🐧 Configurando WSL + Ubuntu para repositórios Git..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas essenciais
echo "🔧 Instalando ferramentas..."
sudo apt install -y git curl wget build-essential dos2unix

# Configurar Git
echo "⚙️ Configurando Git..."
read -p "Digite seu nome: " nome
read -p "Digite seu email: " email

git config --global user.name "$nome"
git config --global user.email "$email"
git config --global core.autocrlf false
git config --global core.eol lf
git config --global init.defaultBranch main
git config --global pull.rebase false

# Criar estrutura de projetos
echo "📁 Criando estrutura de projetos..."
mkdir -p ~/projetos
cd ~/projetos

echo "✅ Configuração concluída!"
echo "📋 Configurações do Git:"
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"

echo ""
echo "🎯 Próximos passos:"
echo "1. cd ~/projetos"
echo "2. git clone https://github.com/usuario/repo.git"
echo "3. cd repo && chmod +x *.sh && ./build.sh"
```

### 🔍 **Script de Diagnóstico**
```bash
#!/bin/bash
# wsl-git-diagnose.sh - Diagnóstico do WSL + Git

echo "🔍 Diagnóstico WSL + Git"
echo "======================="

# Verificar WSL
echo "🐧 WSL:"
wsl --list --verbose

echo ""
echo "📋 Git:"
git --version
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"

echo ""
echo "🔧 Ferramentas:"
which dos2unix
which curl
which wget

echo ""
echo "📁 Estrutura:"
ls -la ~/projetos 2>/dev/null || echo "Diretório ~/projetos não existe"

echo ""
echo "🧪 Teste de finais de linha:"
if [ -f "test.sh" ]; then
    file test.sh
    hexdump -C test.sh | head -1
else
    echo "Criando arquivo de teste..."
    echo '#!/bin/bash' > test.sh
    echo 'echo "Hello World"' >> test.sh
    file test.sh
    hexdump -C test.sh | head -1
    rm test.sh
fi

echo ""
echo "✅ Diagnóstico concluído!"
```

### 🧹 **Script de Limpeza e Correção**
```bash
#!/bin/bash
# fix-repo.sh - Corrigir repositório com problemas

echo "🧹 Corrigindo repositório..."

# Verificar se estamos em um repositório Git
if [ ! -d ".git" ]; then
    echo "❌ Não é um repositório Git!"
    exit 1
fi

# Corrigir finais de linha
echo "🔧 Corrigindo finais de linha..."
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;
find . -name "*.js" -exec dos2unix {} \;

# Dar permissões de execução
echo "🔐 Ajustando permissões..."
find . -name "*.sh" -exec chmod +x {} \;

# Verificar arquivos
echo "📋 Verificando arquivos..."
echo "Scripts encontrados:"
find . -name "*.sh" -type f

echo ""
echo "Verificando finais de linha:"
for file in $(find . -name "*.sh" -type f); do
    echo -n "$file: "
    file "$file" | grep -q "CRLF" && echo "❌ CRLF" || echo "✅ LF"
done

echo ""
echo "✅ Correção concluída!"
echo "🧪 Testando scripts..."
for script in $(find . -name "*.sh" -type f); do
    echo "Testando: $script"
    if bash -n "$script"; then
        echo "✅ $script: Sintaxe OK"
    else
        echo "❌ $script: Erro de sintaxe"
    fi
done
```

### 🎯 **Script de Teste de Repositório**
```bash
#!/bin/bash
# test-repo.sh - Testar repositório completo

echo "🎯 Testando repositório..."

# Verificar se é repositório Git
if [ ! -d ".git" ]; then
    echo "❌ Não é um repositório Git!"
    exit 1
fi

# Verificar configuração Git
echo "📋 Configuração Git:"
git config --global core.autocrlf
git config --global core.eol

# Verificar scripts
echo ""
echo "🔧 Scripts encontrados:"
find . -name "*.sh" -type f

# Testar cada script
echo ""
echo "🧪 Testando scripts:"
for script in $(find . -name "*.sh" -type f); do
    echo -n "Testando $script: "
    if bash -n "$script" 2>/dev/null; then
        echo "✅ OK"
    else
        echo "❌ ERRO"
    fi
done

# Verificar finais de linha
echo ""
echo "📄 Verificando finais de linha:"
for file in $(find . -name "*.sh" -o -name "*.py" -o -name "*.js" | head -5); do
    echo -n "$file: "
    if file "$file" | grep -q "CRLF"; then
        echo "❌ CRLF (problemático)"
    else
        echo "✅ LF (correto)"
    fi
done

echo ""
echo "✅ Teste concluído!"
```

---

## 🎯 **Objetivo**
Configurar WSL2 + Ubuntu para trabalhar com repositórios Git sem problemas de compatibilidade Windows/Linux.

---

## 📋 **Pré-requisitos**
- Windows 10 versão 2004+ ou Windows 11
- Permissões de administrador
- Conexão com internet

---

## 🚀 **Instalação do WSL2 + Ubuntu**

### **1. Habilitar WSL (PowerShell como administrador):**
```powershell
# Habilitar WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Habilitar Máquina Virtual
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Reiniciar o computador
shutdown /r /t 0
```

### **2. Instalar WSL2 e Ubuntu:**
```powershell
# Definir WSL2 como padrão
wsl --set-default-version 2

# Instalar Ubuntu
wsl --install -d Ubuntu

# Verificar instalação
wsl --list --verbose
```

### **3. Configurar Ubuntu (primeira execução):**
```bash
# Será solicitado criar usuário e senha
# Exemplo: usuário "murilo", senha de sua escolha

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas essenciais
sudo apt install -y git curl wget build-essential
```

---

## 🔧 **Configuração para Repositórios**

### **Configuração do Git:**
Antes de clonar, configure o Git primeiro.
Os comandos a seguir garantem que:
1. ✅ Os arquivos mantêm finais de linha no padrão Unix (LF)
2. ✅ Scripts funcionam tanto no Windows quanto WSL
3. ✅ Não há conversão automática problemática
4. ✅ Repositório fica consistente entre plataformas


```bash
# === CONFIGURAÇÃO OBRIGATÓRIA (ANTES DE QUALQUER CLONE) ===
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# CRÍTICO: Line endings
git config --global core.autocrlf false
git config --global core.eol lf

# Extras recomendados
git config --global init.defaultBranch main
git config --global pull.rebase false

# Verificar tudo
git config --global --list | grep -E "(user|autocrlf|eol|defaultBranch)"
```

```bash
# Agora pode clonar qualquer repositório
git clone https://github.com/user/container_monitoramento.git
cd container_monitoramento

# Scripts funcionarão corretamente
chmod +x *.sh
./build.sh  # ✅ Sucesso!
```

```bash
# se clonou antes de configurar
# 1. Configurar Git corretamente
git config --global core.autocrlf false
git config --global core.eol lf

# 2. Remover pasta corrompida
cd ..
rm -rf projeto_antigo

# 3. Clonar novamente
git clone https://github.com/user/projeto.git
cd projeto

# ✅ Agora arquivos terão LF correto
```
### **Configurar Docker (se necessário):**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar WSL
exit
# No PowerShell: wsl --shutdown
# Reabrir Ubuntu
```

---

## ⚠️ **Solução de problemas: erros comuns**

### **🚨 Erro: `/usr/bin/env: 'bash\r': No such file or directory`**

**Causa:** arquivos clonados no Windows têm finais de linha em CRLF (`\r\n`) em vez de LF (`\n`).

#### **💡 Soluções:**

#### **Opção 1: Converter arquivos existentes**
```bash
# Para um arquivo específico
dos2unix build.sh

# Para todos os arquivos .sh no diretório
find . -name "*.sh" -exec dos2unix {} \;

# Instalar dos2unix se não estiver disponível
sudo apt install dos2unix
```

#### **Opção 2: Via sed (alternativa)**
```bash
# Converter um arquivo
sed -i 's/\r$//' build.sh

# Converter todos os .sh
find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
```

#### **Opção 3: Reconfigurar Git e re-clonar**
```bash
# Reconfigurar Git
git config --global core.autocrlf false
git config --global core.eol lf

# Re-clonar repositório
cd /tmp
git clone https://github.com/usuario/repo.git repo_limpo
cd repo_limpo

# Verificar finais de linha
file build.sh
# Deve mostrar: "Bourne-Again shell script, ASCII text executable"
# NÃO deve mostrar: "with CRLF line terminators"
```

---

### **🚨 Erro: permissão negada**

**Mensagem típica:** `Permission denied` (arquivo sem permissão de execução).

```bash
# Problema: arquivo sem permissão de execução
chmod +x build.sh
chmod +x *.sh

# Para múltiplos arquivos
find . -name "*.sh" -exec chmod +x {} \;
```

---

### **🚨 Erro: Docker não funciona**
```bash
# Verificar se Docker Desktop está rodando no Windows
# Verificar integração WSL2 no Docker Desktop

# Testar Docker
docker --version
docker run hello-world

# Se falhar, reiniciar WSL
# No PowerShell Windows:
wsl --shutdown
# Reabrir Ubuntu
```

---

### **🚨 Erro: Comandos Windows no Linux**
```bash
# Problema: tentar usar comandos Windows no WSL
# ❌ ERRADO:
dir
cls

# ✅ CORRETO:
ls
clear
```

---

## 📁 **Estrutura Recomendada**

### **Organização de Projetos:**
```bash
# Trabalhar no sistema Linux, NÃO em /mnt/c/
cd ~
mkdir projetos
cd projetos

# Clonar repositórios aqui
git clone https://github.com/usuario/repo.git

# ❌ EVITAR trabalhar em:
# /mnt/c/Users/usuario/Desktop/
# (Desempenho ruim + problemas de finais de linha)

# ✅ USAR:
# ~/projetos/ ou /home/usuario/projetos/
```

---

## 🔄 **Fluxo de trabalho recomendado**

### **Para Novos Repositórios:**
```bash
# 1. Configurar Git corretamente
git config --global core.autocrlf false
git config --global core.eol lf

# 2. Clonar direto no WSL
cd ~/projetos
git clone https://github.com/repo.git

# 3. Fazer desenvolvimento no WSL
cd repo
chmod +x *.sh
./build.sh
```

### **Para Repositórios Existentes (com problemas):**
```bash
# 1. Limpar finais de linha
find . -name "*.sh" -exec dos2unix {} \;
find . -name "*.py" -exec dos2unix {} \;

# 2. Dar permissões
find . -name "*.sh" -exec chmod +x {} \;

# 3. Testar
./build.sh
```

---

## 📋 **Comandos Úteis**

```bash
# Verificar finais de linha
file arquivo.sh
hexdump -C arquivo.sh | head

# Converter todos os arquivos de texto
find . -type f -exec dos2unix {} \;

# Ver todos os arquivos executáveis
find . -type f -executable

# Acessar arquivos Windows do WSL
cd /mnt/c/Users/$USER/Desktop

# Acessar arquivos WSL do Windows
# No Explorer: \\wsl$\Ubuntu\home\usuario
```

---

## ✅ **Verificação Final**

```bash
# Teste completo
cd ~/projetos
git clone https://github.com/seu-repo/container_monitoramento.git
cd container_monitoramento
chmod +x *.sh
ls -la *.sh
file *.sh
./build.sh
```

**Se tudo funcionar sem erros, configuração está correta! 🎉**

---

## 💡 **Dicas Importantes**

- ✅ **Sempre trabalhe em `~/projetos/`**, não em `/mnt/c/`
- ✅ **Configure Git antes** de clonar repositórios
- ✅ **Use `dos2unix`** para corrigir arquivos problemáticos
- ✅ **Mantenha Docker Desktop** atualizado
- ❌ **Evite editar** no Windows e executar no WSL

---

**🐧 Agora você pode desenvolver tranquilamente no Ubuntu/WSL! 🚀**

Este guia cobre o problema de finais de linha (CRLF vs LF) e oferece soluções práticas para trabalhar com repositórios entre Windows e WSL/Ubuntu. 🎯