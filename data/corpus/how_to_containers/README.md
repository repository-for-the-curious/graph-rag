---
Repo: how_to_containers
CreatedAt: 2026-03
StageTags:
  - 1.4
DomainTags:
  - 2.5
  - 2.6
  - 2.9
  - 2.11
TopicTags:
  - 3.2
  - 3.5
  - 3.10
  - 3.19
  - 3.20
LibraryTags:
  - 4.5
  - 4.9
ModuleTags:
  - 5.6
  - 5.7
  - 5.10
---

# how_to_containers

**🇧🇷** Documentação operacional para **Docker**, **Docker Compose**, **WSL2 + Ubuntu** (Git, finais de linha, Docker Desktop) e **Ollama em containers** (CPU, NVIDIA CUDA, AMD ROCm), em [`docs/pt`](docs/pt/), [`docs/en`](docs/en/), [`docs/de`](docs/de/).

**🇺🇸** Operational docs for **Docker**, **Docker Compose**, **WSL2 + Ubuntu** (Git, line endings, Docker Desktop), and **Ollama in containers** (CPU, NVIDIA CUDA, AMD ROCm) — same guides in [`docs/pt`](docs/pt/), [`docs/en`](docs/en/), [`docs/de`](docs/de/).

**🇩🇪** Operative Dokumentation zu **Docker**, **Docker Compose**, **WSL2 + Ubuntu** (Git, Zeilenenden, Docker Desktop) und **Ollama in Containern** (CPU, NVIDIA CUDA, AMD ROCm) — dieselben Leitfäden in [`docs/pt`](docs/pt/), [`docs/en`](docs/en/), [`docs/de`](docs/de/).

<a id="menu"></a>
## Menu

- 🔙 [SEARCH_CONTENT](https://github.com/repository-for-the-curious/knowledge-hub/blob/main/SEARCH_CONTENT.md)
- [Visão geral](#overview) · [Estrutura](#architecture) · [Tags (hub)](#semantic-integration) · [Ficheiros](#modules) · [Referências](#references)

---

<a id="overview"></a>
## Visão geral

Repositório de **guias práticos** (não é uma aplicação): instalar e validar Docker Engine e plugin Compose; usar WSL2 + Ubuntu para evitar **CRLF/LF** e problemas de permissão em Git; roteiro **Ollama** (`ollama/ollama`) com CLI, **API HTTP** e exemplos opcionais (Python/LangChain, multimodal). Objetivo: menos fricção em ambientes locais/CI com containers e inferência local.

**In English:** How-to docs only (not a deployed service): Docker/Compose install & checks, WSL2+Ubuntu for Git line endings and permissions, full **Ollama** walkthrough with CLI, HTTP API, optional examples — for smoother local/CI setups with containers and on-device inference.

**Auf Deutsch:** Nur **Anleitungen** (keine ausgelieferte App): Docker/Compose installieren und prüfen, WSL2+Ubuntu für Git-Zeilenenden und Rechte, durchgängiger **Ollama**-Leitfaden mit CLI, HTTP-API, optionalen Beispielen — weniger Reibung für lokale/CI-Umgebungen mit Containern und lokaler Inferenz.

---

<a id="architecture"></a>
## Estrutura

- Pastas **`docs/pt`**, **`docs/en`**, **`docs/de`** — mesmo conjunto de ficheiros; links relativos válidos **dentro** de cada pasta.
- Guias: `Install_Docker.md`, `Guia_instalação_Docker_e_docker_compose.md`, `Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md`, `Journey_to_Ollama_Docker.md`.
- Script auxiliar: `install_Docker_linux.sh` (Ubuntu/Debian, repositório oficial Docker).
- Não há API ou serviço próprio — só Markdown e scripts de exemplo.

---

<a id="semantic-integration"></a>
## Tags · Integração com `SEARCH_CONTENT.md`

Códigos do glossário numérico do *knowledge-hub*:

| Tipo | Códigos | Justificativa |
|------|---------|---------------|
| **StageTags** | 1.4 | Material de referência (*Resource*). |
| **DomainTags** | 2.5, 2.6, 2.9, 2.11 | Desenvolvimento, ambiente, fluxo de dados/inferência, análise e diagnóstico. |
| **TopicTags** | 3.2, 3.5, 3.10, 3.19, 3.20 | Automação com containers, IA (Ollama), APIs HTTP, orquestração (*compose* / *pipelines*), *deployment* containerizado. |
| **LibraryTags** | 4.5, 4.9 | Exemplos com `requests` e notebooks nos guias. |
| **ModuleTags** | 5.6, 5.7, 5.10 | Guias/relatórios, chamadas à API Ollama, orquestração com Docker/Compose. |

---

<a id="modules"></a>
## Ficheiros principais

Os mesmos nomes em **`docs/pt/`**, **`docs/en/`** e **`docs/de/`**:

| Ficheiro | Descrição |
|---------|-----------|
| `install_Docker_linux.sh` | Instalação automatizada (Ubuntu/Debian); mensagens por idioma na pasta. |
| `Install_Docker.md` | Instalação multiplataforma (resumo). |
| `Guia_instalação_Docker_e_docker_compose.md` | Guia longo, comandos rápidos, scripts exemplo, *troubleshooting*. |
| `Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md` | WSL2, Git (`core.autocrlf` / `eol`), projetos, *troubleshooting*. |
| `Journey_to_Ollama_Docker.md` | Fluxo 0–5 (Docker → Ollama → modelos → API → multimodal); apêndice PyTorch/CUDA opcional. |

---

<a id="references"></a>
## Referências

| Idioma | Pasta |
|--------|--------|
| Português (BR) | [`docs/pt/`](docs/pt/) |
| English | [`docs/en/`](docs/en/) |
| Deutsch | [`docs/de/`](docs/de/) |

**Ligações externas:** [Docker Docs](https://docs.docker.com/) · [Ollama](https://github.com/ollama/ollama) · [Image `ollama/ollama`](https://hub.docker.com/r/ollama/ollama) · [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)

[Menu](#menu)
