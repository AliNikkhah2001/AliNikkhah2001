#!/usr/bin/env python3
"""
Size Estimation Web Server
==========================
Upload an image -> detect objects (YOLO) -> estimate depth -> compute
metric size estimates + confidence -> visualize.

Run:  python3 app.py
Visit: http://localhost:7860
"""

import io
import os
import time
import json
import base64
import logging
import traceback

import numpy as np

from flask import Flask, request, jsonify, render_template_string
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("size_app")

# --------------------------------------------------------------------------
# Model loading (lazy, with graceful fallbacks)
# --------------------------------------------------------------------------
_yolo = None
_yolo_err = None

_depth = None
_depth_type = None
_depth_err = None

_detector_names = {}


def load_yolo():
    """Load YOLOv8n detector. Returns (model or None, error or None)."""
    global _yolo, _yolo_err
    if _yolo is not None or _yolo_err is not None:
        return _yolo, _yolo_err
    try:
        from ultralytics import YOLO
        start = time.time()
        log.info("Loading YOLOv8n...")
        _yolo = YOLO("yolov8n.pt")
        _detector_names.update(_yolo.names or {})
        log.info(f"YOLOv8n loaded in {time.time() - start:.1f}s")
    except Exception as e:
        _yolo_err = str(e)
        log.error(f"YOLO failed to load: {e}")
    return _yolo, _yolo_err


def load_depth():
    """Load Depth Anything V2 (small) via transformers. Returns (model or None, type or None, err)."""
    global _depth, _depth_type, _depth_err
    if _depth is not None or _depth_type is not None or _depth_err is not None:
        return _depth, _depth_type, _depth_err
    try:
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        import torch

        repo = "depth-anything/Depth-Anything-V2-Small-hf"
        start = time.time()
        log.info(f"Loading depth model {repo}...")
        _depth_processor = AutoImageProcessor.from_pretrained(repo)
        _depth_model = AutoModelForDepthEstimation.from_pretrained(repo)
        _depth = {"processor": _depth_processor, "model": _depth_model, "torch": torch}
        _depth_type = "depth_anything"
        log.info(f"Depth model loaded in {time.time() - start:.1f}s")
    except Exception as e:
        _depth_err = str(e)
        log.error(f"Depth model failed to load, using fallback: {e}")
    return _depth, _depth_type, _depth_err


# --------------------------------------------------------------------------
# Processing
# --------------------------------------------------------------------------
def run_depth(image: np.ndarray) -> np.ndarray:
    """Return a float depth map (relative). Uses model or gradient fallback."""
    if _depth is not None and _depth_type == "depth_anything":
        try:
            import torch
            pil = Image.fromarray(image)
            inputs = _depth["processor"](images=pil, return_tensors="pt")
            with torch.no_grad():
                out = _depth["model"](**inputs)
            depth = out.predicted_depth.squeeze().cpu().numpy()
            # resize to image size
            from PIL import Image as _I
            depth = np.array(_I.fromarray(depth).resize((image.shape[1], image.shape[0]), _I.BILINEAR))
            depth = depth.astype(np.float32)
            if depth.max() > depth.min():
                depth = (depth - depth.min()) / (depth.max() - depth.min())
            return depth
        except Exception as e:
            log.error(f"depth inference failed: {e}")
    return fallback_depth(image)


def fallback_depth(image: np.ndarray) -> np.ndarray:
    """Gradient/pseudo depth map in [0,1] (higher = closer)."""
    import cv2
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
    mag = np.sqrt(sobelx ** 2 + sobely ** 2)
    mag = mag / (mag.max() + 1e-9)
    depth = 1.0 - mag
    h, w = image.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    center = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    depth = depth * (1.0 - 0.4 * np.clip(center, 0, 1))
    return (depth - depth.min()) / (depth.max() - depth.min() + 1e-9)


