---
layout: default
title: "Datasets | Scale Estimation Review"
description: "Comprehensive list of benchmark datasets for scale and size estimation"
---

# Benchmark Datasets

## Depth Estimation Datasets

### Indoor RGB-D

| Dataset | Images | Resolution | Sensor | Metric | License |
|---------|--------|------------|--------|--------|---------|
| **NYU Depth v2** | 1,449 | 640×480 | Kinect v1 | ✅ | Non-commercial |
| **ScanNet** | 2.5M frames | 1296×968 | Structure Sensor | ✅ | Academic |
| **SUN RGB-D** | 10,335 | 640×480 | Kinect v1/v2, Xtion | ✅ | Academic |
| **IBIMS-1** | 100 | 640×480 | FARO Laser | ✅ | Research |
| **Redwood** | 3,900 | 640×480 | Kinect v2 | ✅ | Academic |

### Outdoor / Driving

| Dataset | Images | Resolution | Sensor | Metric | Domain |
|---------|--------|------------|--------|--------|--------|
| **KITTI Depth** | 93K | 1242×375 | Velodyne 64-beam | ✅ | Driving |
| **KITTI 3D** | 7,481 | 1242×375 | Velodyne + labels | ✅ | 3D Detection |
| **nuScenes** | 40K | 1600×900 | 32-beam LiDAR | ✅ | Driving |
| **DDAD** | 12.5K | 1920×1208 | 64-beam LiDAR | ✅ | Driving |
| **Waymo Open** | 230K | 1920×1280 | 64-beam LiDAR | ✅ | Driving |

### Synthetic

| Dataset | Images | Resolution | Metric | Domain |
|---------|--------|------------|--------|--------|
| **Hypersim** | 77K | 1024×768 | ✅ | Indoor |
| **Virtual KITTI 2** | 21K | 1242×375 | ✅ | Driving |
| **ARKitScenes** | 5K+ | 1920×1440 | ✅ | Indoor/AR |
| **Objectron** | 15K | 1280×720 | ✅ | Object-centric |
| **BlendedMVS** | 17K | 768×576 | ✅ | General |
| **Tanks & Temples** | — | — | ✅ | SfM benchmark |

### General Purpose (Zero-shot Evaluation)

| Dataset | Type | Images | Notes |
|---------|------|--------|-------|
| **DA-2K** | Sparse depth | 2,000 | Depth Anything benchmark |
| **Omni3D** | Multi-source | 234K | 6 datasets unified |
| **WildCross** | Mixed | — | Cross-modal benchmark |
| **DIODE** | Sparse | 25K | Indoor + outdoor |

---

## 3D Object Detection Datasets

### Unified Benchmarks

| Dataset | Categories | 3D Boxes | Images | Source Datasets |
|---------|------------|----------|--------|-----------------|
| **Omni3D** | 98 | 3M | 234K | SUN RGB-D, ARKit, Hypersim, KITTI, nuScenes, Objectron |
| **Omni3D-Indoor** | 70 | — | — | SUN RGB-D, ARKit, Hypersim |
| **Omni3D-Outdoor** | 28 | — | — | KITTI, nuScenes |

### Domain-Specific

| Dataset | Categories | 3D Boxes | Domain |
|---------|------------|----------|--------|
| **KITTI 3D** | 8 (car, pedestrian, cyclist, etc.) | 200K | Driving |
| **nuScenes 3D** | 23 | 1.4M | Driving |
| **SUN RGB-D** | 37 | ~50K | Indoor |
| **ARKitScenes** | 18 | 100K+ | Indoor/AR |
| **Objectron** | 9 (bike, book, bottle, camera, cereal box, chair, cup, laptop, shoe) | 15K | Object-centric |
| **Waymo 3D** | 5 | 12M | Driving |

---

## Known-Reference Datasets

| Dataset | Reference Type | Images | Use Case |
|---------|---------------|--------|----------|
| **AnyRuler** | Rulers, tapes, scales | 10K+ | Ruler detection |
| **AutoFish** | Fish (known length) | 10K+ | Aquaculture |
| **Pascal VOC + Synthetic Rulers** | Simulated rulers | 20K | Benchmark |
| **Custom** | ArUco/AprilTag | Any | Calibration |

---

## Multi-View / SfM Datasets

| Dataset | Images | Type | Use |
|---------|--------|------|-----|
| **Tanks & Temples** | — | Real | SfM/MVS benchmark |
| **ETH3D** | — | Real | High-accuracy SfM |
| **DTU** | 80+ | Structured light | MVS benchmark |
| **Replica** | 18 scenes | Synthetic | Indoor reconstruction |
| **Scannet++** | 1,450 scans | Real | 3D reconstruction |
| **MegaDepth** | 1M+ | Internet photos | SfM + depth |
| **Aachen Day-Night** | 6K | Real | Localization |

---

## Dataset Access

