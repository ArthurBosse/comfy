#!/usr/bin/env bash
set -e

# 1) Lancer ComfyUI en arrière-plan (API + no-inductor)
#    --disable-mps (si mac), --listen 0.0.0.0 pour API externe si besoin
python3 /workspace/ComfyUI/main.py \
  --listen $COMFY_HOST \
  --port $COMFY_PORT \
  --dont-print-server \
  --disable-inductor \
  > /workspace/comfy.log 2>&1 &

# 2) Attendre que l'API soit up
echo "Waiting for ComfyUI to start on port ${COMFY_PORT}..."
for i in {1..60}; do
  if curl -s "http://127.0.0.1:${COMFY_PORT}/system_stats" > /dev/null; then
    echo "ComfyUI is up."
    break
  fi
  sleep 1
done

# 3) Démarrer le serveur Runpod (handler.py)
python3 -u /workspace/handler.py