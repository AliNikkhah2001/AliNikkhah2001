# Scale and Size Estimation CV Models Research Report

This document summarizes the current state-of-the-art (SOTA) in single and multi-view scale and size estimation for computer vision, focusing on models that can provide metric (real-world) measurements.

## Table of Contents

1. [Introduction](#introduction)
2. [Method Categories](#method-categories)
   - [Known-Reference Scale Estimation](#known-reference-scale-estimation)
   - [Depth-Based Metric Estimation](#depth-based-metric-estimation)
   - [3D Object Detection with Size Estimation](#3d-object-detection-with-size-estimation)
   - [Multi-View Reconstruction with Scale Recovery](#multi-view-reconstruction-with-scale-recovery)
3. [Leading SOTA Models](#leading-sota-models)
4. [Benchmark Datasets](#benchmark-datasets)
5. [Key Use Cases](#key-use-cases)
6. [Limitations and Challenges](#limitations-and-challenges)
7. [Future Directions](#future-directions)

---

## Introduction

Scale and size estimation in computer vision involves determining the physical dimensions of objects in scenes from visual data. This capability is crucial for applications requiring metric accuracy, from medical diagnostics to autonomous driving. The fundamental challenge is the scale ambiguity inherent in monocular vision: without additional information, a single image cannot distinguish between a small object close to the camera and a large object far away.

This report explores four primary methodological approaches to overcome this ambiguity and provide metric measurements:

---

## Method Categories

### 1. Known-Reference Scale Estimation

**Principle:** Use objects with known physical dimensions (rulers, Aruco markers, calibration boards) as scale references within the scene.

**Key Models:**
- **RulerNet**: Deep learning framework for perspective-invariant ruler reading. Uses geometric progression parameters invariant to perspective transformations.
  - *Accuracy:* ~1.2 px/cm on AnyRuler/Rulers2023 datasets
  - *Speed:* 0.8 ms/sample (DeepGP variant)
  - *Strengths:* Generalizes across diverse ruler types and imaging conditions
  - *Paper:* "Reading a Ruler in the Wild" (2025)

- **Aruco-Based Calibration**: Uses square fiducial markers for pose estimation and scale recovery.
  - *Use cases:* Industrial inspection, drone navigation, medical imaging

**Key Datasets:**
- AnyRuler: Diverse ruler types in "in-the-wild" conditions
- Rulers2023: 2,300 annotated ruler images with centimeter marks

**Applications:**
- Medical measurements (lesion size, wound assessment)
- E-commerce product sizing
- Construction/engineering measurements
- Forensic analysis

---

### 2. Depth-Based Metric Estimation

**Principle:** Estimate depth from a single image and convert pixel measurements to metric units using camera intrinsics or learned scale.

**Key Models:**
- **Depth Pro** (Apple, 2024): Foundation model for zero-shot metric monocular depth estimation.
  - *Performance:* 0.3s for 2.25MP depth map
  - *Accuracy:* SOTA on DA-2K (95.3% accuracy), high boundary precision
  - *Features:* No camera intrinsics required, sharp high-frequency details
  - *Code:* Available at https://github.com/apple/ml-depth-pro

- **Metric3D v2**: Versatile geometric foundation model for metric depth and surface normal estimation.
  - *Features:* Joint depth-normal optimization, zero-shot generalization
  - *Benchmark:* Strong performance on OmniDepth benchmark

- **UniDepth**: Universal monocular metric depth estimation with camera self-prompting.
  - *Features:* Predicts 3D points without external camera information
  - *Strengths:* Robust to different camera intrinsics and scene scales

- **Depth Anything V2**: Large-scale training with synthetic + real data.
  - *Variants:* ViT-Small/Base/Large (25M to 1.3B parameters)
  - *Performance:* 95.3% on DA-2K (Small model), 180ms inference

- **Zoedepth**: Zero-shot transfer combining relative and metric depth estimation.
  - *Innovation:* Learns from both relative depth datasets and metric datasets

**Key Datasets:**
- DA-2K: Diverse synthetic-augmented dataset for metric depth evaluation
- KITTI: Outdoor driving scenarios with accurate depth ground truth
- NYU Depth v2: Indoor scene depth annotations
- Middlebury: High-quality stereo depth benchmarks
- Sintel: Synthetic video sequences for temporal consistency

**Applications:**
- Autonomous driving (distance to objects, road geometry)
- Robotics (navigation, manipulation planning)
- AR/VR (real-world measurement tools)
- 3D reconstruction and scene understanding

---

### 3. 3D Object Detection with Size Estimation

**Principle:** Directly detect objects and predict their 3D bounding boxes including physical dimensions.

**Key Models:**
- **Omni3D / Cube R-CNN** (Facebook AI, 2023): Large-scale 3D object detection benchmark and model.
  - *Scale:* 234k images, 3M instances, 98 categories (20× larger than existing benchmarks)
  - *Performance:* Outperforms prior methods on multiple datasets
  - *Innovation:* "Virtual depth" technique handles varying camera intrinsics

- **YOLO26-Depth**: Native depth estimation in the YOLO model family.
  - *Output:* Per-pixel depth in meters from single RGB image
  - *Speed:* Real-time performance on standard hardware
  - *Use:* Robotics, autonomous driving, AR/VR

- **AutoFish**: Dataset and benchmark for fine-grained fish analysis.
  - *Applications:* Fish length estimation, biomass estimation
  - *Datasets:* 454 individual fish with 40+ images each, ground truth length measurements

- **Mono3D detectors**: Specialized for single-camera 3D object detection.
  - *Techniques:* Extrinsic parameter-aware feature transformation

**Key Datasets:**
- KITTI 3D Object Detection: Urban driving scenes with 3D boxes
- nuScenes: Diverse autonomous driving scenarios
- SUN RGB-D: Indoor object detection
- Objectron: 3D object detection with orientation
- ARKitScenes: Indoor scenes with detailed annotations
- AutoFish: Fish size estimation with individual IDs

**Applications:**
- Autonomous vehicle perception (detecting and sizing vehicles, pedestrians)
- Warehouse automation (package dimensions, inventory management)
- Agricultural monitoring (crop measurements, yield estimation)
- Wildlife conservation (animal size measurements)

---

### 4. Multi-View Reconstruction with Scale Recovery

**Principle:** Use multiple views (stereo, multi-camera, or sequential) with known geometry to recover metric scale.

**Key Models & Techniques:**
- **COLMAP with Known Markers**: Structure-from-Motion with scale recovery using ArUco markers or checkerboard patterns.
  - *Method:* Triangulate 3D points using known baseline distances
  - *Applications:* Photogrammetry, indoor scanning, cultural heritage

- **EndoMetric**: Near-light monocular metric scale estimation for endoscopy.
  - *Innovation:* Uses near-infrared light sources for true-scale reconstruction
  - *Medical applications:* Polyp size measurement, lesion assessment

- **Gaussian Splatting with Scale**: 3DGS reconstruction with known reference objects.
  - *Method:* Uses ArUco markers or calibrated objects during training
  - *Applications:* Indoor mapping, robotics simulation

- **Stereo Vision Systems**: Multi-view cameras with known baseline.
  - *Applications:* Depth estimation for robotics, automotive ADAS

**Key Datasets & Techniques:**
- Multi-view stereo datasets with ground truth scale
- Sequential datasets with motion capture for scale validation
- Indoor datasets with calibration patterns for scale recovery

**Applications:**
- 3D mapping and localization
- Augmented reality object placement
- Industrial quality control
- Archaeological site documentation

---

## Leading SOTA Models Summary

| Model | Primary Method | Accuracy | Speed | Scale | Key Strengths |
|-------|---------------|----------|-------|--------|---------------|
| **RulerNet-DeepGP** | Ruler keypoint detection | ~1.2 px/cm | 0.8 ms/sample | Pixel/cm | Generalizes across ruler types |
| **Depth Pro** | Transformer-based metric depth | 95.3% (DA-2K) | 0.3s (2.25MP) | Metric | No intrinsics, sharp boundaries |
| **UniDepth** | Pseudo-spherical 3D representation | ~0.8mError | ~100ms | Metric | Universal, camera-agnostic |
| **Omni3D/Cube R-CNN** | 3D object detection | 23.3AP3D | ~200ms | Metric | Large-scale, 98 categories |
| **Depth Anything V2** | Synthetic+real training | 95.3% (DA-2K ViT-S) | 180ms | Relative→Metric | Fast, lightweight variants |
| **AutoFish** | Skeleton+CNN length estimation | MAE 0.4-0.8cm | ~50ms | Metric | Fine-grained individual tracking |

---

## Benchmark Datasets

### Ruler-Based Datasets
- **AnyRuler**: 2,300+ images with ruler annotations, diverse imaging conditions
- **Rulers2023**: Focus on "in-the-wild" ruler reading challenges

### Depth Estimation Datasets
- **DA-2K**: Diverse synthetic + real for metric depth evaluation
- **KITTI**: Outdoor driving with calibrated cameras
- **NYU Depth v2**: Indoor scene annotations
- **Middlebury**: High-quality stereo depth ground truth

### 3D Detection Datasets
- **OMNI3D**: 234k images, 3M instances, 98 categories (largest 3D detection benchmark)
- **KITTI 3D**: Urban driving with 3D bounding boxes
- **nuScenes**: Multi-modal autonomous driving data
- **AutoFish**: Individual fish with length measurements

### Multi-View Datasets
- **Outdoor datasets** with GPS/IMU for scale validation
- **Indoor datasets** with calibration patterns
- **Medical datasets** with known instrument sizes

---

## Key Use Cases

### 1. Medical & Healthcare
- **Lesion measurement**: Automated size assessment of tumors, skin lesions
- **Endoscopy**: Polyp size estimation, disease progression monitoring
- **Radiology**: Organ dimension measurements, implant sizing
- **Advantages:** Consistent, objective measurements, reduces inter-observer variability

### 2. Forensics & Law Enforcement
- **Crime scene reconstruction**: Object size estimation from photographs
- **Document analysis**: Measuring evidence dimensions
- **Biological evidence**: Animal or plant specimen measurements
- **Advantages:** Non-contact measurement, preserves evidence integrity

### 3. E-commerce & Retail
- **Product sizing**: Garment size estimation from photographs
- **Package dimensions**: Automated shipping cost calculation
- **Inventory management**: Real-time product dimension tracking
- **Advantages:** Faster cataloging, reduced returns due to size discrepancies

### 4. Agriculture & Fisheries
- **Fish measurement**: Automated length and weight estimation
- **Crop monitoring**: Plant height, fruit size estimation
- **Livestock management**: Animal body condition scoring
- **Advantages**: Rapid assessment, reduces manual labor

### 5. Autonomous Systems
- **Distance estimation**: Real-time obstacle sizing and distance calculation
- **Obstacle classification**: Size-based danger assessment
- **Path planning**: Clearance calculations around large objects
- **Advantages**: Enhanced safety, improved navigation accuracy

### 6. Industrial & Manufacturing
- **Quality control**: Part dimension verification
- **Assembly line monitoring**: Component size checking
- **Maintenance**: Equipment wear measurement
- **Advantages**: Consistent measurements, reduced human error

---

## Limitations and Challenges

### Technical Challenges
1. **Lighting conditions**: All methods struggle with shadows, glare, and low-light scenarios
2. **Viewpoint dependency**: Most methods assume relatively straightforward viewing angles
3. **Surface texture**: Highly reflective or transparent surfaces confuse depth estimation
4. **Scale ambiguity**: Even with depth, metric accuracy requires camera calibration
5. **Computational requirements**: High-end models (Depth Pro, Omni3D) require significant resources

### Practical Limitations
1. **Dataset availability**: Many SOTA models require specialized training datasets
2. **Real-world generalization**: Performance often degrades on unseen environments
3. **Hardware requirements**: Some methods require specific sensors or equipment
4. **Regulatory approval**: Medical applications require extensive validation
5. **Integration complexity**: Many solutions don't provide production-ready APIs

### Open Research Problems
1. **Zero-shot generalization**: How to maintain accuracy on completely unseen domains
2. **Real-time performance**: Balancing accuracy and speed for edge deployment
3. **Robustness**: Handling challenging conditions (rain, fog, motion blur)
4. **Calibration-free operation**: Eliminating need for camera intrinsics or reference objects
5. **Multi-modal fusion**: Combining depth, lidar, and vision for robust measurement

---

## Future Directions

### Emerging Trends
1. **Foundation models**: Pre-trained large-scale models fine-tuned for specific measurement tasks
2. **Diffusion-based approaches**: Using generative models for high-quality depth and metric estimation
3. **Multi-modal systems**: Combining vision with depth sensors, IMU, and GPS
4. **Self-supervised learning**: Reducing annotation requirements for training data
5. **Edge optimization**: Model compression for mobile and embedded deployment

### Future Applications
1. **Smart cities**: Automated measurement of infrastructure components
2. **Precision agriculture**: Real-time crop and soil analysis
3. **Healthcare at home**: Remote monitoring of patient measurements
4. **AR/VR interaction**: Real-world object manipulation and measurement
5. **Robotics**: Adaptive grasping based on object size and distance

---

## Conclusion

The field of scale and size estimation in computer vision has made remarkable progress, with SOTA models now capable of providing metric measurements with high accuracy and reasonable speed. The choice of method depends on specific application requirements:

- **For precise measurements**: Known-reference methods (RulerNet) provide highest accuracy
- **For general scene understanding**: Depth-based models (Depth Pro, UniDepth) offer best generalization
- **For object detection**: 3D detection models (Omni3D) provide comprehensive scene understanding
- **For large-scale reconstruction**: Multi-view methods with calibrated references

Practical deployment requires careful consideration of accuracy requirements, computational constraints, and real-world robustness. Future advances in foundation models and multi-modal fusion will likely bridge many current limitations.

---

## References

1. Pan et al. "Reading a Ruler in the Wild." *Computer Vision and Pattern Recognition*, 2025.
2. Bochkovskii et al. "Depth Pro: Sharp Monocular Metric Depth in Less Than a Second." *Apple Machine Learning Research*, 2024.
3. Piccinelli et al. "UniDepth: Universal Monocular Metric Depth Estimation." *CVPR*, 2024.
4. Brazil et al. "Omni3D: A Large Benchmark and Model for 3D Object Detection in the Wild." *CVPR*, 2023.
5. The DeepFish Dataset: "The DeepFish computer vision dataset for fish instance segmentation, classification, and size estimation." *Scientific Data*, 2022.
6. Pizzicoli et al. "Monocular Metric Distance Estimation in Maritime Scenes via Reference-Based Scale Recovery." *CVPR Workshops*, 2026.

*(Note: This document is continually updated as new research emerges)*