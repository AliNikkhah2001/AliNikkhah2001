# Scale and Size Estimation for Computer Vision

## Overview

This repository contains state-of-the-art research and practical implementations for computer vision-based scale and size estimation. The goal is to enable real-world measurements from visual data, addressing the fundamental challenge of converting pixel information to metric units.

## Key Features

### Research Summary
- Comprehensive analysis of SOTA models for scale and size estimation
- Evaluation of four main methodological approaches
- Detailed benchmark dataset comparisons
- Identification of key use cases and applications

### Practical Implementations
- **Single-image size estimation** using YOLO + depth models
- **Ruler-based scale calibration** for precise measurements
- **Multi-view reconstruction** with scale recovery
- **Web interface** for easy deployment and interaction

### Model Integrations
- YOLO variants for object detection (v8n, v9n)
- Depth estimation models (Depth Pro, Depth Anything V2)
- Ruler reading (RulerNet)
- 3D object detection (Omni3D/Cube R-CNN)

## Quick Start

### Prerequisites

```bash
# Create virtual environment
python -m venv size_estimation_env

# Activate environment
source size_estimation_env/bin/activate  # On Windows: size_estimation_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Installation

The package can be used in two ways:

#### Option 1: Full Web Interface (Recommended)

```bash
# Start the web interface with Gradio
python prototype/single_image_app.py --gradio

# Open your browser to: http://localhost:7860
```

#### Option 2: Command-Line Processing

```bash
# Process a single image
python prototype/cli.py --image input.jpg --output output.jpg --format json

