import json, os, copy, base64
import runpod
from comfy_client import post_prompt, wait_result

WORKFLOW_PATH = os.environ.get("WORKFLOW_PATH", "/workspace/ComfyUI/workflows/my_workflow.json")
OUTPUT_DIR    = os.environ.get("OUTPUT_DIR",    "/workspace/ComfyUI/output")

def load_workflow():
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_overrides(graph, overrides: dict):
    # overrides = { "44": { "inputs": {"width": 864, "height": 1536}}, "6": {"inputs": {"text": "..."} } }
    g = copy.deepcopy(graph)
    nodes = { str(n["id"]): n for n in g.get("nodes", []) }
    for node_id, patch in overrides.items():
        if node_id in nodes and "inputs" in patch:
            # Trouver les widgets/inputs : on cible "widgets_values" si le node s'y base,
            # sinon gère des inputs dynamiques (selon le type de node)
            inputs = patch["inputs"]
            node = nodes[node_id]
            # Cas simple : inputs directs dans "widgets_values" par ordre
            # → tu peux aussi faire du ciblage par nom (mieux) si tu sais l’ordre exact
            # Ici on fait un patch par nom si ComfyUI expose des "widgets" nommés (selon nœud).
            if "widgets_values" in node:
                # Heuristique : si la valeur existe dans inputs par clé connue, on remplace
                # Sinon on laisse tel quel. Pour être précis, mappe par index toi-même si besoin.
                pass
            # Meilleur : si le node a le champ "inputs" déclaratif, tu peux l'éditer ici.
            if "inputs" in node:
                for k, v in inputs.items():
                    node["inputs"][k] = v
    return g

def collect_images(outputs):
    """Retourne la liste de fichiers générés sous /output + option base64 (petits médias)."""
    files = []
    # ComfyUI renvoie par type. On parcourt images
    for node_id, node_out in outputs.items():
        if "images" in node_out:
            for img in node_out["images"]:
                subfolder = img.get("subfolder","")
                filename  = img["filename"]
                files.append(os.path.join(OUTPUT_DIR, subfolder, filename))
    return files

def file_to_b64(path, limit_mb=8):
    try:
        size = os.path.getsize(path)
        if size > limit_mb * 1024 * 1024:
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None

def handler(event):
    # 1) Entrée
    user_in = event.get("input", {})
    overrides = user_in.get("overrides", {})
    return_b64 = user_in.get("return_b64", False)

    # 2) Charge workflow + overrides
    graph = load_workflow()
    if overrides:
        graph = apply_overrides(graph, overrides)

    # 3) Envoie à ComfyUI
    job = post_prompt(graph)
    prompt_id = job.get("prompt_id")

    # 4) Attend résultat
    outputs = wait_result(prompt_id)

    # 5) Récup fichiers
    files = collect_images(outputs)
    result = {"files": files}

    if return_b64:
        result["base64"] = [file_to_b64(p) for p in files]

    return {"output": result}

runpod.serverless.start({"handler": handler})