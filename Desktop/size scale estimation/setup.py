#!/usr/bin/env python3
"""
Setup script for Size Estimation Prototype

This script sets up the environment, downloads necessary models, and provides
a quick test of the installation.
"""

import os
import sys
import argparse
import subprocess
import json
import time
from pathlib import Path

def print_header(message):
    """Print a formatted header message."""
    print("=" * 60)
    print(message)
    print("=" * 60)

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 or higher is required")
        return False
    return True

def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✓ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("✗ pip is not available")
        return False

def install_requirements():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def check_models():
    """Check for pre-trained models and download if needed."""
    print("\nChecking for pre-trained models...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    yolo_models = models_dir / "yolo"
    yolo_models.mkdir(exist_ok=True)
    
    # Check for YOLO model
    yolo_model_path = yolo_models / "yolov8n.pt"
    if not yolo_model_path.exists():
        print(f"Downloading YOLO model to {yolo_model_path}...")
        try:
            from huggingface_hub import hf_hub_download
            # Download from Ultralytics Hub
            hf_hub_download(
                repo_id="ultralytics/yolov8",
                filename="yolov8n.pt",
                local_dir=yolo_models
            )
            print("✓ YOLO model downloaded")
        except ImportError:
            print("Warning: huggingface_hub not installed, skipping YOLO download")
        except Exception as e:
            print(f"Warning: Could not download YOLO model: {e}")
    else:
        print("✓ YOLO model already exists")
    
    return True

def create_sample_data():
    """Create sample data directory with test images."""
    print("\nSetting up sample data...")
    
    sample_dir = Path("data/sample_images")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if we have sample images
    existing_images = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
    
    if existing_images:
        print(f"✓ Found {len(existing_images)} sample images")
        return True
    else:
        print("Note: No sample images found. You can add your own images to the data/sample_images directory")
        print("You can download sample images from:")
        print("  - COCO dataset: https://cocodataset.org/")
        print("  - KITTI dataset: http://www.robots.ox.ac.uk/~vgg/data/kitti/data/")
        print("  - Custom: Add your own object images")
        return False

def test_installation():
    """Test the installation by running a simple test."""
    print("\nTesting installation...")
    
    try:
        # Try to import core modules
        import cv2
        import numpy as np
        import ultralytics
        import gradio
        print("✓ All core modules imported successfully")
        
        # Test YOLO import
        from ultralytics import YOLO
        yolo = YOLO("models/yolo/yolov8n.pt")
        print("✓ YOLO model loaded successfully")
        
        # Test Gradio
        import gradio as gr
        print("✓ Gradio imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def create_test_image():
    """Create a simple test image with objects."""
    print("\nCreating test image...")
    
    try:
        import cv2
        import numpy as np
        
        # Create a test image with colored rectangles
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 240
        
        # Draw some objects
        cv2.rectangle(test_image, (50, 50), (150, 150), (255, 0, 0), -1)  # Red square
        cv2.rectangle(test_image, (250, 100), (400, 250), (0, 255, 0), -1)  # Green rectangle
        cv2.rectangle(test_image, (450, 200), (550, 350), (0, 0, 255), -1)  # Blue rectangle
        
        # Add some text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(test_image, "Test Image", (50, 400), font, 1, (0, 0, 0), 2)
        
        # Save test image
        test_path = Path("data/sample_images/test_objects.jpg")
        test_path.parent.mkdir(exist_ok=True)
        cv2.imwrite(str(test_path), test_image)
        
        print(f"✓ Test image created: {test_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        return False

def print_usage_examples():
    """Print usage examples."""
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n1. Start the web interface:")
    print("   python prototype/single_image_app.py --gradio")
    print("   (Opens in browser at http://localhost:7860)")
    
    print("\n2. Process a single image (CLI):")
    print("   python prototype/cli.py --image photo.jpg --output result.jpg")
    
    print("\n3. Process image with JSON output:")
    print("   python prototype/cli.py --image photo.jpg --format json")
    
    print("\n4. Process image with custom models:")
    print("   python prototype/cli.py --image photo.jpg \\")
    print("     --yolo-model models/yolo/yolov8s.pt \\")
    print("     --depth-model models/depth/depth_pro.pth")
    
    print("\n5. Run batch processing:")
    print("   python << 'EOF'")
    print("   import os")
    print("   import sys")
    print("   sys.path.append('prototype')")
    print("   from single_image_app import process_image")
    print("   import cv2")
    print("   ")
    print("   for filename in os.listdir('input_images'):")
    print("       if filename.lower().endswith(('.png', '.jpg', '.jpeg')):")
    print("           image = cv2.imread(os.path.join('input_images', filename))")
    print("           if image is not None:")
    print("               results = process_image(image)")
    print("               cv2.imwrite(f'output/{filename}_result.jpg', ")
    print("                          cv2.cvtColor(results['visualization'], cv2.COLOR_RGB2BGR))")
    print("   EOF")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup script for Size Estimation Prototype")
    parser.add_argument("--skip-models", action="store_true", help="Skip model downloads")
    parser.add_argument("--skip-test", action="store_true", help="Skip installation test")
    parser.add_argument("--quiet", action="store_true", help="Minimize output")
    
    args = parser.parse_args()
    
    print_header("Size Estimation Prototype Setup")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check pip
    if not check_pip():
        return 1
    
    # Install requirements
    if not args.quiet:
        if not install_requirements():
            print("Warning: Some dependencies could not be installed")
    
    # Check models
    if not args.skip_models:
        if not check_models():
            print("Warning: Some models could not be downloaded")
    
    # Create sample data
    if not create_sample_data():
        if not args.quiet:
            print("Note: Sample data not available")
    
    # Create test image
    if not args.quiet:
        create_test_image()
    
    # Test installation
    if not args.skip_test:
        if not test_installation():
            print("Warning: Installation test failed")
            print("You may need to install missing dependencies")
    
    # Print usage examples
    print_usage_examples()
    
    print_header("Setup Complete!")
    print("\nNext Steps:")
    print("1. Run 'python prototype/single_image_app.py --gradio' to start the web interface")
    print("2. Run 'python prototype/cli.py --help' for CLI options")
    print("3. Add your own images to 'data/sample_images/'")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)