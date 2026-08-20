---
layout: default
title: "Methods | Scale Estimation Review"
description: "Taxonomy of scale estimation methods"
---

# Methods Taxonomy

## Overview

Scale estimation methods fall into **five families** based on what external information they require:

<div class="card-grid">
  <div class="card">
    <h3><span class="badge badge-reference">Reference</span> Known-Reference</h3>
    <p>Place an object of known size in the scene. Direct pixel→metric calibration.</p>
    <strong>Pros:</strong> Exact scale, simple geometry<br>
    <strong>Cons:</strong> Requires marker in every image
  </div>
  <div class="card">
    <h3><span class="badge badge-relative">Relative</span> Monocular Relative Depth</h3>
    <p>Predict ordinal depth from single image. Scale ambiguous without calibration.</p>
    <strong>Pros:</strong> Zero-shot, generalizes well<br>
    <strong>Cons:</strong> No metric scale
  </div>
  <div class="card">
    <h3><span class="badge badge-metric">Metric</span> Monocular Metric Depth</h3>
    <p>Predict absolute depth in meters. Learns scale from training data with known intrinsics.</p>
    <strong>Pros:</strong> Direct metric output<br>
    <strong>Cons:</strong> Domain gaps, needs focal length
  </div>
  <div class="card">
    <h3><span class="badge badge-3d">3D Detection</span> Monocular 3D Detection</h3>
    <p>Predict oriented 3D boxes with dimensions. Uses category-level size priors.</p>
    <strong>Pros:</strong> Full 3D pose + size<br>
    <strong>Cons:</strong> Limited categories, needs 3D labels
  </div>
  <div class="card">
    <h3><span class="badge badge-multiview">Multi-View</span> SfM/MVS</h3>
    <p>Reconstruct 3D from multiple views. Fix scale with known anchor.</p>
    <strong>Pros:</strong> High accuracy, full 3D<br>
    <strong>Cons:</strong> Needs multiple views, compute heavy
  </div>
</div>

---

## Detailed Comparison

| Aspect | Reference | Relative Depth | Metric Depth | 3D Detection | Multi-View |
|--------|-----------|----------------|--------------|--------------|------------|
| **Metric output** | ✅ Direct | ❌ Needs cal | ✅ Direct | ✅ Direct | ✅ After anchor |
| **Single image** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Training data** | Minimal | Large (unlabeled) | Large (with K) | 3D boxes (rare) | None (geometry) |
| **Categories** | Any | Any | Any | Fixed set | Any |
| **Accuracy** | Sub-cm | N/A (ordinal) | 5–15% | 10–20% | 1–5% |
| **Speed** | Fast | Fast | Medium | Medium | Slow |
| **Focal length** | Solved | Not needed | Needed/Predicted | Needed/Predicted | Solved |

---

## Decision Tree

```
START: What's your deployment constraint?
│
├─ Can place marker in scene? → Known-Reference (ArUco, AnyRuler)
│
├─ Single image only?
│   ├─ Need exact metric? → Metric Depth (Metric3D v2, Depth Pro)
│   ├─ Relative OK + can calibrate? → Relative Depth (Depth Anything V2) + reference
│   └─ Known categories (cars, furniture)? → 3D Detection (Cube R-CNN)
│
├─ Multiple views available?
│   ├─ High accuracy needed? → COLMAP + scale anchor
│   └─ Real-time? → Keyframe SfM + detection
│
└─ Mobile/Edge? → Depth Anything V2 Small + YOLOv8n (ONNX/CoreML)
```

---

## Hybrid Pipelines (Recommended for Practice)

Most production systems combine methods:

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  YOLOv8     │────▶│  Depth      │────▶│  Geometry    │
│  Detection  │     │  Anything V2│     │  Fusion      │
└─────────────┘     └─────────────┘     └──────────────┘
                          │                    │
                          ▼                    ▼
                   ┌─────────────┐     ┌──────────────┐
                   │  (Optional) │     │  Output:     │
                   │  Metric3D   │     │  W×H×D (m)   │
                   │  refine     │     │  + confidence│
                   └─────────────┘     └──────────────┘
```

This is what our [Flask demo](../app.py) implements.