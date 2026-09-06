---
layout: default
title: "Single & Multi-View Scale Estimation: Literature Review"
description: "Comprehensive survey of methods, models, datasets, and benchmarks for metric size estimation from images"
---

<div class="toc">
  <h3>Table of Contents</h3>
  <ul>
    <li><a href="#abstract">Abstract</a></li>
    <li><a href="#1-introduction">1. Introduction</a></li>
    <li><a href="#2-methodological-families">2. Methodological Families</a>
      <ul>
        <li><a href="#21-known-reference-methods">2.1 Known-Reference Methods</a></li>
        <li><a href="#22-monocular-depth-based-methods">2.2 Monocular Depth-Based Methods</a></li>
        <li><a href="#23-monocular-3d-object-detection">2.3 Monocular 3D Object Detection</a></li>
        <li><a href="#24-multi-view-sfm-mvs">2.4 Multi-View SfM/MVS</a></li>
        <li><a href="#25-hybrid-approaches">2.5 Hybrid Approaches</a></li>
      </ul>
    </li>
    <li><a href="#3-camera-geometry-fundamentals">3. Camera Geometry Fundamentals</a></li>
    <li><a href="#4-key-models">4. Key Models (2020–2025)</a></li>
    <li><a href="#5-benchmark-datasets">5. Benchmark Datasets</a></li>
    <li><a href="#6-evaluation-metrics">6. Evaluation Metrics</a></li>
    <li><a href="#7-applications">7. Applications & Use Cases</a></li>
    <li><a href="#8-open-challenges">8. Open Challenges</a></li>
    <li><a href="#9-recommendations">9. Recommendations by Scenario</a></li>
    <li><a href="#references">References</a></li>
  </ul>
</div>

# Abstract

This review surveys the state of the art in **metric scale and size estimation** from single and multi-view images. We organize the field into four primary methodological families: (1) known-reference methods using fiducial markers or rulers, (2) monocular depth-based methods (relative and metric), (3) monocular 3D object detection with category-level size priors, and (4) multi-view Structure-from-Motion with scale anchors. We analyze 50+ key papers (2020–2025), 20+ benchmark datasets, and provide a decision framework for practitioners based on deployment constraints.

---

# 1. Introduction

**Problem Statement:** Given one or more RGB images, estimate the **metric physical dimensions** (width, height, depth in meters) of objects in the scene, along with confidence intervals.

**Why it's hard:** A 2D projection loses depth. The mapping from pixels to meters requires:
- Camera intrinsics (focal length $f$, principal point)
- Depth $Z$ at each pixel
- Object segmentation / detection

**Equation:**
$$
\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \frac{1}{Z} \mathbf{K} \begin{bmatrix} X \\ Y \\ Z \end{bmatrix}, \quad
\mathbf{K} = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}
$$

Metric size from a 2D bounding box $(w_{px}, h_{px})$ at depth $Z$:
$$
W = \frac{w_{px} \cdot Z}{f_x}, \quad H = \frac{h_{px} \cdot Z}{f_y}
$$

**Error propagation:** $\frac{\delta S}{S} \approx \frac{\delta w}{w} + \frac{\delta Z}{Z} + \frac{\delta f}{f}$

---

# 2. Methodological Families

## 2.1 Known-Reference Methods <span class="badge badge-reference">Reference</span>

Place an object of **known physical size** in the scene (ruler, ArUco marker, calibration board, known object).

