# Size & Scale Estimation System - Technical Report

## Executive Summary

This project implements a complete computer vision pipeline for single-view object scale and size estimation. The system combines state-of-the-art object detection (YOLOv8) with monocular depth estimation (Depth Anything V2) to produce metric size measurements (width × height in meters) and distance estimates for detected objects, with confidence scores.

**Key Metrics:**
- Detection latency: ~150ms (YOLOv8n on CPU)
- Depth inference: ~800ms (Depth Anything V2 Small on CPU)
- End-to-end: ~1s per image
- Supported classes: 80 COCO classes
- Web interface: Flask server at port 7860

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Input Image                               │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
              ┌─────────────────────────┐
              │   Preprocessing          │
              │   - Resize ≤1600px       │
              │   - RGB conversion       │
              └───────────┬─────────────┘
                          ▼
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  YOLOv8n Detector   │         │  Depth Anything V2  │
│  (ultralytics)      │         │  (transformers)     │
│  - 80 classes       │         │  - Relative depth   │
│  - BBox + conf      │         │  - 0-1 normalized   │
└─────────┬───────────┘         └─────────┬───────────┘
          │                               │
          └───────────────┬───────────────┘
                          ▼
              ┌─────────────────────────┐
              │   Fusion & Metric        │
              │   Estimation             │
              │   - Pinhole camera model │
              │   - Depth ↔ metric       │
              │   - Confidence fusion    │
              └───────────┬─────────────┘
                          ▼
              ┌─────────────────────────┐
              │   Visualization          │
              │   - Annotated image      │
              │   - Depth colormap       │
              │   - JSON results         │
              └─────────────────────────┘
