# Journey to Ollama Docker — No GPU, no problem

This documentation is a **practical guide** to **running Ollama in Docker** on your local environment, with distinct paths for **CPU** (when there is no dedicated GPU), **NVIDIA (CUDA)**, or **AMD (ROCm)**.

- **What it covers:** preparation (OS / WSL / GPU check), Docker installation, starting the `ollama/ollama` container, configuring the *NVIDIA Container Toolkit* when needed, tests, and API validation.
- **How it works:** follow the numbered [Recommended flow](#recommended-flow) from **0 to 5**; each **section** is one step. Follow in order or **skip** what you have already done (for example, Docker already installed).
- **Where to run commands:** the examples assume **Linux** or **WSL2 with Ubuntu** for Docker Engine; on native Windows, use Docker Desktop and adapt paths per the official documentation.

**After you finish this walkthrough, what will you be able to do?**

- Have the Ollama service **locally** on port **11434**, with models stored in the container **volume** (or a mounted folder).
- **Download and run** text models with `docker exec … ollama pull/run` and use the **HTTP API** (`/api/tags`, `/api/generate`) from the host, scripts, or notebooks.
- (Optional) Try **multimodal** (e.g. `llava`) and, in the **appendix**, validate **CUDA/PyTorch on the host** — useful for *benchmarks* outside the container; **not required** for Ollama in Docker.

## Objective

This guide covers a practical flow to run Ollama locally:

- **CPU** mode (no GPU)
- **NVIDIA GPU** mode (CUDA) via Docker
- **AMD GPU** mode (ROCm), when applicable
- Validation via **commands**, **HTTP API**, and (optional) **image inference**

## Recommended flow

0. [Preparation](#0-preparation)
1. [Install and validate Docker](#1-install-and-validate-docker)
2. [Run the Ollama container (CPU or GPU)](#2-run-the-ollama-container-cpu-or-gpu)
3. [Download and test a text model](#3-download-and-test-a-text-model)
4. [Validate the HTTP API](#4-validate-the-http-api)
5. [(Optional) Multimodal pipeline (image)](#5-optional-multimodal-pipeline-image)

## Important

- Without an NVIDIA GPU, Ollama usually runs fine on **CPU**.
- **CUDA** only accelerates when the host has a GPU, a compatible driver, and the **NVIDIA Container Toolkit** configured.
- Entry-level GPUs (e.g. 2 GB VRAM): prefer **smaller models** and avoid several inferences at once.

---

## 0. Preparation

### Operating system

This process works best on **Linux** (including a distro on **WSL2**).

If you are on Windows and need WSL + Ubuntu, see the guide:  
[WSL with Ubuntu for repositories guide](./Guia_Guia_WSL_com_Ubuntu_para_Repositorios.md)

### Check NVIDIA (only if you will use an NVIDIA GPU)

```bash
nvidia-smi
```

- If it **works**, you can continue to [2.2 NVIDIA (CUDA)](#22-nvidia-cuda).
- If it **fails**, use the **CPU** path in [2.1 CPU (without GPU)](#21-cpu-without-gpu). You cannot “invent” a GPU in Docker; the *fallback* is CPU.

---

## 1. Install and validate Docker

Follow the step-by-step in [Install_Docker.md](./Install_Docker.md) (and, if needed, the complementary guides in the `docs/` folder).

Minimal validation:

```bash
docker info
docker run --rm hello-world
```

---

## 2. Run the Ollama container (CPU or GPU)

Choose **one** of the subsections below according to your hardware.

### 2.1 CPU (without GPU)

```bash
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

The command returns the **container ID**; you can also see it with `docker ps -a`.

**Models on a host folder** (optional):

```bash
docker run -d \
  -v /path/to/models:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### 2.2 NVIDIA (CUDA)

Confirm the driver on the host:

```bash
nvidia-smi
```

#### Example output (reference)

Below is a real sample output (GeForce MX110, driver 451.67, CUDA 11.0). Your output will differ depending on the GPU and driver.

```text
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 451.67       Driver Version: 451.67       CUDA Version: 11.0     |
|   0  GeForce MX110      WDDM  | ... |     37MiB /  2048MiB |      0%      |
+-----------------------------------------------------------------------------+
```

**Entry-level** GPUs (little VRAM): use smaller models and monitor memory.

#### NVIDIA Container Toolkit

Official documentation: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation).

The steps below install the toolkit on the **same Linux where Docker Engine runs** (for example, Ubuntu inside **WSL2** or a server). The difference between **Apt** and **Yum/Dnf** is only the **distribution family**: **`.deb`** packages (Debian, Ubuntu, Linux Mint derivatives, etc.) vs **`.rpm`** (RHEL, CentOS Stream, Fedora, Rocky Linux, AlmaLinux, etc.). Pick **one** block — the one that matches your system — and ignore the other.

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

2. Packages:

```bash
sudo apt-get install -y nvidia-container-toolkit
```

**RHEL/CentOS/Fedora (Yum/Dnf):**

```bash
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo \
  | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo yum install -y nvidia-container-toolkit
```

**Configure Docker and restart:**

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**Start Ollama with GPU:**

```bash
docker run -d \
  --gpus=all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

### 2.3 AMD (ROCm)

Use this path when acceleration is **AMD** with **ROCm** support on the host (correct drivers/*stack*) and the **`/dev/kfd`** and **`/dev/dri`** devices exist — typical on Linux with an AMD GPU set up for compute. The **`ollama/ollama:rocm`** image is the variant for that ecosystem. **NVIDIA** stays in [2.2](#22-nvidia-cuda) with **`ollama/ollama`** and `--gpus=all`; on the same machine, follow **only** the GPU vendor you will use.

```bash
docker run -d \
  --device /dev/kfd --device /dev/dri \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama:rocm
```

---

## 3. Download and test a text model

### Useful Docker commands

```bash
docker ps -a
docker logs --tail 100 ollama
docker stats ollama
```

### List, download, and run models

```bash
docker exec -it ollama ollama list
docker exec -it ollama ollama pull qwen2.5
docker exec -it ollama ollama run qwen2.5
```

In interactive mode, use `/bye` to exit.

### Shell inside the container

```bash
docker exec -it ollama /bin/bash
```

Inside the container: `ollama list`, `ollama pull tinyllama`, etc. To leave: `exit`.

---

## 4. Validate the HTTP API

With the container running, the API listens at `http://localhost:11434`.

### List tags / models

```bash
curl http://localhost:11434/api/tags
```

### Generation (example)

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5",
    "prompt": "Answer in one sentence: what is Ollama?",
    "stream": false
  }'
```

### Python client (LangChain) — optional

Environment (Windows / example):

```batch
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install langchain langchain-core langchain-community tenacity jupyter notebook ipykernel
python -m ipykernel install --user --name=ia_ollama_docker --display-name="ia ollama docker"
```

Sample script (Python):

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

This test may take 1 to 3 minutes depending on the model and hardware.

---

## 5. (Optional) Multimodal pipeline (image)

To validate **images** with Ollama in Docker, use a vision model (e.g. `llava`).

1. Download the model:

```bash
docker exec -it ollama ollama pull llava
```

2. Sample test script (use `test_image.jpg` in the current directory):

```python
import base64
import requests

with open("test_image.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "llava",
    "prompt": "Describe the image in at most 3 lines.",
    "images": [img_b64],
    "stream": False,
}

resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
resp.raise_for_status()
print(resp.json().get("response", "No response"))
```

If the description matches the image, verification is complete.

---

## Appendix — CUDA + PyTorch on the host (optional)

> This **section** is **not** required for Ollama in Docker. It is for **validating CUDA/PyTorch on the host OS** (for example, notebooks on Windows).

### A.1 CUDA Toolkit on Windows (NVIDIA GPU)

If you need to install or align the toolkit version on the host:

- [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)

Follow the wizard (Windows, x86_64, `.exe` installer). If `nvidia-smi` does not show the expected version, check environment variables (e.g. `CUDA_HOME`) pointing to the install folder.

### A.2 Install PyTorch with CUDA

Use the official selector: [PyTorch — Get Started](https://pytorch.org/get-started/locally/)

Example (adjust to your CUDA version):

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### A.3 Quick CUDA test in PyTorch

```python
import torch

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
else:
    print("No CUDA available")
```

### A.4 Image classification (ImageNet — example)

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

    print("Top 5 predictions:")
    for idx in indices[0][:5]:
        print(f"{labels[idx]}: {percentages[idx].item():.2f}%")

    display(image.resize((512, int(512 * image.height / image.width))))

image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Felis_silvestris_gordoni.jpg/1024px-Felis_silvestris_gordoni.jpg"
describe_image(image_path)
```

### A.5 CIFAR-10 benchmark (reference)

CIFAR-10 has 60,000 32×32 images in 10 classes (50,000 train / 10,000 test). Classes: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck.

The script below compares model forward-pass times on GPU vs CPU (values depend on hardware):

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
    print("\nRunning on GPU...")
    gpu_time, gpu_proc = test_performance("cuda")
    print(f"GPU processing time: {gpu_proc:.2f} seconds")
else:
    print("CUDA is not available.")

print("\nRunning on CPU...")
cpu_time, cpu_proc = test_performance("cpu")
print(f"CPU processing time: {cpu_proc:.2f} seconds")

if torch.cuda.is_available():
    print(f"\nForward pass on GPU ~ {(cpu_proc / gpu_proc):.1f}x vs CPU (approximate metric)")
```

#### Sample output (reference machine)

```text
Running on GPU...
cuda: 100%|...| 782/782 [05:30<00:00, 2.37it/s]
GPU processing time: 3.15 seconds

Running on CPU...
cpu: 100%|...| 782/782 [08:16<00:00, 1.58it/s]
CPU processing time: 480.50 seconds
```

---

## Sources

- [![Discord](https://dcbadge.vercel.app/api/server/ollama?style=flat&compact=true)](https://discord.gg/ollama)
- [Ollama (GitHub)](https://github.com/ollama/ollama)
- [Docker image `ollama/ollama`](https://hub.docker.com/r/ollama/ollama)
