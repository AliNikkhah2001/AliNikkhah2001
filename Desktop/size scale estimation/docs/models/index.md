---
layout: default
title: "Models | Scale Estimation Review"
description: "Detailed model cards for key scale estimation models"
---

# Model Zoo

## Depth Estimation Models

### Depth Anything V2 <span class="badge badge-relative">Relative</span>

| Property | Value |
|----------|-------|
| **Venue** | NeurIPS 2024 |
| **Authors** | Yang et al. (HKU, TikTok) |
| **Scales** | Small (24M), Base (97M), Large (335M), Giant (1.3B) |
| **Backbone** | DINOv2 (ViT-S/B/L/G) + DPT decoder |
| **Training** | 595K synthetic → 62M pseudo-labeled real |
| **Input** | Any resolution |
| **Output** | Relative depth [0,1], same resolution |
| **Speed (V100)** | ~30ms (Small), ~120ms (Large) |
| **License** | Apache-2.0 (Small/Base), CC-BY-NC-4.0 (Large/Giant) |
| **GitHub** | [DepthAnything/Depth-Anything-V2](https://github.com/DepthAnything/Depth-Anything-V2) |
| **HF** | `depth-anything/Depth-Anything-V2-Small-hf` |

**Key insight:** Replaced real labeled data with synthetic pre-training. Better boundaries than V1.

```python
from transformers import pipeline
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
depth = pipe(image)["depth"]  # PIL Image, relative [0,1]
```

---

### Metric3D v2 <span class="badge badge-metric">Metric</span>

| Property | Value |
|----------|-------|
| **Venue** | TPAMI 2024 (ICCV 2023 for v1) |
| **Authors** | Hu, Yin et al. (HKUST, Shanghai AI Lab) |
| **Scales** | ViT-S, ViT-L, ViT-Giant2 |
| **Backbone** | DINOv2-reg + RAFT decoder |
| **Output** | Metric depth (m) + surface normals + focal length |
| **Zero-shot** | ✅ No fine-tuning needed |
| **Champion** | CVPR 2023 Monocular Depth Estimation Challenge |
| **GitHub** | [YvanYin/Metric3D](https://github.com/YvanYin/Metric3D) |
| **PyTorch Hub** | `torch.hub.load('yvanyin/metric3d', 'metric3d_vit_small')` |

**Key insight:** Canonical camera space normalization enables zero-shot metric prediction across datasets.

```python
import torch
model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_small', pretrain=True)
pred_depth, confidence, output_dict = model.inference({'input': rgb, 'focal_length': f})
# pred_depth in meters
```

---

### Depth Pro <span class="badge badge-metric">Metric</span>

| Property | Value |
|----------|-------|
| **Venue** | ICLR 2025 |
| **Authors** | Bochkovskii et al. (Apple) |
| **Architecture** | Multi-scale ViT (MP-Encoder) |
| **Output** | Metric depth + **predicted focal length** |
| **Resolution** | Up to 2.25 MP (1536×1536) |
| **Speed** | 0.3s on V100 (2.25 MP) |
| **Boundary F1** | SOTA on DIS-5K, AM-2K |
| **GitHub** | [apple/ml-depth-pro](https://github.com/apple/ml-depth-pro) |
| **HF** | `apple/DepthPro-hf` |

**Key insight:** First model to predict focal length accurately from single image + metric depth simultaneously.

```python
import depth_pro
model, transform = depth_pro.create_model_and_transforms()
image, _, f_px = depth_pro.load_rgb("image.jpg")
pred = model.infer(transform(image), f_px=f_px)
depth_m = pred["depth"]       # Metric depth
focal_px = pred["focallength_px"]  # Predicted focal length
```

---

### UniDepth <span class="badge badge-metric">Metric</span> <span class="badge badge-relative">Relative</span>

| Property | Value |
|----------|-------|
| **Venue** | CVPR 2024 |
| **Authors** | Piccinelli et al. (ETH Zürich) |
| **Output** | Metric depth + relative depth + camera intrinsics |
| **Backbone** | DINOv2 + custom heads |
| **Universal** | Single model for all scenarios |
| **GitHub** | [lpiccinelli-eth/UniDepth](https://github.com/lpiccinelli-eth/UniDepth) |

---

### ZoeDepth <span class="badge badge-metric">Metric</span>

| Property | Value |
|----------|-------|
| **Venue** | CVPR 2023 |
| **Authors** | Bhat et al. (ETH Zürich) |
| **Approach** | Relative + metric fusion |
| **Models** | ZoeD_N (indoor), ZoeD_K (outdoor), ZoeD_NK (both) |
| **GitHub** | [isl-org/ZoeDepth](https://github.com/isl-org/ZoeDepth) |

---

### MiDaS v3 / DPT <span class="badge badge-relative">Relative</span>

| Property | Value |
|----------|-------|
| **Venue** | ICCV 2021 |
| **Authors** | Ranftl et al. (Intel ISL) |
| **Scales** | Small (MiDaS), Large (DPT-Hybrid) |
| **Training** | Multi-dataset with scale-invariant loss |
| **GitHub** | [isl-org/MiDaS](https://github.com/isl-org/MiDaS) |

---

## 3D Object Detection Models

### Cube R-CNN (Omni3D) <span class="badge badge-3d">3D Detection</span>

| Property | Value |
|----------|-------|
| **Venue** | CVPR 2023 |
| **Authors** | Brazil et al. (Meta AI) |
| **Categories** | 98 (unified across 6 datasets) |
| **Backbone** | DLA-34 / ResNet-50 / Swin-T (Detectron2) |
| **Output** | Oriented 3D boxes: (x,y,z,w,h,l,θ) + 2D bbox + class |
| **Key innovation** | Virtual camera space (normalizes varying intrinsics) |
| **GitHub** | [facebookresearch/omni3d](https://github.com/facebookresearch/omni3d) |

**Virtual camera:** All predictions made in normalized space, then transformed to target camera.

---

### Driving-Specific (KITTI/nuScenes)

| Model | Venue | Categories | Key Feature |
|-------|-------|------------|-------------|
| **MonoFlex** | CVPR 2021 | 3 | Decoupled truncation |
| **MonoDTR** | CVPR 2022 | 3 | Transformer decoder |
| **PGD** | CVPR 2022 | 3 | Geometric reasoning |
| **GUPNet** | CVPR 2021 | 3 | Uncertainty estimation |
| **ImVoxelNet** | CVPR 2022 | 3 | Voxel-based |

---

## Known-Reference Models

### AnyRuler <span class="badge badge-reference">Reference</span>

| Property | Value |
|----------|-------|
| **Venue** | CVPR 2024 |
| **Authors** | Alibaba |
| **Task** | Detect ruler/tape measure keypoints → pixel/mm |
| **Generalization** | Works on arbitrary rulers, tapes, scales |
| **GitHub** | [alibaba/AnyRuler](https://github.com/alibaba/AnyRuler) |

### RulerNet <span class="badge badge-reference">Reference</span>

| Property | Value |
|----------|-------|
| **Venue** | CVPR 2024 |
| **Approach** | Keypoint-based ruler detection |
| **Application** | Metric scale recovery in the wild |

### ArUco / AprilTag (OpenCV) <span class="badge badge-reference">Reference</span>

| Property | Value |
|----------|-------|
| **Library** | OpenCV contrib (`cv2.aruco`) |
| **Markers** | Predefined dictionaries (4×4 to 7×7) |
| **Output** | 6DoF pose + intrinsic calibration |
| **Accuracy** | Sub-millimeter with good detection |

---

## Multi-View

### COLMAP

| Property | Value |
|----------|-------|
| **Type** | SfM + MVS pipeline |
| **Features** | SIFT, SuperPoint, LoFTR, DISK |
| **Scale anchor** | Known object, GPS, IMU, plane |
| **Output** | Sparse/dense point cloud, mesh, camera poses |
| **Python** | `pip install pycolmap` / `pycolmap-cuda12` |
| **GitHub** | [colmap/colmap](https://github.com/colmap/colmap) |

---

## Model Selection Guide

| Need | Recommended |
|------|-------------|
| **Fastest relative depth** | Depth Anything V2 Small (30ms) |
| **Best metric depth (zero-shot)** | Metric3D v2 Giant / Depth Pro |
| **Best boundary sharpness** | Depth Pro |
| **Need focal length too** | Depth Pro / Metric3D v2 / UniDepth |
| **3D boxes for known categories** | Cube R-CNN (Omni3D) |
| **Exact scale, controlled env** | ArUco + any depth |
| **Mobile deployment** | Depth Anything V2 Small (ONNX/CoreML) |
| **Multi-view reconstruction** | COLMAP + pycolmap |

---

## Export Formats

| Model | ONNX | TensorRT | CoreML | TFLite |
|-------|------|----------|--------|--------|
| Depth Anything V2 | ✅ | ✅ | ✅ | ✅ |
| Metric3D v2 | ✅ | ✅ | ❌ | ❌ |
| Depth Pro | ❌ | ❌ | ❌ | ❌ |
| Cube R-CNN | ✅ (Detectron2) | ✅ | ❌ | ❌ |
| YOLOv8 | ✅ | ✅ | ✅ | ✅ |