def estimate_metric(bbox, depth_map, image_shape, det_conf):
    """Convert a bbox + depth into a metric size estimate.

    Uses a pinhole assumption: world_width = bbox_width_px * depth / focal_px.
    Since depth is relative, we normalize so depth==1 corresponds to a
    nominal distance of 1 meter (configurable). Relative sizes within the
    same plane are still meaningful.
    """
    x1, y1, x2, y2 = [float(v) for v in bbox]
    img_h, img_w = image_shape[:2]
    w_px = max(1.0, x2 - x1)
    h_px = max(1.0, y2 - y1)
    cx = int(np.clip((x1 + x2) / 2, 0, img_w - 1))
    cy = int(np.clip((y1 + y2) / 2, 0, img_h - 1))

    # median depth in a small patch around center (robust)
    p = 5
    patch = depth_map[max(0, cy - p):cy + p + 1, max(0, cx - p):cx + p + 1]
    d = float(np.median(patch)) if patch.size else float(depth_map[cy, cx])
    d = max(d, 0.05)

    focal_px = img_w * 1.2  # rough nominal focal length
    # relative depth d in [0,1]; map to meters: 1.0 -> 2.0 m
    meters_depth = 0.5 + d * 3.5

    world_w = (w_px * meters_depth) / focal_px
    world_h = (h_px * meters_depth) / focal_px

    # confidence: blend detection conf with depth quality near center
    depth_quality = float(np.clip(1.0 - abs(d - 0.5) / 0.5, 0.0, 1.0))
    conf = float(np.clip(0.5 * det_conf + 0.5 * depth_quality, 0.0, 1.0))

    return {
        "width_m": round(world_w, 3),
        "height_m": round(world_h, 3),
        "distance_m": round(meters_depth, 2),
        "relative_depth": round(d, 3),
        "confidence": round(conf, 3),
        "detection_conf": round(float(det_conf), 3),
        "depth_quality": round(depth_quality, 3),
    }


def detect_objects(image: np.ndarray, conf_thresh=0.3):
    """Run detection. Returns (detections list, model_used or error)."""
    model, err = load_yolo()
    if model is None:
        return [], f"detector unavailable: {err}"
    import cv2
    results = model(image, conf=conf_thresh, verbose=False)
    dets = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            dets.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class_id": cls,
                "class_name": _detector_names.get(cls, f"class_{cls}"),
            })
    return dets, None


