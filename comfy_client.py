import requests
import time

BASE = "http://127.0.0.1:8188"

def post_prompt(graph):
    r = requests.post(f"{BASE}/prompt", json={"prompt": graph})
    r.raise_for_status()
    return r.json()

def get_history(prompt_id):
    return requests.get(f"{BASE}/history/{prompt_id}").json()

def wait_result(prompt_id, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = get_history(prompt_id)
        if prompt_id in h and "outputs" in h[prompt_id]:
            return h[prompt_id]["outputs"]
        time.sleep(0.5)
    raise TimeoutError("ComfyUI result timeout")