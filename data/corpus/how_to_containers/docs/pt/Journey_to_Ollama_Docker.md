# Journey to Ollama Docker — No GPU, no problem

Esta documentação é um **guia prático** para **executar o Ollama em Docker** no seu ambiente local, com caminhos distintos para **CPU** (quando não há GPU dedicada), **NVIDIA (CUDA)** ou **AMD (ROCm)**.

- **Sobre o quê é:** preparação (SO / WSL / verificação de GPU), instalação do Docker, subida do container `ollama/ollama`, configuração do *NVIDIA Container Toolkit* quando necessário, testes e validação da API.
- **Como funciona:** segue o [Fluxo recomendado](#fluxo-recomendado) numerado de **0 a 5**; cada **seção** corresponde a uma etapa. Siga na ordem ou **pule** o que você já tiver feito (por exemplo, Docker já instalado).
- **Onde rodar os comandos:** os exemplos assumem **Linux** ou **WSL2 com Ubuntu** para o Docker Engine; no Windows nativo, use o Docker Desktop e adapte caminhos conforme a documentação oficial.

**Depois de concluir este roteiro, o que você poderá fazer?**

- Ter o serviço Ollama **local** na porta **11434**, com modelos salvos no **volume** do container (ou em pasta montada).
- **Baixar e executar** modelos de texto com `docker exec … ollama pull/run` e usar a **API HTTP** (`/api/tags`, `/api/generate`) a partir do host, scripts ou notebooks.
- (Opcional) Testar **multimodal** (ex.: `llava`) e, no **apêndice**, validar **CUDA/PyTorch no host** — útil para *benchmarks* fora do container; **não é obrigatório** para o Ollama em Docker.

## Objetivo

Este guia cobre um fluxo prático para executar Ollama localmente:

- Modo **CPU** (sem GPU)
- Modo **GPU NVIDIA** (CUDA) via Docker
- Modo **GPU AMD** (ROCm), quando aplicável
- Validação por **comandos**, **API HTTP** e (opcional) **inferência com imagem**

## Fluxo recomendado

0. [Preparação](#0-preparação)
1. [Instalar e validar Docker](#1-instalar-e-validar-docker)
2. [Subir o container Ollama (CPU ou GPU)](#2-subir-o-container-ollama-cpu-ou-gpu)
3. [Baixar e testar modelo de texto](#3-baixar-e-testar-modelo-de-texto)
4. [Validar a API HTTP](#4-validar-a-api-http)
5. [(Opcional) Pipeline multimodal (imagem)](#5-opcional-pipeline-multimodal-imagem)

## Importante

- Sem GPU NVIDIA, o Ollama funciona em **CPU** normalmente.
- **CUDA** só acelera quando o host tem GPU, driver compatível e **NVIDIA Container Toolkit** configurado.
- GPUs de entrada (ex.: 2 GB VRAM): prefira **modelos menores** e evite várias inferências ao mesmo tempo.

---

## 0. Preparação

### Sistema operacional

Este processo funciona melhor em **Linux** (incluindo distro no **WSL2**).

Se estiver no Windows e precisar de WSL + Ubuntu, consulte o guia:  
[Guia WSL com Ubuntu para repositórios](./Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md)

### Verificar NVIDIA (apenas se for usar GPU NVIDIA)

```bash
nvidia-smi
```

- Se **funcionar**, você pode seguir para [2.2 NVIDIA (CUDA)](#22-nvidia-cuda).
- Se **falhar**, use o caminho **CPU** em [2.1 CPU (sem GPU)](#21-cpu-sem-gpu). Não dá para “inventar” GPU no Docker; o *fallback* é CPU.

---

## 1. Instalar e validar Docker

Siga o passo a passo em [Install_Docker.md](./Install_Docker.md) (e, se precisar, os guias complementares na pasta `docs/`).

Validação mínima:

```bash
docker info
docker run --rm hello-world
```

---

## 2. Subir o container Ollama (CPU ou GPU)

Escolha **uma** das subseções abaixo, de acordo com o seu hardware.

### 2.1 CPU (sem GPU)

```bash
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

O comando devolve o **ID do container**; você também pode vê-lo com `docker ps -a`.

**Modelos em pasta do host** (opcional):

```bash
docker run -d \
  -v /caminho/para/modelos:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### 2.2 NVIDIA (CUDA)

Confirme o driver no host:

```bash
nvidia-smi
```

#### Exemplo de saída (referência)

Abaixo, um exemplo real de saída (GeForce MX110, driver 451.67, CUDA 11.0). A saída no seu caso será diferente, conforme a GPU e o driver.

```text
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 451.67       Driver Version: 451.67       CUDA Version: 11.0     |
|   0  GeForce MX110      WDDM  | ... |     37MiB /  2048MiB |      0%      |
+-----------------------------------------------------------------------------+
```

GPUs **de entrada** (pouca VRAM): use modelos menores e monitore memória.

#### NVIDIA Container Toolkit

Documentação oficial: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation).

Os passos abaixo instalam o toolkit no **mesmo Linux onde o Docker Engine corre** (por exemplo, Ubuntu dentro do **WSL2** ou um servidor). A diferença entre **Apt** e **Yum/Dnf** é só a **família da distribuição**: pacotes **`.deb`** (Debian, Ubuntu, Linux Mint derivado, etc.) vs **`.rpm`** (RHEL, CentOS Stream, Fedora, Rocky Linux, AlmaLinux, etc.). Escolha **um** bloco — o que corresponde ao seu sistema — e ignore o outro.

**Debian/Ubuntu (Apt):**

1. Repositório:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
```

2. Pacotes:

```bash
sudo apt-get install -y nvidia-container-toolkit
```

**RHEL/CentOS/Fedora (Yum/Dnf):**

```bash
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo \
  | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo yum install -y nvidia-container-toolkit
```

**Configurar o Docker e reiniciar:**

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**Subir o Ollama com GPU:**

```bash
docker run -d \
  --gpus=all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### 2.3 AMD (ROCm)

Use este caminho quando a aceleração for **AMD** com suporte **ROCm** no host (drivers/*stack* corretos) e os dispositivos **`/dev/kfd`** e **`/dev/dri`** existirem — típico em Linux com GPU AMD configurada para computação. A imagem **`ollama/ollama:rocm`** é a variante para esse ecossistema. **NVIDIA** segue no [2.2](#22-nvidia-cuda) com **`ollama/ollama`** e `--gpus=all`; na mesma máquina, siga **só** o fabricante da GPU que você for usar.

```bash
docker run -d \
  --device /dev/kfd --device /dev/dri \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama:rocm
```

---

## 3. Baixar e testar modelo de texto

### Comandos úteis do Docker

```bash
docker ps -a
docker logs --tail 100 ollama
docker stats ollama
```

### Listar, baixar e executar modelos

```bash
docker exec -it ollama ollama list
docker exec -it ollama ollama pull qwen2.5
docker exec -it ollama ollama run qwen2.5
```

No modo interativo, use `/bye` para sair.

### Shell dentro do container

```bash
docker exec -it ollama /bin/bash
```

Dentro do container: `ollama list`, `ollama pull tinyllama`, etc. Para sair: `exit`.

---

## 4. Validar a API HTTP

Com o container em execução, a API escuta em `http://localhost:11434`.

### Listar tags / modelos

```bash
curl http://localhost:11434/api/tags
```

### Geração (exemplo)

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5",
    "prompt": "Responda em uma frase: o que é o Ollama?",
    "stream": false
  }'
```

### Cliente Python (LangChain) — opcional

Ambiente (Windows / exemplo):

```batch
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install langchain langchain-core langchain-community tenacity jupyter notebook ipykernel
python -m ipykernel install --user --name=ia_ollama_docker --display-name="ia ollama docker"
```

Exemplo de script (Python):

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from tenacity import retry, stop_after_attempt, wait_exponential

template = """Question: {question}
Answer: Let's think step by step."""

prompt = ChatPromptTemplate.from_template(template)
model = Ollama(model="qwen2.5", base_url="http://localhost:11434")
chain = prompt | model

attempt_count = 0
max_attempts = 5

@retry(stop=stop_after_attempt(max_attempts), wait=wait_exponential(multiplier=1, min=4, max=60))
def invoke_chain(question):
    global attempt_count
    attempt_count += 1
    try:
        return chain.invoke({"question": question})
    except Exception as e:
        print(f"Attempt {attempt_count} of {max_attempts} failed: {e}")
        raise

try:
    response = invoke_chain("How can I get to the moon in the fastest way?")
    print(response)
except Exception as e:
    print("Failed to get a response after multiple attempts.")
    print(f"Error: {e}")
```

Este teste pode levar de 1 a 3 minutos, conforme modelo e hardware.

---

## 5. (Opcional) Pipeline multimodal (imagem)

Para validar **imagem** com Ollama no Docker, use um modelo visual (ex.: `llava`).

1. Baixar o modelo:

```bash
docker exec -it ollama ollama pull llava
```

2. Exemplo de script de teste (use `imagem_teste.jpg` no diretório atual):

```python
import base64
import requests

with open("imagem_teste.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "llava",
    "prompt": "Descreva a imagem em até 3 linhas.",
    "images": [img_b64],
    "stream": False,
}

resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
resp.raise_for_status()
print(resp.json().get("response", "Sem resposta"))
```

Se a descrição fizer sentido em relação à imagem, a verificação está concluída.

---

## Apêndice — CUDA + PyTorch no host (opcional)

> Esta **seção** **não** é necessária para o Ollama em Docker. Serve para **validar CUDA/PyTorch no sistema operacional host** (por exemplo, notebooks no Windows).

### A.1 CUDA Toolkit no Windows (quem tem GPU NVIDIA)

Se precisar instalar ou alinhar versão do toolkit no host:

- [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

Siga o assistente (Windows, x86_64, instalador `.exe`). Se o `nvidia-smi` não mostrar a versão esperada, verifique as variáveis de ambiente (ex.: `CUDA_HOME`) apontando para a pasta de instalação.

### A.2 Instalar PyTorch com CUDA

Use o seletor oficial: [PyTorch — Get Started](https://pytorch.org/get-started/locally/)

Exemplo (ajuste à sua versão CUDA):

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### A.3 Teste rápido de CUDA no PyTorch

```python
import torch

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
else:
    print("Nenhum CUDA disponível")
```

### A.4 Classificação de imagem (ImageNet — exemplo)

```python
import requests
import torch
from PIL import Image as PILImage
from io import BytesIO
from torchvision import transforms, models
from IPython.display import display

LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(LABELS_URL, timeout=30).text.split("\n")

model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def describe_image(image_path: str) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    if image_path.startswith("http"):
        response = requests.get(image_path, timeout=30)
        image = PILImage.open(BytesIO(response.content))
    else:
        image = PILImage.open(image_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    img_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)

    _, indices = torch.sort(outputs, descending=True)
    percentages = torch.nn.functional.softmax(outputs, dim=1)[0] * 100

    print("Top 5 previsões:")
    for idx in indices[0][:5]:
        print(f"{labels[idx]}: {percentages[idx].item():.2f}%")

    display(image.resize((512, int(512 * image.height / image.width))))

image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Felis_silvestris_gordoni.jpg/1024px-Felis_silvestris_gordoni.jpg"
describe_image(image_path)
```

### A.5 Benchmark CIFAR-10 (referência)

O CIFAR-10 tem 60.000 imagens 32×32 em 10 classes (50.000 treino / 10.000 teste). Classes: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck.

O script abaixo compara tempos de passagem pelo modelo em GPU vs CPU (valores dependem do hardware):

```python
import time
import torch
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader
from tqdm import tqdm

transform = transforms.Compose([transforms.ToTensor()])
dataset = datasets.CIFAR10(root="./data", train=True, download=True, transform=transform)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)

def test_performance(device):
    model.to(device)
    model.eval()
    total_time = 0.0
    total_processing_time = 0.0
    with torch.no_grad():
        for images, _ in tqdm(dataloader, desc=str(device)):
            start_time = time.time()
            images = images.to(device)
            start_processing = time.time()
            _ = model(images)
            total_processing_time += time.time() - start_processing
            total_time += time.time() - start_time
    return total_time, total_processing_time

if torch.cuda.is_available():
    print("\nTestando na GPU...")
    gpu_time, gpu_proc = test_performance("cuda")
    print(f"Tempo de processamento na GPU: {gpu_proc:.2f} segundos")
else:
    print("CUDA não está disponível.")

print("\nTestando na CPU...")
cpu_time, cpu_proc = test_performance("cpu")
print(f"Tempo de processamento na CPU: {cpu_proc:.2f} segundos")

if torch.cuda.is_available():
    print(f"\nProcessamento (forward) na GPU ~ {(cpu_proc / gpu_proc):.1f}x vs CPU (métrica aproximada)")
```

#### Exemplo de saída (máquina de referência)

```text
Testando na GPU...
cuda: 100%|...| 782/782 [05:30<00:00, 2.37it/s]
Tempo de processamento na GPU: 3.15 segundos

Testando na CPU...
cpu: 100%|...| 782/782 [08:16<00:00, 1.58it/s]
Tempo de processamento na CPU: 480.50 segundos
```

---

## Fontes

- [![Discord](https://dcbadge.vercel.app/api/server/ollama?style=flat&compact=true)](https://discord.gg/ollama)
- [Ollama (GitHub)](https://github.com/ollama/ollama)
- [Imagem Docker `ollama/ollama`](https://hub.docker.com/r/ollama/ollama)