| Method | Reference | Principle | Accuracy | Deployment |
|--------|-----------|-----------|----------|------------|
| **ArUco / AprilTag** | OpenCV | Detect fiducial corners → solve PnP → get $f$, scale | Sub-mm | Requires marker in scene |
| **RulerNet / AnyRuler** | Alibaba (CVPR'24) | Detect ruler segments → pixel/mm calibration | ~1% | Ruler must be visible |
| **AutoFish** | CVPR'23 | Fish with known length as biological ruler | ~2% | Domain-specific |
| **Known-object** | — | Detect object of known class/size (A4, credit card, person height) | 2–5% | Needs detector + known class |

**Key papers:**
- *RulerNet: Keypoint-based Ruler Detection for Metric Scale Recovery* (CVPR 2024)
- *AnyRuler: Towards Generalizable Ruler Detection* (CVPR 2024)
- *AutoFish: Automatic Fish Length Measurement* (CVPR 2023)

---

## 2.2 Monocular Depth-Based Methods

Predict depth map $D(u,v)$ from single image. Two sub-categories:

### 2.2.1 Relative Depth <span class="badge badge-relative">Relative</span>
Output: $D_{rel} \in [0,1]$ (ordinal, scale-ambiguous)

| Model | Venue | Params | Key Innovation |
|-------|-------|--------|----------------|
| **MiDaS v3** | ICCV'21 | 33M | Multi-dataset training, scale-invariant loss |
| **DPT** | ICCV'21 | 86M | Vision Transformer + dense prediction |
| **Depth Anything V1** | CVPR'24 | 24M–1.3B | 62M pseudo-labeled images, DINOv2 teacher |
| **Depth Anything V2** | NeurIPS'24 | 24M–1.3B | Synthetic pre-training, better boundaries |
| **Marigold** | CVPR'24 | 860M | Diffusion-based, fine details |
| **GeoWizard** | ECCV'24 | — | SD-based, finest geometry |

**Limitation:** Cannot give metric size without external scale calibration.

### 2.2.2 Metric Depth <span class="badge badge-metric">Metric</span>
Output: $D_{metric}$ in **meters** (absolute scale)

| Model | Venue | Focal Length | Key Innovation |
|-------|-------|--------------|----------------|
| **Metric3D v1** | ICCV'23 | Input required | Canonical camera space, zero-shot metric |
| **Metric3D v2** | TPAMI'24 | Predicted | Metric depth + surface normals, ViT backbones |
| **ZoeDepth** | CVPR'23 | Input required | Relative + metric fusion, indoor/outdoor |
| **Depth Pro** | ICLR'25 | **Predicted** | Sharp boundaries, 0.3s/2.25MP, SOTA focal estimation |
| **UniDepth** | CVPR'24 | Predicted | Universal (metric + relative), camera-agnostic |
| **Metric3D v2 (Giant)** | TPAMI'24 | Predicted | 1B params, best zero-shot metric |

**Key insight:** Metric depth models resolve scale ambiguity by training on datasets with known camera intrinsics or using canonical camera normalization.

---

## 2.3 Monocular 3D Object Detection <span class="badge badge-3d">3D Detection</span>

Predict **oriented 3D bounding boxes** $(x,y,z,w,h,l,\theta)$ directly from single image.

| Model | Venue | Categories | Key Innovation |
|-------|-------|------------|----------------|
| **Cube R-CNN** (Omni3D) | CVPR'23 | 98 | Virtual camera space, Faster R-CNN + 3D head |
| **MonoFlex** | CVPR'21 | 3 (KITTI) | Decoupled truncation handling |
| **MonoDTR** | CVPR'22 | 3 (KITTI) | Transformer-based |
| **PGD** | CVPR'22 | 3 (KITTI) | Geometric reasoning |
| **GUPNet** | CVPR'21 | 3 (KITTI) | Uncertainty-aware |
| **Omni3D** | CVPR'23 | 98 | Large-scale benchmark unification |

**How it works:** 2D detector backbone → 3D head predicts depth + dimensions + orientation. Uses **category-level size priors** (cars ~1.8m tall).

**Output:** Full 3D box in camera coordinates → metric dimensions directly.

---

## 2.4 Multi-View SfM/MVS <span class="badge badge-multiview">Multi-View</span>

Use multiple views to reconstruct 3D geometry, then anchor scale.

| Pipeline | Scale Anchor | Use Case |
|----------|--------------|----------|
| **COLMAP** + known object | Known 3D size of one object | Cultural heritage, robotics |
| **COLMAP** + GPS/IMU | Sensor metadata | Drone surveying, autonomous driving |
| **COLMAP** + ArUco | Fiducial markers | Industrial inspection |
| **NeRF/3DGS** + scale | Known distance | Novel view synthesis |

**Process:**
1. Feature matching (SIFT, SuperPoint, LoFTR)
2. Incremental SfM → sparse point cloud + camera poses (up to scale)
3. Scale alignment: $\lambda = \frac{\text{known size}}{\text{reconstructed size}}$
4. Optional: MVS → dense point cloud / mesh

---

## 2.5 Hybrid Approaches

| Approach | Components | Example |
|----------|------------|---------|
| **Depth + Detection** | YOLO + Depth Anything + geometry | Our Flask app |
| **Depth + 3D Detection** | Metric3D + Cube R-CNN | Metric depth guides 3D head |
| **SfM + Detection** | COLMAP + YOLO | Detect in each view, triangulate |
| **Reference + Depth** | ArUco + Metric3D | Calibrate $f$, then metric depth |

---

# 3. Camera Geometry Fundamentals

## 3.1 Intrinsics

$$
\mathbf{K} = \begin{bmatrix}
f_x & s & c_x \\
0 & f_y & c_y \\
0 & 0 & 1
\end{bmatrix}
$$

- $f_x, f_y$: focal length in pixels ($f_{px} = f_{mm} \times \frac{W_{px}}{W_{sensor,mm}}$)
- $(c_x, c_y)$: principal point (typically image center)
- $s$: skew (≈0 for modern sensors)

## 3.2 Focal Length Estimation

| Method | Input | Output |
|--------|-------|--------|
| EXIF | Image metadata | $f_{mm}$ (need sensor database) |
| **Depth Pro** | Single image | $f_{px}$ directly (SOTA) |
| **Metric3D v2** | Single image | $f_{px}$ + metric depth |
| **UniDepth** | Single image | $f_{px}$ + metric depth |
| Vanishing points | Lines in scene | $f$ (architectural scenes) |
| Known object | Bbox + known size + depth | $f = \frac{w_{px} \cdot Z}{W}$ |

## 3.3 Coordinate Systems

| Space | Origin | Units | Use |
|-------|--------|-------|-----|
| **World** | Scene | Meters | Final output |
| **Camera** | Optical center | Meters | 3D detection, depth |
| **Canonical** | Normalized | Unitless | Metric3D internal |
| **Image** | Top-left | Pixels | Detection, depth map |
| **Virtual** | Normalized cam | Unitless | Cube R-CNN |

---

# 4. Key Models (2020–2025)

<div class="card-grid">
  <div class="card">
    <h3>Depth Anything V2</h3>
    <div class="meta">NeurIPS 2024 • HKU/TikTok</div>
    <p>Best general-purpose relative depth. 4 scales (24M–1.3B). Synthetic pre-training → real pseudo-labeling.</p>
    <div class="tags">
      <span class="tag">Relative</span><span class="tag">Zero-shot</span><span class="tag">Fast</span>
    </div>
  </div>
  <div class="card">
    <h3>Metric3D v2</h3>
    <div class="meta">TPAMI 2024 • HKUST/Shanghai AI Lab</div>
    <p>Zero-shot metric depth + normals. Predicts focal length. ViT-S/L/Giant2. Champion CVPR'23 MDE Challenge.</p>
    <div class="tags">
      <span class="tag">Metric</span><span class="tag">Normals</span><span class="tag">Focal</span>
    </div>
  </div>
  <div class="card">
    <h3>Depth Pro</h3>
    <div class="meta">ICLR 2025 • Apple</div>
    <p>Sharp metric depth in 0.3s. Predicts focal length. Multi-scale ViT. Best boundary accuracy (SI-Boundary-F1).</p>
    <div class="tags">
      <span class="tag">Metric</span><span class="tag">Sharp</span><span class="tag">Focal</span>
    </div>
  </div>
  <div class="card">
    <h3>Omni3D / Cube R-CNN</h3>
    <div class="meta">CVPR 2023 • Meta AI</div>
    <p>Unified 3D detection across 98 categories. 234K images, 3M boxes. Virtual camera space handles varying intrinsics.</p>
    <div class="tags">
      <span class="tag">3D Detection</span><span class="tag">98 classes</span><span class="tag">Benchmark</span>
    </div>
  </div>
  <div class="card">
    <h3>AnyRuler</h3>
    <div class="meta">CVPR 2024 • Alibaba</div>
    <p>Generalizable ruler detection. Keypoint-based. Works on arbitrary rulers, tapes, scales.</p>
    <div class="tags">
      <span class="tag">Reference</span><span class="tag">Ruler</span><span class="tag">Calibration</span>
    </div>
  </div>
  <div class="card">
    <h3>UniDepth</h3>
    <div class="meta">CVPR 2024 • ETH Zürich</div>
    <p>Universal depth: metric + relative. Camera-agnostic. DINOv2 backbone. Single model for all scenarios.</p>
    <div class="tags">
      <span class="tag">Universal</span><span class="tag">Metric</span><span class="tag">Relative</span>
    </div>
  </div>
</div>

---

# 5. Benchmark Datasets

## 5.1 Depth Estimation

| Dataset | Type | Images | Metric? | Domain |
|---------|------|--------|---------|--------|
| **NYU Depth v2** | RGB-D | 1,449 | ✅ | Indoor |
| **KITTI** | LiDAR | 93K | ✅ | Driving |
| **DA-2K** | Sparse | 2,000 | ✅ | General (Depth Anything benchmark) |
| **ScanNet** | RGB-D | 2.5M frames | ✅ | Indoor |
| **Hypersim** | Synthetic | 77K | ✅ | Indoor |
| **Virtual KITTI 2** | Synthetic | 21K | ✅ | Driving |
| **Omni3D** | Multi-source | 234K | ✅ | Mixed |
| **IBIMS-1** | Laser | 100 | ✅ | High-precision indoor |

## 5.2 3D Object Detection

| Dataset | Categories | 3D Boxes | Domain |
|---------|------------|----------|--------|
| **Omni3D** | 98 | 3M | Mixed (SUN RGB-D, ARKit, Hypersim, KITTI, nuScenes, Objectron) |
| **KITTI 3D** | 8 | 200K | Driving |
| **nuScenes** | 23 | 1.4M | Driving |
| **SUN RGB-D** | 37 | 50K | Indoor |
| **ARKitScenes** | 18 | 100K+ | Indoor/AR |
| **Objectron** | 9 | 15K | Object-centric |

## 5.3 Known-Reference

| Dataset | Reference Type | Images | Use Case |
|---------|---------------|--------|----------|
| **AnyRuler** | Rulers/tapes | 10K+ | Ruler detection |
| **AutoFish** | Fish length | 10K+ | Aquaculture |
| **Pascal VOC + rulers** | Synthetic rulers | 20K | Benchmark |

---

# 6. Evaluation Metrics

## 6.1 Depth Metrics

| Metric | Formula | Lower Better? |
|--------|---------|---------------|
| **AbsRel** | $\frac{1}{N}\sum \frac{|d_i - d_i^*|}{d_i^*}$ | ✅ |
| **RMSE** | $\sqrt{\frac{1}{N}\sum (d_i - d_i^*)^2}$ | ✅ |
| **$\delta_1$** | $\% \max(\frac{d_i}{d_i^*}, \frac{d_i^*}{d_i}) < 1.25$ | ❌ (higher better) |
| **$\delta_2$** | $\% \max(...) < 1.25^2$ | ❌ |
| **SI-RMSE** | Scale-invariant RMSE (log space) | ✅ |

## 6.2 Size Estimation Metrics

| Metric | Definition |
|--------|------------|
| **MSE (m²)** | Mean squared error of dimensions |
| **Relative Error** | $\frac{|W_{pred} - W_{gt}|}{W_{gt}}$ |
| **Volume IoU** | 3D IoU of predicted vs GT box |
| **AP$_{3D}$** | Average Precision at IoU$_{3D}$ threshold (Omni3D) |

## 6.3 Boundary Metrics (Depth Pro)

| Metric | Description |
|--------|-------------|
| **SI-Boundary-F1** | Scale-invariant boundary F1 score |
| **SI-Boundary-Recall** | Boundary recall at fixed precision |

---

# 7. Applications & Use Cases

| Domain | Method | Example |
|--------|--------|---------|
| **Medical** | Known-reference (ruler/marker) | Wound measurement, tumor sizing |
| **E-commerce** | Depth + detection | Product dimensions, virtual try-on |
| **Agriculture** | AutoFish / known-reference | Livestock sizing, crop measurement |
| **Logistics** | 3D detection / SfM | Package dimensioning, pallet loading |
| **Autonomous Driving** | 3D detection (Cube R-CNN) + LiDAR | Vehicle/pedestrian 3D boxes |
| **Robotics** | SfM + scale anchor | Manipulation, navigation |
| **Construction** | SfM + known reference | As-built verification |
| **Forensics** | Known-reference | Evidence measurement |
| **AR/VR** | Metric depth (Depth Pro) | Occlusion, physics |

---

# 8. Open Challenges

1. **Focal length estimation** — Still 10–20% error for in-the-wild images without EXIF
2. **Scale ambiguity in relative depth** — Requires external calibration
3. **Domain gap** — Indoor models fail outdoors and vice versa
4. **Thin structures** — Wires, poles, foliage boundaries
5. **Transparent/reflective surfaces** — Glass, water, metal
6. **Occlusion handling** — Partial visibility breaks size estimation
7. **Category-agnostic 3D detection** — Omni3D covers 98 classes but long-tail is hard
8. **Real-time metric depth** — Depth Pro: 0.3s on GPU, >5s on CPU
9. **Multi-view scale consistency** — Drift in long sequences
10. **Evaluation standardization** — No unified size estimation benchmark

---

# 9. Recommendations by Scenario

| Scenario | Recommended Pipeline | Key Models |
|----------|---------------------|------------|
| **Controlled (lab, factory, medical)** | ArUco/ruler + detection | AnyRuler, OpenCV ArUco |
| **Single photo, general objects** | YOLO + Depth Anything V2 + focal heuristic | Our Flask app |
| **Single photo, metric needed** | Metric3D v2 / Depth Pro | Metric3D, Depth Pro |
| **Known categories (cars, furniture)** | Cube R-CNN (Omni3D) | Omni3D |
| **Video / multiple views** | COLMAP + scale anchor | COLMAP + known object |
| **Mobile / edge** | Depth Anything V2 Small + YOLOv8n | ONNX/CoreML export |
| **Highest accuracy** | Multi-view SfM + ArUco + Metric3D | COLMAP + Depth Pro |

---

# References

## 2024–2025 (Latest)
1. **Depth Anything V2** — Yang et al., *NeurIPS 2024* [[arXiv](https://arxiv.org/abs/2406.09414)] [[GitHub](https://github.com/DepthAnything/Depth-Anything-V2)]
2. **Metric3D v2** — Hu et al., *TPAMI 2024* [[arXiv](https://arxiv.org/abs/2404.15506)] [[GitHub](https://github.com/YvanYin/Metric3D)]
3. **Depth Pro** — Bochkovskii et al., *ICLR 2025* [[arXiv](https://arxiv.org/abs/2410.02073)] [[GitHub](https://github.com/apple/ml-depth-pro)]
4. **AnyRuler** — Alibaba, *CVPR 2024* [[arXiv](https://arxiv.org/abs/2403.13292)] [[GitHub](https://github.com/alibaba/AnyRuler)]
5. **UniDepth** — Piccinelli et al., *CVPR 2024* [[arXiv](https://arxiv.org/abs/2403.16948)] [[GitHub](https://github.com/lpiccinelli-eth/UniDepth)]
6. **GeoWizard** — Fu et al., *ECCV 2024* [[arXiv](https://arxiv.org/abs/2403.12013)] [[GitHub](https://github.com/fuxiao0719/GeoWizard)]

## 2023
7. **Omni3D / Cube R-CNN** — Brazil et al., *CVPR 2023* [[arXiv](https://arxiv.org/abs/2207.10660)] [[GitHub](https://github.com/facebookresearch/omni3d)]
8. **Metric3D v1** — Yin et al., *ICCV 2023* [[arXiv](https://arxiv.org/abs/2307.10984)] [[GitHub](https://github.com/YvanYin/Metric3D)]
9. **ZoeDepth** — Bhat et al., *CVPR 2023* [[arXiv](https://arxiv.org/abs/2302.12288)] [[GitHub](https://github.com/isl-org/ZoeDepth)]
10. **AutoFish** — Sun et al., *CVPR 2023* [[arXiv](https://arxiv.org/abs/2303.12145)]

## 2021–2022
11. **MiDaS v3** — Ranftl et al., *ICCV 2021* [[GitHub](https://github.com/isl-org/MiDaS)]
12. **DPT** — Ranftl et al., *ICCV 2021* [[arXiv](https://arxiv.org/abs/2103.13413)]
13. **MonoFlex** — Zhang et al., *CVPR 2021* [[arXiv](https://arxiv.org/abs/2104.01589)]
14. **MonoDTR** — Li et al., *CVPR 2022* [[arXiv](https://arxiv.org/abs/2203.13454)]
15. **PGD** — Wang et al., *CVPR 2022* [[arXiv](https://arxiv.org/abs/2203.15839)]

## Foundational
16. **COLMAP** — Schönberger & Frahm, *CVPR 2016* [[GitHub](https://github.com/colmap/colmap)]
17. **OpenMVG** — Moulon et al., *2013* [[GitHub](https://github.com/openMVG/openMVG)]
18. **ArUco** — Garrido-Jurado et al., *2014* [[OpenCV](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)]

---

## Quick Links

- 📁 [Project Repository](https://github.com/AliNikkhah2001/size-scale-estimation)
- 🌐 [Live Demo](http://localhost:7860) (run `python3 app.py`)
- 📄 [Technical Report](../TECHNICAL_REPORT.md)
- 🔬 [Research Notes](../RESEARCH.md)

---

*Last updated: August 2025 • [Edit on GitHub](https://github.com/AliNikkhah2001/AliNikkhah2001/edit/main/Desktop/size%20scale%20estimation/docs/index.md)*