# Process multiple images
for img in images/*.jpg; do
    python prototype/cli.py --image "$img" --output "results/${img%.*}_result.jpg"
done
```

### Usage Examples

#### 1. Upload Image and Get Size Estimates

1. Start the web interface
2. Upload an image containing objects of interest
3. View results:
   - Object detections with bounding boxes
   - Metric size estimates (width × height × depth in meters)
   - Confidence scores
   - Depth map visualization

#### 2. Command-Line Processing

```bash
# Basic usage
python prototype/cli.py --image photo.jpg --output annotated.jpg

# With JSON output for data processing
python prototype/cli.py --image photo.jpg --format json

# With CSV output for spreadsheet import
python prototype/cli.py --image photo.jpg --format csv

# With custom model paths
python prototype/cli.py --image photo.jpg \
  --yolo-model /path/to/yolo_model.pt \
  --depth-model /path/to/depth_model.pth
```

## Research Summary

### Methodology Categories

1. **Known-Reference Scale Estimation**
   - Ruler-based calibration (RulerNet)
   - Aruco marker detection
   - Applications: Medical measurements, construction, forensics

2. **Depth-Based Metric Estimation**
   - Zero-shot metric depth models (Depth Pro, UniDepth)
   - Relative-to-metric conversion (Zoedepth)
   - Applications: Robotics, autonomous driving, AR/VR

3. **3D Object Detection with Size Estimation**
   - Cube R-CNN (Omni3D)
   - YOLO variants with depth
   - Applications: Warehouse automation, vehicle detection

4. **Multi-View Reconstruction with Scale Recovery**
   - SfM with known markers (COLMAP)
   - Multi-camera systems
   - Applications: 3D mapping, cultural heritage

### Leading SOTA Models

| Model | Method | Accuracy | Speed | Scale |
|-------|--------|----------|-------|--------|
| RulerNet-DeepGP | Ruler keypoint detection | ~1.2 px/cm | 0.8 ms/sample | Pixel/cm |
| Depth Pro | Transformer-based metric depth | 95.3% (DA-2K) | 0.3s (2.25MP) | Metric |
| UniDepth | Pseudo-spherical 3D representation | ~0.8mError | ~100ms | Metric |
| Omni3D/Cube R-CNN | 3D object detection | 23.3AP3D | ~200ms | Metric |

### Key Datasets

- **AnyRuler/Rulers2023**: Ruler-based scale estimation
- **DA-2K**: Metric depth evaluation
- **OMNI3D**: Large-scale 3D object detection
- **AutoFish**: Fish size estimation with ground truth

### Applications

- **Medical**: Lesion measurement, endoscopy measurements
- **Forensics**: Crime scene reconstruction, evidence sizing
- **E-commerce**: Product sizing, package dimensions
- **Agriculture**: Fish measurement, crop monitoring
- **Autonomous Systems**: Distance estimation, obstacle sizing
- **Industrial**: Quality control, part dimension verification

## Advanced Usage

### Custom Models

To use custom trained models:

1. Place model files in the `models/` directory
2. Update `config.yaml` with model paths
3. Modify `prototype/single_image_app.py` to load your custom models

### Batch Processing

```bash
# Create output directory
mkdir -p batch_results

# Process all images in a directory
python << 'EOF'
import os
from PIL import Image
import numpy as np
import sys
sys.path.append('prototype')
from single_image_app import process_image

input_dir = "input_images"
output_dir = "batch_results"

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Load image
        img_path = os.path.join(input_dir, filename)
        image = np.array(Image.open(img_path))
        
        # Process
        print(f"Processing {filename}...")
        results = process_image(image)
        
        # Save results
        output_name = filename.rsplit('.', 1)[0]
        
        # Save visualization
        cv2.imwrite(os.path.join(output_dir, f"{output_name}_vis.jpg"), 
                   cv2.cvtColor(results["visualization"], cv2.COLOR_RGB2BGR))
        
        # Save detailed results
        with open(os.path.join(output_dir, f"{output_name}_results.json"), "w") as f:
            import json
            json.dump(results["size_results"], f, indent=2)
        
        print(f"  ✓ Saved results to {output_name}")
EOF
```

### Model Integration

To integrate new models:

1. **For YOLO models**: Place `.pt` files in the `models/yolo/` directory
2. **For depth models**: Place model files in `models/depth/` with appropriate `config.yaml` entry
3. **Update dependencies**: Add required libraries to `requirements.txt`

## File Structure

```
size-estimation/
├── README.md                 # This file
├── RESEARCH.md               # Detailed research summary
├── requirements.txt          # Python dependencies
├── config.yaml               # Configuration settings
├── pyproject.toml            # Project metadata
├── models/                   # Pre-trained models (if included)
│   ├── yolo/                 # YOLO models
│   └── depth/                # Depth estimation models
├── data/                     # Sample data
│   └── sample_images/        # Example images
├── prototype/                # Core implementations
│   ├── __init__.py           # Package initialization
│   ├── single_image_app.py   # Web interface implementation
│   └── cli.py                # Command-line interface
└── docs/                     # Documentation
    └── examples/             # Usage examples
```

## Development Guide

### Adding New Models

1. Create a new model directory in `models/`
2. Implement loading function in `prototype/single_image_app.py`
3. Add model configuration to `config.yaml`
4. Test with sample images
5. Update `RESEARCH.md` with performance metrics

### Performance Optimization

1. **Model quantization**: Convert models to ONNX or use quantization for faster inference
2. **Batch processing**: Process multiple images in parallel
3. **Caching**: Cache model outputs for repeated images
4. **Hardware acceleration**: Use GPU when available

### Testing and Validation

1. **Unit tests**: Test individual components
2. **Integration tests**: Test full pipeline
3. **Performance tests**: Benchmark on different hardware
4. **Accuracy tests**: Compare against ground truth where available

## Troubleshooting

### Common Issues

#### Model Loading Errors
```
# Error: Could not load model
# Solution: Check file paths and internet connection
```

#### GPU Memory Issues
```
# Error: CUDA out of memory
# Solution: Reduce batch size, use smaller models
```

#### Installation Problems
```
# Error: pip install failed
# Solution: Use virtual environment, update pip
```

### Getting Help

1. Check the [Troubleshooting](troubleshooting.md) guide
2. Visit the GitHub repository issues
3. Join the community on Discord/Slack (if available)
4. Check for updated documentation

## Future Development

### Planned Features

1. **Multi-modal fusion**: Combine depth, lidar, and vision data
2. **Real-time processing**: < 100ms inference for video streams
3. **Self-supervised learning**: Reduce annotation requirements
4. **Edge deployment**: Optimized for mobile and embedded devices
5. **AR/VR integration**: Direct measurement in augmented reality

### Research Directions

1. **Foundation models**: Large-scale pre-trained models fine-tuned for specific tasks
2. **Diffusion-based approaches**: Using generative models for high-quality depth
3. **Cross-domain generalization**: Zero-shot adaptation to new environments
4. **Uncertainty quantification**: Better confidence estimation
5. **Multi-view consistency**: Ensuring consistent measurements across views

## Contributing

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit a pull request

### Research Contributions

1. Update `RESEARCH.md` with new findings
2. Add benchmark results
3. Document new datasets
4. Contribute model weights

### Documentation

1. Write tutorials and examples
2. Update API documentation
3. Create user guides
4. Maintain changelog

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

## Citation

If you use this research or code in your work, please cite:

```bibtex
@misc{size_estimation_cv_2025,
  title={Scale and Size Estimation for Computer Vision: SOTA Models and Practical Implementations},
  author={Developer},
  year={2025},
  url={https://github.com/yourusername/size-estimation-cv}
}
```

## Acknowledgments

We thank the open-source community for their contributions to computer vision models and datasets. Special thanks to:

- Apple ML Research (Depth Pro)
- Facebook AI Research (Omni3D)
- Ultralytics (YOLO family)
- Huawei (Depth Anything V2)
- And all contributors to open-source computer vision!

---

*This project is continuously updated as new research emerges. Check for updates regularly.*