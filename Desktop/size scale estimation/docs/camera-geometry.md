# Camera Geometry & Focal Length for Size Estimation

## The Core Problem

**A 2D image loses depth information.** To recover metric size from pixels, we need the camera's geometric model.

---

## Pinhole Camera Model

```
          World Point (X, Y, Z)
                   │
                   │  Z = distance from camera
                   ▼
         ┌─────────────────┐
         │   Image Plane   │  f = focal length (pixels)
         │        ●        │  (x, y) = pixel coordinates
         │       /|\       │
         │      / | \      │
         │   f /  |  \     │
         │    /   |   \    │
         └───/────|────\───┘
             Camera Center
```

**Projection Equations:**
```
x = f * X / Z + cx
y = f * Y / Z + cy
```

Where:
- `(X, Y, Z)` = 3D world coordinates (meters)
- `(x, y)` = 2D pixel coordinates
- `f` = focal length in pixels
- `(cx, cy)` = principal point (image center)

---

## From Pixels to Meters

Given a **bounding box** in pixels and **depth** at that location:

```
bbox_width_px  = x2 - x1
bbox_height_px = y2 - y1
depth_m        = Z (from depth model at bbox center)

world_width_m  = bbox_width_px  * depth_m / f
world_height_m = bbox_height_px * depth_m / f
```

**This is the fundamental equation.** Everything depends on knowing `f`.

---

## Focal Length: Where Does It Come From?

| Source | How to Get | Accuracy |
|--------|------------|----------|
| **EXIF metadata** | `focal_length_mm * image_width_px / sensor_width_mm` | High (if available) |
| **Camera calibration** | Chessboard/ArUco calibration (OpenCV) | Very high |
| **Known object** | `f = bbox_px * known_distance_m / known_width_m` | High (if object size known) |
| **Depth model** | Some (Depth Pro, Metric3D) predict `f` | Medium |
| **Heuristic** | `f ≈ 1.2 × image_width` (typical phone) | Low (~30% error) |
| **Learnable** | Treat `f` as parameter, optimize | Medium |

---

## Sensor Size Matters

```
f_pixels = focal_length_mm × image_width_px / sensor_width_mm
```

| Device | Sensor Width | Focal Length (mm) | f_pixels (4000px wide) |
|--------|-------------|-------------------|------------------------|
| iPhone 15 main | 6.3mm | 24mm (equiv) → 6.86mm actual | ~4350 |
| iPhone 15 ultra-wide | 4.8mm | 13mm (equiv) → 2.24mm actual | ~1867 |
| Full-frame DSLR | 36mm | 50mm | ~5555 |
| APS-C DSLR | 23.5mm | 35mm | ~5957 |
| Webcam (typical) | 4.8mm | 3.6mm | ~3000 |

**Key insight:** "24mm equivalent" is marketing. You need **actual focal length in mm + sensor width in mm**.

---

## Depth Model Output Types

| Model | Output | Can Give Metric Size? |
|-------|--------|----------------------|
| Depth Anything V2 | Relative depth [0,1] | ❌ Needs `f` + scale calibration |
| Metric3D v2 | Metric depth (meters) | ✅ Direct, but needs `f` for point cloud |
| Depth Pro | Metric depth + predicts `f` | ✅ Full metric |
| MiDaS | Relative (inverse depth) | ❌ |
| ZoeDepth | Metric (indoor/outdoor) | ✅ With `f` |

---

## Error Propagation

```
δsize/size = δbbox/bbox + δdepth/depth + δf/f
```

Typical errors:
- Bbox: 5-10% (detection)
- Depth: 10-20% (monocular)
- Focal length: 20-50% (if estimated)

**Total size error: ~30-60% without calibration**

---

## Practical Solutions

### 1. ArUco Calibration (Best for Controlled)
```python
# Print 100mm ArUco marker, detect it
marker_size_m = 0.1
corners = detect_aruco(image)
f = solve_for_f(corners, marker_size_m, camera_matrix)
```

### 2. Known Object Calibration
```python
# Detect object of known size (e.g., A4 paper = 210×297mm)
known_w, known_h = 0.21, 0.297
bbox = detect_object(image, class_name='paper')
f = bbox_w_px * distance_m / known_w
```

### 3. EXIF + Sensor Database
```python
from PIL import Image
exif = Image.open('photo.jpg')._getexif()
focal_mm = exif[37386]  # FocalLength
# Look up sensor width for camera model
sensor_w_mm = SENSOR_DB[camera_model]
f_px = focal_mm * image_w_px / sensor_w_mm
```

### 4. Depth Pro (Predicts f)
```python
import depth_pro
model, transform = depth_pro.create_model_and_transforms()
pred = model.infer(image)
depth_m = pred['depth']          # Metric depth
f_px = pred['focallength_px']    # Predicted focal length
# Now size = bbox_px * depth_m / f_px
```

---

## Summary for Implementation

```python
def estimate_size(bbox_px, depth_m, focal_px=None, image_w_px=None):
    """
    bbox_px: (w, h) in pixels
    depth_m: distance to object center in meters
    focal_px: focal length in pixels (if None, use heuristic)
    image_w_px: image width (for heuristic)
    """
    if focal_px is None:
        focal_px = image_w_px * 1.2  # Rough phone heuristic
    
    w_m = bbox_px[0] * depth_m / focal_px
    h_m = bbox_px[1] * depth_m / focal_px
    return w_m, h_m

# Example: person at 3m, bbox 200px tall, f=3000px
# h = 200 * 3 / 3000 = 0.2m → WRONG (person is 1.7m)
# Actual f for phone ~4000px: h = 200 * 3 / 4000 = 0.15m → STILL WRONG
# Because depth from relative model isn't metric!
# Need metric depth OR known scale reference
```
