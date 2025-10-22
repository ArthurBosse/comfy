FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Déps systeme
RUN apt-get update && apt-get install -y git python3 python3-pip ffmpeg && rm -rf /var/lib/apt/lists/*

# Dossiers
WORKDIR /workspace
ENV PYTHONUNBUFFERED=1
ENV COMFY_DIR=/workspace/ComfyUI
ENV HF_HOME=/workspace/.cache/huggingface

# Installer ComfyUI (stable)
RUN git clone https://github.com/comfyanonymous/ComfyUI.git $COMFY_DIR

# (Optionnel) Installer des custom nodes ici
# RUN git clone https://github.com/....git $COMFY_DIR/custom_nodes/SomeNode

# Python deps ComfyUI
RUN pip install --upgrade pip
RUN pip install -r $COMFY_DIR/requirements.txt

# Runpod + client HTTP + utilitaires
COPY requirements.txt /workspace/requirements.txt
RUN pip install -r /workspace/requirements.txt

# Scripts
COPY start.sh /workspace/start.sh
RUN chmod +x /workspace/start.sh
COPY comfy_client.py /workspace/comfy_client.py
COPY handler.py /workspace/handler.py

# Par défaut, ComfyUI écoutera 0.0.0.0:8188
ENV COMFY_PORT=8188
ENV COMFY_HOST=0.0.0.0

# Pour éviter certains soucis de compilation Triton / FP8 sur GPU non-Hopper
ENV TORCH_DISABLE_DYNAMO=1
ENV TORCHINDUCTOR_DISABLE=1

# Runpod serverless démarre en lançant handler.py
CMD ["/workspace/start.sh"]