def build_visualization(image, detections, depth_map):
    """Draw bboxes + labels on the image and return annotated numpy array."""
    import cv2
    vis = image.copy()
    depth_vis = None
    if depth_map is not None:
        depth_vis = (np.clip(depth_map, 0, 1) * 255).astype(np.uint8)
        depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
              (255, 0, 255), (0, 255, 255)]
    for i, det in enumerate(detections):
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        color = colors[i % len(colors)]
        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
        m = det.get("metric", {})
        label = f"{det['class_name']} {det['confidence']:.2f}"
        if m:
            label += f"  {m['width_m']}x{m['height_m']}m  d={m['distance_m']}m"
        cv2.putText(vis, label, (x1, max(15, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    return vis, depth_vis


# --------------------------------------------------------------------------
# Flask app
# --------------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Size & Scale Estimation</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; background:#0f1115;
         color:#e6e6e6; margin:0; padding:24px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .sub { color:#999; font-size:14px; margin-bottom:20px; }
  .card { background:#1a1d24; border:1px solid #2a2e3a; border-radius:12px; padding:20px;
          margin-bottom:20px; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
  @media(max-width:900px){ .grid{grid-template-columns:1fr;} }
  #drop { border:2px dashed #3a3f4d; border-radius:12px; padding:40px; text-align:center;
          cursor:pointer; transition:.2s; }
  #drop.hover { border-color:#4a9eff; background:#14202e; }
  #drop input { display:none; }
  #preview { max-width:100%; max-height:360px; margin-top:12px; border-radius:8px; display:none; }
  button { background:#3b82f6; color:#fff; border:none; border-radius:8px; padding:10px 22px;
           font-size:15px; cursor:pointer; margin-top:14px; }
  button:disabled { opacity:.5; cursor:not-allowed; }
  #results { display:none; }
  .imgs { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  .imgs figure { margin:0; }
  .imgs img { width:100%; border-radius:8px; border:1px solid #2a2e3a; }
  figcaption { font-size:13px; color:#999; margin-top:6px; text-align:center; }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th, td { padding:8px 10px; text-align:left; border-bottom:1px solid #262b36; }
  th { color:#9aa3b2; font-weight:600; }
  .conf { color:#7ee787; }
  #meta { color:#9aa3b2; font-size:13px; margin-bottom:12px; }
  #status { color:#ffb454; font-size:14px; margin-top:10px; }
  .err { color:#ff6b6b; }
</style>
</head>
<body>
  <h1>Object Size &amp; Scale Estimation</h1>
  <div class="sub">Upload an image &rarr; YOLO detection + depth model &rarr; metric size estimates with confidence</div>

  <div class="grid">
    <div class="card">
      <div id="drop">Drop an image here or click to choose
        <input type="file" id="file" accept="image/*">
        <div id="status"></div>
      </div>
      <img id="preview" alt="preview">
      <button id="go" disabled>Analyze Image</button>
    </div>

    <div class="card" id="results">
      <div id="meta"></div>
      <div class="imgs">
        <figure><img id="out_vis" alt="annotated"><figcaption>Detections &amp; sizes</figcaption></figure>
        <figure><img id="out_depth" alt="depth"><figcaption>Depth map</figcaption></figure>
      </div>
      <h3 style="margin-top:16px;">Detected objects</h3>
      <table>
        <thead><tr><th>#</th><th>Class</th><th>Conf</th><th>Width</th><th>Height</th>
        <th>Distance</th><th>Box</th></tr></thead>
        <tbody id="rows"></tbody>
      </table>
    </div>
  </div>

<script>
const drop=document.getElementById('drop'), file=document.getElementById('file'),
      prev=document.getElementById('preview'), go=document.getElementById('go'),
      statusEl=document.getElementById('status'), results=document.getElementById('results');

let currentImage=null;

drop.onclick=()=>file.click();
drop.ondragover=(e)=>{e.preventDefault();drop.classList.add('hover');};
drop.ondragleave=()=>drop.classList.remove('hover');
drop.ondrop=(e)=>{e.preventDefault();drop.classList.remove('hover'); if(e.dataTransfer.files[0]) handle(e.dataTransfer.files[0]);};
file.onchange=()=>{if(file.files[0]) handle(file.files[0]);};

function handle(f){
  currentImage=f;
  prev.src=URL.createObjectURL(f); prev.style.display='block';
  go.disabled=false; statusEl.textContent='';
}
go.onclick=async ()=>{
  if(!currentImage) return;
  go.disabled=true; statusEl.textContent='Analyzing... (first run may take a minute to load models)';
  const fd=new FormData(); fd.append('image', currentImage);
  try{
    const r=await fetch('/analyze',{method:'POST',body:fd});
    const d=await r.json();
    if(!r.ok) throw new Error(d.error||'server error');
    statusEl.textContent='';
    document.getElementById('meta').innerHTML = d.meta.join(' &nbsp;|&nbsp; ');
    document.getElementById('out_vis').src='data:image/jpeg;base64,'+d.vis;
    document.getElementById('out_depth').src='data:image/jpeg;base64,'+d.depth;
    const rows=document.getElementById('rows');
    rows.innerHTML='';
    d.detections.forEach((o,i)=>{
      const tr=document.createElement('tr');
      tr.innerHTML=`<td>${i+1}</td><td>${o.class_name}</td>
        <td class="conf">${o.confidence.toFixed(2)}</td>
        <td>${o.metric.width_m.toFixed(3)} m</td>
        <td>${o.metric.height_m.toFixed(3)} m</td>
        <td>${o.metric.distance_m.toFixed(2)} m</td>
        <td style="font-size:12px">[${o.bbox.map(v=>v.toFixed(0)).join(', ')}]</td>`;
      rows.appendChild(tr);
    });
    results.style.display='block';
  }catch(e){
    statusEl.className='err'; statusEl.textContent='Error: '+e.message;
  }finally{ go.disabled=false; }
};
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/analyze", methods=["POST"])
def analyze():
    t0 = time.time()
    if "image" not in request.files:
        return jsonify({"error": "no image provided"}), 400
    f = request.files["image"]
    try:
        img_bytes = f.read()
        pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        image = np.array(pil)
    except Exception as e:
        return jsonify({"error": f"could not read image: {e}"}), 400

    # ensure not too huge
    if image.shape[1] > 1600 or image.shape[0] > 1600:
        scale = min(1.0, 1600.0 / max(image.shape[:2]))
        pil = pil.resize((int(image.shape[1]*scale), int(image.shape[0]*scale)))
        image = np.array(pil)

    depth_map = run_depth(image)

    detections, err = detect_objects(image)
    if err:
        return jsonify({"error": err}), 500

    for det in detections:
        det["metric"] = estimate_metric(det["bbox"], depth_map, image.shape, det["confidence"])

    vis, depth_vis = build_visualization(image, detections, depth_map)

    def to_b64(arr):
        from PIL import Image as _I
        buf = io.BytesIO()
        _I.fromarray(arr.astype(np.uint8)).save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode()

    meta = []
    det_model, _ = load_yolo()
    depth_info = "Depth Anything V2" if _depth_type == "depth_anything" else "gradient fallback"
    meta.append(f"detector: {'YOLOv8n' if det_model else 'N/A'}")
    meta.append(f"depth: {depth_info}")
    meta.append(f"objects: {len(detections)}")
    meta.append(f"time: {time.time()-t0:.2f}s")

    return jsonify({
        "detections": detections,
        "vis": to_b64(vis),
        "depth": to_b64(depth_vis),
        "meta": meta,
    })


if __name__ == "__main__":
    load_yolo()
    load_depth()
    port = int(os.environ.get("PORT", "7860"))
    print(f"\n  Size Estimation server -> http://localhost:{port}\n", flush=True)
    app.run(host="0.0.0.0", port=port, threaded=True)
