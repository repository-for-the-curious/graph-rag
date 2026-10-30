# Journey to Ollama Docker — No GPU, no problem

Diese Dokumentation ist ein **praktischer Leitfaden**, um **Ollama in Docker** in deiner lokalen Umgebung zu betreiben — mit klar getrennten Wegen für **CPU** (ohne dedizierte GPU), **NVIDIA (CUDA)** oder **AMD (ROCm)**.

- **Worum es geht:** Vorbereitung (Betriebssystem / WSL / GPU-Prüfung), Docker-Installation, Start des Containers `ollama/ollama`, Konfiguration des *NVIDIA Container Toolkit* falls nötig, Tests und Validierung der API.
- **So funktioniert es:** Es folgt dem [empfohlenen Ablauf](#empfohlener-ablauf) in den nummerierten Schritten **0 bis 5**; jeder **Abschnitt** entspricht einer Etappe. Arbeite der Reihe nach oder **überspringe**, was du schon erledigt hast (z. B. Docker bereits installiert).
- **Wo du die Befehle ausführst:** Die Beispiele gehen von **Linux** oder **WSL2 mit Ubuntu** für die Docker Engine aus; unter nativem Windows nutzt du Docker Desktop und passt Pfade gemäß der offiziellen Dokumentation an.

**Nach diesem Ablauf kannst du:**

- Den Ollama-Dienst **lokal** auf Port **11434** betreiben, mit Modellen im **Volume** des Containers (oder in einem gemounteten Ordner).
- **Modelle herunterladen und ausführen** mit `docker exec … ollama pull/run` und die **HTTP-API** (`/api/tags`, `/api/generate`) vom Host, aus Skripten oder Notebooks nutzen.
- (Optional) **Multimodal** testen (z. B. `llava`) und im **Anhang** **CUDA/PyTorch auf dem Host** prüfen — nützlich für *Benchmarks* außerhalb des Containers; für Ollama in Docker **nicht erforderlich**.

## Ziel

Dieser Leitfaden beschreibt einen praktischen Ablauf für lokales Ollama:

- **CPU-Modus** (ohne GPU)
- **NVIDIA-GPU-Modus** (CUDA) über Docker
- **AMD-GPU-Modus** (ROCm), falls zutreffend
- Validierung per **Befehlen**, **HTTP-API** und (optional) **Inferenz mit Bild**

## Empfohlener Ablauf

0. [Vorbereitung](#0-vorbereitung)
1. [Docker installieren und validieren](#1-docker-installieren-und-validieren)
2. [Ollama-Container starten (CPU oder GPU)](#2-ollama-container-starten-cpu-oder-gpu)
3. [Textmodell herunterladen und testen](#3-textmodell-herunterladen-und-testen)
4. [HTTP-API validieren](#4-http-api-validieren)
5. [(Optional) Multimodale Pipeline (Bild)](#5-optional-multimodale-pipeline-bild)

## Wichtig

- Ohne NVIDIA-GPU läuft Ollama normalerweise auf der **CPU**.
- **CUDA** bringt nur etwas, wenn der Host eine GPU hat, ein passender Treiber installiert ist und das **NVIDIA Container Toolkit** eingerichtet ist.
- Einstiegs-GPUs (z. B. 2 GB VRAM): lieber **kleinere Modelle** und keine parallelen Inferenzen im großen Stil.

---

## 0. Vorbereitung

### Betriebssystem

Dieser Ablauf funktioniert am besten unter **Linux** (einschließlich einer Distribution unter **WSL2**).

Wenn du unter Windows bist und WSL + Ubuntu brauchst, sieh im Leitfaden nach:  
[Leitfaden WSL mit Ubuntu für Repositories](./Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md)

### NVIDIA prüfen (nur bei NVIDIA-GPU)

```bash
nvidia-smi
```

- **Funktioniert es**, kannst du mit [2.2 NVIDIA (CUDA)](#22-nvidia-cuda) weitermachen.
- **Schlägt es fehl**, nimm den **CPU**-Weg unter [2.1 CPU (ohne GPU)](#21-cpu-ohne-gpu). Eine GPU lässt sich im Docker nicht „erfinden“; der *Fallback* ist CPU.

---

## 1. Docker installieren und validieren

Folge der Schritt-für-Schritt-Anleitung in [Install_Docker.md](./Install_Docker.md) (und bei Bedarf den ergänzenden Guides im Ordner `docs/`).

Minimale Prüfung:

```bash
docker info
docker run --rm hello-world
```

---

## 2. Ollama-Container starten (CPU oder GPU)

Wähle **eine** der folgenden Unterabschnitte passend zu deiner Hardware.

### 2.1 CPU (ohne GPU)

```bash
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

Der Befehl liefert die **Container-ID**; du siehst sie auch mit `docker ps -a`.

**Modelle in einem Host-Ordner** (optional):

```bash
docker run -d \
  -v /caminho/para/modelos:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### 2.2 NVIDIA (CUDA)

Treiber auf dem Host prüfen:

```bash
nvidia-smi
```

#### Beispielausgabe (Referenz)

Unten eine reale Beispielausgabe (GeForce MX110, Treiber 451.67, CUDA 11.0). Bei dir sieht die Ausgabe je nach GPU und Treiber anders aus.

```text
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 451.67       Driver Version: 451.67       CUDA Version: 11.0     |
|   0  GeForce MX110      WDDM  | ... |     37MiB /  2048MiB |      0%      |
+-----------------------------------------------------------------------------+
```

**Einstiegs-GPUs** (wenig VRAM): kleinere Modelle nutzen und den Speicher im Blick behalten.

#### NVIDIA Container Toolkit

Offizielle Dokumentation: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation).

Die folgenden Schritte installieren das Toolkit auf **demselben Linux, auf dem die Docker Engine läuft** (z. B. Ubuntu unter **WSL2** oder ein Server). Der Unterschied zwischen **Apt** und **Yum/Dnf** ist nur die **Distribution**: Pakete **`.deb`** (Debian, Ubuntu, abgeleitetes Linux Mint usw.) vs. **`.rpm`** (RHEL, CentOS Stream, Fedora, Rocky Linux, AlmaLinux usw.). Wähle **einen** Block — der zu deinem System passt — und ignoriere den anderen.

**Debian/Ubuntu (Apt):**

1. Repository:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
```

2. Pakete:

```bash
sudo apt-get install -y nvidia-container-toolkit
```

**RHEL/CentOS/Fedora (Yum/Dnf):**

```bash
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo \
  | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo yum install -y nvidia-container-toolkit
```

**Docker konfigurieren und neu starten:**

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**Ollama mit GPU starten:**

```bash
docker run -d \
  --gpus=all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### 2.3 AMD (ROCm)

Diesen Weg nutzt du, wenn die Beschleunigung **AMD** mit **ROCm**-Unterstützung auf dem Host erfolgt (Treiber/*Stack* korrekt) und die Geräte **`/dev/kfd`** und **`/dev/dri`** vorhanden sind — typisch unter Linux mit für Computing eingerichteter AMD-GPU. Das Image **`ollama/ollama:rocm`** ist die Variante für dieses Ökosystem. **NVIDIA** bleibt bei [2.2](#22-nvidia-cuda) mit **`ollama/ollama`** und `--gpus=all`; auf demselben Rechner folgst du **nur** dem Hersteller der GPU, die du nutzen willst.

```bash
docker run -d \
  --device /dev/kfd --device /dev/dri \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama:rocm
```

---

## 3. Textmodell herunterladen und testen

### Nützliche Docker-Befehle

```bash
docker ps -a
docker logs --tail 100 ollama
docker stats ollama
```

### Modelle auflisten, herunterladen und ausführen

```bash
docker exec -it ollama ollama list
docker exec -it ollama ollama pull qwen2.5
docker exec -it ollama ollama run qwen2.5
```

Im interaktiven Modus beendest du mit `/bye`.

### Shell im Container

```bash
docker exec -it ollama /bin/bash
```

Im Container: `ollama list`, `ollama pull tinyllama` usw. Beenden: `exit`.

---

## 4. HTTP-API validieren

Während der Container läuft, lauscht die API unter `http://localhost:11434`.

### Tags / Modelle auflisten

```bash
curl http://localhost:11434/api/tags
```

### Generierung (Beispiel)

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5",
    "prompt": "Antworte in einem Satz: Was ist Ollama?",
    "stream": false
  }'
```

### Python-Client (LangChain) — optional

Umgebung (Windows / Beispiel):

```batch
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install langchain langchain-core langchain-community tenacity jupyter notebook ipykernel
python -m ipykernel install --user --name=ia_ollama_docker --display-name="ia ollama docker"
```

Beispielskript (Python):

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

Dieser Test kann je nach Modell und Hardware etwa 1–3 Minuten dauern.

---

## 5. (Optional) Multimodale Pipeline (Bild)

Um **Bilder** mit Ollama in Docker zu prüfen, nutzt du ein Vision-Modell (z. B. `llava`).

1. Modell herunterladen:

```bash
docker exec -it ollama ollama pull llava
```

2. Beispiel-Testskript (verwende `testbild.jpg` im aktuellen Verzeichnis):

```python
import base64
import requests

with open("testbild.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "llava",
    "prompt": "Beschreibe das Bild in höchstens drei Zeilen.",
    "images": [img_b64],
    "stream": False,
}

resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
resp.raise_for_status()
print(resp.json().get("response", "Keine Antwort"))
```

Wenn die Beschreibung zur Bilddatei passt, ist die Prüfung abgeschlossen.

---

## Anhang — CUDA + PyTorch auf dem Host (optional)

> Dieser **Abschnitt** ist für Ollama in Docker **nicht** nötig. Er dient dazu, **CUDA/PyTorch im Host-Betriebssystem** zu prüfen (z. B. Notebooks unter Windows).

### A.1 CUDA Toolkit unter Windows (bei NVIDIA-GPU)

Wenn du das Toolkit auf dem Host installieren oder die Version angleichen musst:

- [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

Folge dem Assistenten (Windows, x86_64, Installer `.exe`). Wenn `nvidia-smi` nicht die erwartete Version zeigt, prüfe Umgebungsvariablen (z. B. `CUDA_HOME`) auf den Installationsordner.

### A.2 PyTorch mit CUDA installieren

Nutze den offiziellen Konfigurator: [PyTorch — Get Started](https://pytorch.org/get-started/locally/)

Beispiel (an deine CUDA-Version anpassen):

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### A.3 Schnelltest CUDA in PyTorch

```python
import torch

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
else:
    print("Kein CUDA verfügbar")
```

### A.4 Bildklassifikation (ImageNet — Beispiel)

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

    print("Top-5-Vorhersagen:")
    for idx in indices[0][:5]:
        print(f"{labels[idx]}: {percentages[idx].item():.2f}%")

    display(image.resize((512, int(512 * image.height / image.width))))

image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Felis_silvestris_gordoni.jpg/1024px-Felis_silvestris_gordoni.jpg"
describe_image(image_path)
```

### A.5 Benchmark CIFAR-10 (Referenz)

CIFAR-10 enthält 60.000 Bilder 32×32 in 10 Klassen (50.000 Training / 10.000 Test). Klassen: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck.

Das folgende Skript vergleicht die Laufzeiten für einen Durchlauf durch das Modell auf GPU vs. CPU (Werte hängen von der Hardware ab):

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
    print("\nTest auf GPU...")
    gpu_time, gpu_proc = test_performance("cuda")
    print(f"Verarbeitungszeit auf der GPU: {gpu_proc:.2f} Sekunden")
else:
    print("CUDA ist nicht verfügbar.")

print("\nTest auf CPU...")
cpu_time, cpu_proc = test_performance("cpu")
print(f"Verarbeitungszeit auf der CPU: {cpu_proc:.2f} Sekunden")

if torch.cuda.is_available():
    print(f"\nForward auf der GPU ~ {(cpu_proc / gpu_proc):.1f}× vs. CPU (näherungsweise Metrik)")
```

#### Beispielausgabe (Referenzrechner)

```text
Test auf GPU...
cuda: 100%|...| 782/782 [05:30<00:00, 2.37it/s]
Verarbeitungszeit auf der GPU: 3.15 Sekunden

Test auf CPU...
cpu: 100%|...| 782/782 [08:16<00:00, 1.58it/s]
Verarbeitungszeit auf der CPU: 480.50 Sekunden
```

---

## Quellen

- [![Discord](https://dcbadge.vercel.app/api/server/ollama?style=flat&compact=true)](https://discord.gg/ollama)
- [Ollama (GitHub)](https://github.com/ollama/ollama)
- [Docker-Image `ollama/ollama`](https://hub.docker.com/r/ollama/ollama)
