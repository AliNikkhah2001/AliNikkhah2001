---
layout: default
title: "Applications | Scale Estimation Review"
description: "Real-world applications and use cases for scale estimation"
---

# Applications & Use Cases

## By Domain

### Medical & Healthcare

| Application | Method | Requirements |
|-------------|--------|--------------|
| **Wound measurement** | Known-reference (ruler/ArUco) + segmentation | Sub-mm accuracy, sterile markers |
| **Tumor sizing (radiology)** | 3D detection (Monai) + calibration | DICOM, known voxel spacing |
| **Dental/orthodontics** | Intraoral scanner + known reference | High-res, controlled lighting |
| **Surgical navigation** | ArUco + depth + registration | Real-time, <5mm error |
| **Dermatology (lesion tracking)** | Ruler detection + segmentation | Mobile app, patient self-use |

**Key papers:** *RulerNet for Medical Scale* (MICCAI 2024), *Intraoperative Scale Estimation* (IROS 2023)

---

### E-Commerce & Retail

| Application | Method | Requirements |
|-------------|--------|--------------|
| **Product dimensioning** | Depth + detection + known background | White background, multiple angles |
| **Virtual try-on** | Metric depth (Depth Pro) + body pose | Accurate focal length, real-time |
| **Package measurement (logistics)** | 3D detection (Cube R-CNN) + conveyor | High throughput, varying boxes |
| **Furniture placement (AR)** | Metric depth + plane detection | Mobile LiDAR or Depth Pro |
| **Size recommendation** | Body measurement from photos | Privacy-preserving, diverse bodies |

**Key papers:** *Metric3D for E-commerce* (CVPRW 2024), *Virtual Try-on with Metric Depth* (SIGGRAPH 2024)

---

### Agriculture & Aquaculture

| Application | Method | Requirements |
|-------------|--------|--------------|
| **Livestock weighing** | AutoFish / known-reference + 3D detection | Non-invasive, outdoor |
| **Crop measurement (phenotyping)** | SfM + scale anchor (ground markers) | Drone/ground robot, seasonal |
| **Fruit sizing & yield estimation** | 3D detection + depth | Orchard, varying lighting |
| **Fish biomass (aquaculture)** | AutoFish (known species length) | Underwater, turbid water |

**Key papers:** *AutoFish* (CVPR 2023), *Crop Phenotyping with SfM* (Plant Phenomics 2024)

---

### Logistics & Manufacturing

| Application | Method | Requirements |
|-------------|--------|--------------|
| **Parcel dimensioning (DWS)** | 3D detection + conveyor belt sync | Real-time, 100+ parcels/min |
| **Pallet loading optimization** | Depth + detection + 3D packing | Warehouse lighting |
| **Quality control (defect + size)** | Known-reference + high-res inspection | Sub-mm, controlled |
| **Inventory counting** | YOLO + depth (shelf monitoring) | Mobile robot/drone |

**Key papers:** *Logistics Dimensioning Systems* (ICRA 2024), *Warehouse Robotics with Metric Depth* (RSS 2023)

---

### Autonomous Driving & Robotics

| Application | Method | Requirements |
|-------------|--------|--------------|
| **3D object detection** | Cube R-CNN / MonoFlex + LiDAR fusion | Real-time, 10Hz+, safety-critical |
| **Metric depth for planning** | Metric3D v2 / Depth Pro | Generalization, edge cases |
| **Visual SLAM scale** | COLMAP/orb-slam + IMU/GPS | Loop closure, long-term |
| **Manipulation (grasp planning)** | Metric depth + 6DoF pose | Real-time, <2cm error |

**Key papers:** *Omni3D for Driving* (CVPR 2023), *Metric Depth for Robotics* (CoRL 2024)

---

### Construction & Infrastructure

| Application | Method | Requirements |
|-------------|--------|--------------|
| **As-built verification** | SfM + known reference (total station) | cm accuracy, large scale |
| **Progress monitoring** | Multi-view + scale anchor | Weekly/daily captures |
| **Bridge/structure inspection** | Drone SfM + known markers | GPS-denied, high-res |
| **BIM coordination** | Metric depth + CAD alignment | Indoor/outdoor transition |

**Key papers:** *Construction Monitoring with SfM* (ASCE 2024), *Digital Twins with Metric Scale* (ICRA 2024)

---

### Forensics & Security

| Application | Method | Requirements |
|-------------|--------|--------------|
| **Crime scene measurement** | ArUco/ruler + photogrammetry | Court-admissible, chain of custody |
| **Accident reconstruction** | SfM + vehicle dimensions | Post-incident, varying conditions |
| **Border/security screening** | Known-reference + X-ray/visual | High throughput, regulated |

