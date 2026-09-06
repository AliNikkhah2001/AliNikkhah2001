# Prototype: Simple CLI for Size Estimation

"""
Command-line interface for size estimation using YOLO + Depth Pro models.

This script provides a simple command-line interface for processing images
and estimating object sizes using a combination of YOLO object detection
and depth estimation models.
"""

import os
import sys
import argparse
import json
import time
from typing import List, Dict, Any
import numpy as np
import cv2

# Import the core processing functions from the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import from the app module, with fallback
app_module = None
try:
    from single_image_app import (
        load_yolo_model,
        load_depth_model,
        detect_objects,
        estimate_depth,
        calculate_metric_size,
        create_visualization,
        process_image
    )
    app_module = "single_image_app"
    print("✓ Using single_image_app module")
except ImportError as e:
    print(f"✗ Could not import from single_image_app: {e}")
    print("Falling back to simplified implementation...")
    app_module = None

# Fallback implementations for when the app module is not available
if not app_module:
    print("Using fallback implementations...")
    
    def load_yolo_model(model_path: str = None) -> Any:
        """Load YOLO model for object detection (fallback)."""
        print(f"Loading YOLO model from {model_path if model_path else 'default YOLOv8n'}")
        try:
            import torch
            from ultralytics import YOLO
            
            if model_path and os.path.exists(model_path):
                model = YOLO(model_path)
            else:
                # Use the smallest YOLO model available
                model = YOLO("yolov8n.pt")
            
            print("✓ YOLO model loaded successfully")
            return model
        except Exception as e:
            print(f"✗ Failed to load YOLO model: {e}")
            return None
    
    def load_depth_model(model_path: str = None) -> Dict:
        """Load depth estimation model (fallback)."""
        print("Loading depth estimation model...")
        try:
            # Check if we're on a system with CUDA
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")
            
            # Create a simple placeholder model for demo
            DEPTH_MODEL = {"type": "placeholder"}
            print("✓ Depth model placeholder created")
            return DEPTH_MODEL
        except Exception as e:
            print(f"✗ Failed to load depth model: {e}")
            return {"type": "placeholder"}
    
    def detect_objects(image: np.ndarray, yolo_model) -> List[Dict]:
        """Detect objects in image using YOLO (fallback)."""
        if yolo_model is None:
            print("No YOLO model available, using simple detection")
            return detect_fallback_objects(image)
        
        try:
            print(f"Running YOLO detection on image of shape {image.shape}")
            results = yolo_model(image, conf=0.25, iou=0.45)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        detection = {
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                            "confidence": confidence,
                            "class_id": class_id,
                            "class_name": f"Class_{class_id}"
                        }
                        detections.append(detection)
            
            print(f"✓ Detected {len(detections)} objects")
            return detections
        except Exception as e:
            print(f"YOLO detection failed: {e}")
            return detect_fallback_objects(image)
    
    def detect_fallback_objects(image: np.ndarray) -> List[Dict]:
        """Simple fallback object detection for demo when YOLO is not available."""
        detections = []
        
        # Convert to grayscale and apply simple edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            if cv2.contourArea(contour) > 1000:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                
                # Only consider objects that are not too small
                if w > 20 and h > 20 and (w * h) < (image.shape[0] * image.shape[1]) * 0.5:
                    detection = {
                        "bbox": [float(x), float(y), float(x + w), float(y + h)],
                        "confidence": 0.7,
                        "class_id": 0,
                        "class_name": "Object"
                    }
                    detections.append(detection)
        
        print(f"✓ Fallback detection found {len(detections)} objects")
        return detections
    
    def estimate_depth(image: np.ndarray, depth_model) -> np.ndarray:
        """Estimate depth map from image (fallback)."""
        print("Estimating depth map...")
        
        # Simple fallback depth estimation based on image gradients
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Create depth from gradients (simple approximation)
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=5)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalize to [0, 1]
        if magnitude.max() > 0:
            depth = magnitude / magnitude.max()
        else:
            depth = np.zeros_like(magnitude)
        
        # Invert: darker objects are farther away
        depth = 1.0 - depth
        
        print("✓ Depth map estimated")
        return depth
    
    def calculate_metric_size(bbox: List[float], depth_map: np.ndarray, image_shape: tuple) -> Dict[str, Any]:
        """Calculate real-world size of object from bounding box and depth (fallback)."""
        x1, y1, x2, y2 = bbox
        img_h, img_w = image_shape[:2]
        
        # Get depth at bounding box center
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        
        # Ensure center is within bounds
        center_x = max(0, min(center_x, img_w - 1))
        center_y = max(0, min(center_y, img_h - 1))
        
        center_depth = depth_map[center_y, center_x]
        
        # Estimate camera intrinsics (these would be known for real deployment)
        focal_length = img_w  # Approximation
        sensor_width = 36.0   # mm (typical full-frame sensor)
        pixel_size = sensor_width / img_w
        
        # Calculate real-world dimensions
        # The depth value is normalized, so we need to convert to metric
        # For demo purposes, assume depth in meters when depth > 0.5
        metric_depth = center_depth * 10.0  # Scale for demo
        
        # Object width and height in the image
        obj_width_px = x2 - x1
        obj_height_px = y2 - y1
        
        # Convert to metric units
        obj_width_m = (obj_width_px * pixel_size) / 1000.0  # mm to meters
        obj_height_m = (obj_height_px * pixel_size) / 1000.0  # mm to meters
        
        # Adjust based on depth (perspective projection)
        if metric_depth > 0:
            obj_width_m = obj_width_m * (1.0 / metric_depth)
            obj_height_m = obj_height_m * (1.0 / metric_depth)
        
        # Calculate volume approximation (assuming box shape)
        obj_volume_m3 = obj_width_m * obj_height_m * metric_depth
        
        # Calculate distance confidence based on depth quality
        depth_quality = 1.0 - abs(metric_depth - 2.0) / 3.0  # Simulate confidence based on distance
        depth_quality = max(0.0, min(1.0, depth_quality))
        
        return {
            "width_meters": float(obj_width_m),
            "height_meters": float(obj_height_m),
            "depth_meters": float(metric_depth),
            "volume_cubic_meters": float(obj_volume_m3),
            "confidence": float(depth_quality),
            "center_distance": float(metric_depth)
        }
    
    def create_visualization(image: np.ndarray, detections: List[Dict], depth_map: np.ndarray, 
                             results: List[Dict]) -> np.ndarray:
        """Create visualization with bounding boxes and size information (fallback)."""
        # Convert to PIL Image for easier drawing
        try:
            from PIL import Image as PILImage, ImageDraw as PILDraw
            vis_image = PILImage.fromarray(image)
            draw = PILDraw.Draw(vis_image)
            
            # Try to load a font
            try:
                font = PILImageFont.truetype("arial.ttf", 16)
                small_font = PILImageFont.truetype("arial.ttf", 12)
            except:
                font = PILImageFont.load_default()
                small_font = font
            
            # Draw bounding boxes and results
            for i, (detection, result) in enumerate(zip(detections, results)):
                bbox = detection["bbox"]
                x1, y1, x2, y2 = bbox
                
                # Draw bounding box
                color = (255, 0, 0)  # Red for regular detections
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
                
                # Draw label background
                label = f"{detection['class_name']}: {detection['confidence']:.2f}"
                draw.rectangle([x1, y1 - 20, x1 + len(label) * 8, y1], fill=(255, 0, 0))
                
                # Draw label text
                draw.text((x1 + 2, y1 - 18), label, fill=(255, 255, 255), font=small_font)
                
                # Draw size information if available
                if "width_meters" in result:
                    size_info = f"W: {result['width_meters']:.2f}m H: {result['height_meters']:.2f}m D: {result['center_distance']:.2f}m"
                    draw.text((x1, y2 + 5), size_info, fill=(0, 255, 0), font=small_font)
            
            return np.array(vis_image)
        except ImportError:
            # Fallback to OpenCV drawing
            vis_image = image.copy()
            
            # Draw bounding boxes and results
            for i, (detection, result) in enumerate(zip(detections, results)):
                bbox = detection["bbox"]
                x1, y1, x2, y2 = bbox
                
                # Draw bounding box
                color = (255, 0, 0)  # Red for regular detections
                cv2.rectangle(vis_image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                
                # Draw label background
                label = f"{detection['class_name']}: {detection['confidence']:.2f}"
                cv2.putText(vis_image, label, (int(x1), int(y1) - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Draw size information if available
                if "width_meters" in result:
                    size_info = f"W: {result['width_meters']:.2f}m H: {result['height_meters']:.2f}m D: {result['center_distance']:.2f}m"
                    cv2.putText(vis_image, size_info, (int(x1), int(y2) + 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Add legend
            cv2.putText(vis_image, "Red boxes: Detected objects", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(vis_image, "Green text: Metric size (meters)", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            
            return vis_image
    
    def create_demo_app():
        """Create Gradio web application for size estimation (fallback)."""
        print("✗ Gradio not available in fallback mode")
        return None
    
    def process_image(image: np.ndarray) -> Dict[str, Any]:
        """Process an image and return detection, depth, and size estimation results (fallback)."""
        # Load models
        yolo_model = load_yolo_model()
        depth_model = load_depth_model()
        
        # Detect objects
        detections = detect_objects(image, yolo_model)
        
        # Estimate depth
        depth_map = estimate_depth(image, depth_model)
        
        # Calculate metric size for each detection
        results = []
        for detection in detections:
            size_info = calculate_metric_size(detection["bbox"], depth_map, image.shape)
            result = {
                "detection": detection,
                "size_info": size_info
            }
            results.append(result)
        
        # Create visualization
        vis_image = create_visualization(image, detections, depth_map, results)
        
        return {
            "original_image": image,
            "detections": detections,
            "depth_map": depth_map,
            "size_results": results,
            "visualization": vis_image,
            "model_info": {
                "yolo_loaded": yolo_model is not None,
                "depth_loaded": depth_model is not None and depth_model.get("type") != "placeholder"
            }
        }


if __name__ == "__main__":
    # Import torch for device checking in fallback
    try:
        import torch
    except ImportError:
        print("Warning: Could not import torch for device detection")
        torch = None

    print("=" * 60)
    print("Size Estimation Prototype - CLI Version")
    print("=" * 60)
    
    # Command-line processing
    parser = argparse.ArgumentParser(description="Process image for size estimation")
    parser.add_argument("--image", type=str, help="Path to input image")
    parser.add_argument("--output", type=str, help="Path to output visualization")
    parser.add_argument("--format", type=str, choices=["json", "csv", "txt"], default="json", help="Output format")
    parser.add_argument("--yolo-model", type=str, help="Path to YOLO model file")
    parser.add_argument("--depth-model", type=str, help="Path to depth model file")
    
    args = parser.parse_args()
    
    if args.image:
        # Load image
        image = cv2.imread(args.image)
        if image is None:
            print(f"Error: Could not load image {args.image}")
            sys.exit(1)
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        print(f"Processing {args.image}...")
        start_time = time.time()
        results = process_image(image)
        processing_time = time.time() - start_time
        
        print(f"Processing completed in {processing_time:.2f} seconds")
        print(f"Detected {len(results['detections'])} objects")
        
        # Save visualization
        if args.output:
            cv2.imwrite(args.output, results["visualization"])
            print(f"Visualization saved to {args.output}")
        
        # Display results
        print("\nDetection Results:")
        for i, result in enumerate(results["size_results"]):
            det = result["detection"]
            size = result["size_info"]
            print(f"Object {i+1}: {det['class_name']} ({det['confidence']:.2f})")
            print(f"  Size: {size['width_meters']:.3f} x {size['height_meters']:.3f} x {size['center_distance']:.3f} meters")
            print(f"  Volume: {size['volume_cubic_meters']:.3f} cubic meters")
            print(f"  Confidence: {size['confidence']:.2f}")
        
        # Save detailed results if requested
        if args.format == "json":
            output_file = args.output or "results.json"
            with open(output_file, "w") as f:
                json.dump(results["size_results"], f, indent=2)
            print(f"Detailed results saved to {output_file}")
        elif args.format == "csv":
            output_file = args.output or "results.csv"
            with open(output_file, "w") as f:
                f.write("object_id,class,confidence,width_meters,height_meters,depth_meters,volume_cubic_meters,confidence_score\n")
                for i, result in enumerate(results["size_results"]):
                    det = result["detection"]
                    size = result["size_info"]
                    f.write(f"{i+1},{det['class_name']},{det['confidence']},{size['width_meters']},{size['height_meters']},{size['center_distance']},{size['volume_cubic_meters']},{size['confidence']}\n")
            print(f"Results saved to {output_file}")
        elif args.format == "txt":
            output_file = args.output or "results.txt"
            with open(output_file, "w") as f:
                f.write("Size Estimation Results\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Detected {len(results['detections'])} objects\n\n")
                for i, result in enumerate(results["size_results"]):
                    det = result["detection"]
                    size = result["size_info"]
                    f.write(f"Object {i+1}:\n")
                    f.write(f"  Class: {det['class_name']}\n")
                    f.write(f"  Confidence: {det['confidence']:.2f}\n")
                    f.write(f"  Size: {size['width_meters']:.3f} x {size['height_meters']:.3f} x {size['center_distance']:.3f} meters\n")
                    f.write(f"  Volume: {size['volume_cubic_meters']:.3f} cubic meters\n")
                    f.write(f"  Confidence: {size['confidence']:.2f}\n\n")
            print(f"Results saved to {output_file}")
        
        print("\nDone!")
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python cli.py --image input.jpg --output output.jpg")
        print("  python cli.py --image input.jpg --format json")
    
    print("=" * 60)

# Create __init__.py to make the directory a package
__init__.py = """
Size Estimation Package

This package provides tools for computer vision-based size and scale estimation.
It includes implementations for:
- Single-image size estimation using YOLO and depth models
- Ruler-based scale calibration
- Multi-view 3D reconstruction with scale recovery
- Real-time web interfaces for deployment

For more information, see the documentation and examples in the package.
"""