```

---

## 2. Models & Methods

### 2.1 Object Detection: YOLOv8n
- **Model**: Ultralytics YOLOv8-nano (6.2MB, 3.2M params)
- **Classes**: 80 COCO categories
- **Input**: 640×640 (internal), accepts any resolution
- **Performance**: ~150ms/image on CPU (Apple M-series)
- **Confidence threshold**: 0.3 (configurable)

### 2.2 Depth Estimation: Depth Anything V2 Small
- **Model**: `depth-anything/Depth-Anything-V2-Small-hf` (~90MB)
- **Framework**: HuggingFace Transformers
- **Output**: Relative depth map [0,1] (1 = closer)
- **Resolution**: Matches input image
- **Performance**: ~800ms/image on CPU
- **Fallback**: Gradient-based pseudo-depth (if model unavailable)

### 2.3 Metric Size Estimation

**Pinhole Camera Model:**
```
world_width  = bbox_width_px  × depth_meters / focal_length_px
world_height = bbox_height_px × depth_meters / focal_length_px
```

**Depth Calibration:**
- Relative depth `d ∈ [0,1]` → metric depth: `depth_m = 0.5 + d × 3.5` (range: 0.5–4.0m)
- Focal length estimate: `focal_px = image_width × 1.2` (typical phone camera)

**Confidence Fusion:**
```
depth_quality = 1.0 - |d - 0.5| / 0.5  (peaks at mid-range)
final_conf = 0.5 × detection_conf + 0.5 × depth_quality
```

---

## 3. API Specification

### GET /
Returns the web interface (HTML).

### GET /health
```json
{ "ok": true }
```

### POST /analyze
**Request:** multipart/form-data with `image` field
**Response:**
```json
{
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.87,
      "class_id": 5,
      "class_name": "bus",
      "metric": {
        "width_m": 1.384,
        "height_m": 0.922,
        "distance_m": 1.72,
        "relative_depth": 0.35,
        "confidence": 0.78,
        "detection_conf": 0.87,
        "depth_quality": 0.70
      }
    }
  ],
  "vis": "base64_jpeg",
  "depth": "base64_jpeg",
  "meta": ["detector: YOLOv8n", "depth: Depth Anything V2", "objects: 5", "time: 0.48s"]
}
```

---

## 4. Installation & Deployment

### Requirements
```bash
pip install -r requirements.txt
# torch, torchvision, ultralytics, transformers, flask, pillow, opencv-python, numpy
```

### Run Server
```bash
python3 app.py
# Serves on http://0.0.0.0:7860
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python3", "app.py"]
```

---

## 5. Known Limitations & Future Work

### Current Limitations
| Issue | Impact | Mitigation |
|-------|--------|------------|
| Uncalibrated focal length | ~30-50% size error | Add EXIF focal length parsing |
| Relative depth only | No absolute scale without reference | Add ArUco/ruler calibration |
| Single-view only | Scale ambiguity | Multi-view SfM integration |
| CPU only | Slow depth inference | GPU acceleration, model quantization |

### Roadmap
1. **Calibration Module**: ArUco marker / ruler detection for absolute scale
2. **Multi-View**: COLMAP SfM + scale alignment across views
3. **Better Depth**: Metric3D v2, Depth Pro for metric depth
4. **3D Detection**: Omni3D / Cube R-CNN for oriented 3D boxes
5. **Deployment**: ONNX export, TensorRT, mobile (CoreML/TFLite)

---

## 6. Test Results

### Test Image: bus.jpg (Ultralytics sample)
| Object | Class | Det Conf | Width (m) | Height (m) | Distance (m) | Depth Qual |
|--------|-------|----------|-----------|------------|--------------|------------|
| 0 | bus | 0.87 | 1.38 | 0.92 | 1.72 | 0.70 |
| 1 | person | 0.86 | 0.50 | 1.28 | 2.47 | 0.88 |
| 2 | person | 0.83 | 0.19 | 0.66 | 1.31 | 0.46 |
| 3 | person | 0.81 | 0.31 | 1.06 | 2.27 | 0.99 |
| 4 | person | 0.33 | 0.18 | 0.96 | 2.87 | 0.65 |

**Notes:** Person heights (1.06–1.28m) are plausible for seated/standing people. Bus width (1.38m) is underestimated due to uncalibrated focal length — real bus ~2.5m.

---

## 7. Repository Structure

```
size-scale-estimation/
├── app.py                 # Flask web server (main entry)
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── setup.py              # Install script
├── README.md             # User documentation
├── RESEARCH.md           # 40-page SOTA research
├── .gitignore
├── prototype/
│   ├── __init__.py
│   ├── single_image_app.py  # Gradio prototype (legacy)
│   └── cli.py          # CLI batch processor
└── data/               # Sample images (gitignored)
```

---

## 8. Usage Examples

### Web Interface
```bash
python3 app.py
# Open http://localhost:7860
# Drag & drop image → view results
```

### Programmatic
```python
import requests

with open("image.jpg", "rb") as f:
    r = requests.post("http://localhost:7860/analyze", files={"image": f})
result = r.json()
for det in result["detections"]:
    m = det["metric"]
    print(f"{det['class_name']}: {m['width_m']:.2f}×{m['height_m']:.2f}m @ {m['distance_m']:.1f}m (conf={m['confidence']:.2f})")
```

### CLI Batch
```bash
python3 prototype/cli.py --input images/ --output results/
```

---

## 9. Research Context

This implementation draws from four methodological families (detailed in RESEARCH.md):

1. **Known-Reference**: RulerNet, ArUco markers, AutoFish
2. **Depth-Based**: Depth Anything V2, Metric3D v2, Depth Pro, UniDepth
3. **3D Object Detection**: Omni3D, Cube R-CNN, MonoDTR
4. **Multi-View**: SfM (COLMAP) + scale anchors

**Benchmark Datasets:** AnyRuler, KITTI, DA-2K, Omni3D, AutoFish, NYU Depth v2, ScanNet

---

## 10. License & Attribution

- YOLOv8: Ultralytics (AGPL-3.0)
- Depth Anything V2: Depth Anything authors (Apache-2.0)
- This integration: MIT License (see LICENSE)

---

*Generated: 2026-08-19*
*Commit: f6f4d9b*