---

### Cultural Heritage & AR/VR

| Application | Method | Requirements |
|-------------|--------|--------------|
| **Artifact documentation** | SfM + scale bar | Sub-mm, texture + geometry |
| **Site reconstruction** | Drone SfM + GCPs | Large area, georeferenced |
| **AR occlusion** | Metric depth (Depth Pro) | Real-time mobile, <10ms |
| **Virtual tourism** | NeRF/3DGS + scale anchor | High visual fidelity |

---

## Implementation Patterns by Use Case

### Pattern 1: Controlled Environment (Medical, Factory, Forensics)
```
[ArUco Marker] → [Camera Calibration] → [Detection] → [Metric Size]
     │                │                    │              │
  Print 100mm      cv2.calibrateCamera    YOLO/Segment   bbox_px * Z / f
  marker           (or solvePnP)          Anything       (exact)
```

### Pattern 2: In-the-Wild Single Image (E-commerce, Mobile Apps)
```
[Image] → [YOLO Detection] → [Depth Anything V2] → [Focal Heuristic] → [Metric Size]
                              (relative)              │
                              │                    f ≈ 1.2 × W
                              ▼                    ▼
                       [Optional: Metric3D]    [Calibration UI]
                       (refines depth)         (user measures known object)
```

### Pattern 3: Known Categories (Automotive, Robotics)
```
[Image] → [Cube R-CNN] → [3D Box: x,y,z,w,h,l,θ] → [Metric Size Direct]
                      (category priors)
```

### Pattern 4: Multi-View (Construction, Heritage, Logistics)
```
[Video/Frames] → [COLMAP SfM] → [Sparse Point Cloud + Poses] 
                                    │
                                    ▼
                          [Scale Anchor: Known Object / GPS / IMU]
                                    │
                                    ▼
                          [Scaled 3D Model] → [Measurements]
```

---

## Error Budget by Application

| Application | Tolerable Error | Typical Achieved | Gap |
|-------------|-----------------|------------------|-----|
| Medical (wound) | <2mm | 1-3mm | ✅ |
| E-commerce (product) | <5% | 3-10% | ⚠️ |
| Logistics (parcel) | <1cm | 0.5-2cm | ✅ |
| Automotive (3D det) | <10cm | 15-30cm | ❌ |
| Construction (as-built) | <1cm | 0.5-5cm | ⚠️ |
| Agriculture (livestock) | <5% | 3-8% | ⚠️ |
| AR/VR (occlusion) | <5cm | 2-10cm | ⚠️ |

---

## Deployment Considerations

### Mobile (iOS/Android)
```swift
// iOS: CoreML + Vision
import CoreML
import Vision

let model = try DepthAnythingV2Small(configuration: MLModelConfiguration())
let request = VNCoreMLRequest(model: model) { request, error in
    let depthMap = request.results?.first as? VNPixelBufferObservation
    // Convert to metric with focal length
}

// Android: TFLite / ONNX Runtime
// Depth Anything V2 Small: ~180ms on Snapdragon 8 Gen 2
```

### Edge (Jetson, Raspberry Pi)
```python
# Jetson Orin: TensorRT optimization
# Depth Anything V2 Small: ~45ms (FP16)
# YOLOv8n: ~8ms
# Total pipeline: ~60ms (16 FPS)
```

### Cloud (GPU Server)
```python
# Batch processing
# Depth Anything V2 Large: ~115ms/img
# Metric3D v2 Giant: ~210ms/img
# Depth Pro: ~300ms/img (2.25MP)
```

---

## Privacy & Ethics

| Concern | Mitigation |
|---------|------------|
| **Body measurement** | On-device processing, no image upload, differential privacy |
| **Medical images** | HIPAA/GDPR compliance, encrypted storage, access control |
| **Surveillance** | Purpose limitation, data minimization, transparency |
| **Biometric data** | Explicit consent, right to deletion, secure enclaves |

---

## Future Application Directions

1. **Foundation models for metric geometry** — Unified models (Depth Pro, UniDepth) reducing need for task-specific training
2. **Generative priors** — Diffusion models (Marigold, GeoWizard) for detail recovery
3. **Multi-modal fusion** — RGB + LiDAR + IMU + GPS for robust scale
4. **Self-supervised scale learning** — Video consistency + known object priors
5. **Standardized benchmarks** — Community effort for size estimation leaderboard