### Direct Downloads

```bash
# KITTI
wget https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_image_2.zip
wget https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_velodyne.zip

# NYU Depth v2
wget http://horatio.cs.nyu.edu/mit/silberman/nyu_depth_v2/nyu_depth_v2_labeled.mat

# ScanNet (requires agreement)
# http://www.scan-net.org/

# Hypersim
# https://github.com/apple/ml-hypersim

# DA-2K (Depth Anything)
# https://huggingface.co/datasets/depth-anything/DA-2K
```

### HuggingFace Datasets

```python
from datasets import load_dataset

# DA-2K
ds = load_dataset("depth-anything/DA-2K")

# Omni3D (via detectron2)
# Requires detectron2 dataset registration

# NYU Depth v2
ds = load_dataset("nyu_depth_v2")

# KITTI
ds = load_dataset("kitti")
```

### PyTorch Datasets

```python
import torchvision.datasets as datasets

# NYU Depth v2 (torchvision)
nyu = datasets.NYUDepthV2(root="./data", download=True)

# KITTI (torchvision)
kitti = datasets.KITTI(root="./data", train=True, download=True)
```

---

## Dataset Statistics Summary

| Dataset | Year | Total Images | Annotations | Modalities | Metric |
|---------|------|--------------|-------------|------------|--------|
| NYU Depth v2 | 2012 | 1,449 | Dense depth | RGB-D | ✅ |
| KITTI | 2012 | 93K | Sparse LiDAR + 3D boxes | RGB + LiDAR | ✅ |
| ScanNet | 2017 | 2.5M | Dense depth + 3D boxes | RGB-D | ✅ |
| SUN RGB-D | 2015 | 10K | 3D boxes | RGB-D | ✅ |
| nuScenes | 2019 | 40K | 3D boxes + LiDAR | RGB + LiDAR + Radar | ✅ |
| Hypersim | 2021 | 77K | Dense depth + normals | Synthetic RGB-D | ✅ |
| Omni3D | 2023 | 234K | 3M 3D boxes | Multi-source | ✅ |
| DA-2K | 2024 | 2K | Sparse depth | RGB + sparse depth | ✅ |
| AutoFish | 2023 | 10K | Fish length | RGB + keypoints | ✅ |
| AnyRuler | 2024 | 10K+ | Ruler keypoints | RGB + keypoints | ✅ |

---

## Choosing a Dataset

| For Training... | Use |
|-----------------|-----|
| Relative depth (general) | DA-2K + Hypersim + ScanNet |
| Metric depth (indoor) | NYU Depth v2 + ScanNet + Hypersim |
| Metric depth (outdoor) | KITTI + DDAD + nuScenes |
| Metric depth (zero-shot) | Omni3D (mixed) |
| 3D detection (general) | Omni3D |
| 3D detection (driving) | KITTI / nuScenes / Waymo |
| 3D detection (indoor) | SUN RGB-D / ARKitScenes / ScanNet |
| Ruler detection | AnyRuler |
| SfM/MVS | Tanks & Temples / ETH3D / DTU |

---

## Evaluation Protocols

### Depth (Standard)

```python
# Standard metrics (lower better)
abs_rel = np.mean(np.abs(pred - gt) / gt)
rmse = np.sqrt(np.mean((pred - gt)**2))
log10 = np.mean(np.abs(np.log10(pred) - np.log10(gt)))

# Threshold accuracy (higher better)
delta1 = np.mean(np.maximum(pred/gt, gt/pred) < 1.25)
delta2 = np.mean(np.maximum(pred/gt, gt/pred) < 1.25**2)
delta3 = np.mean(np.maximum(pred/gt, gt/pred) < 1.25**3)
```

### 3D Detection (Omni3D)

```python
# IoU_3D (from PyTorch3D)
from pytorch3d.ops import box3d_overlap
iou3d = box3d_overlap(pred_corners, gt_corners).iou

# AP_3D at IoU threshold (typically 0.25 for Omni3D)
ap3d = compute_ap(iou3d, scores, threshold=0.25)
```

### Size Estimation (Proposed)

```
Relative Error = |W_pred - W_gt| / W_gt
Volume IoU = Intersection_3D / Union_3D
```

---

## Data Licenses

| Dataset | License | Commercial Use |
|---------|---------|----------------|
| NYU Depth v2 | Custom | ❌ |
| KITTI | Custom | ❌ (request) |
| ScanNet | Custom | ❌ |
| nuScenes | CC BY-NC-SA 4.0 | ❌ |
| Hypersim | Custom (Apple) | ❌ |
| Omni3D | CC BY-NC 4.0 | ❌ |
| DA-2K | Apache-2.0 | ✅ |
| AutoFish | Custom | ❌ |
| AnyRuler | Custom | ❌ |
| Tanks & Temples | Custom | ❌ |
| ETH3D | Custom | ❌ |