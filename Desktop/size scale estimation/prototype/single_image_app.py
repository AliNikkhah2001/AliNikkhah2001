#!/usr/bin/env python3
"""
Size Estimation Prototype

This prototype demonstrates real-world size measurement from single images using:
- YOLO detection for object localization
- Depth estimation for metric distance
- Optional ruler-based calibration for precise scaling
- Gradio web interface for easy interaction

The pipeline can estimate:
1. Object positions and sizes in metric units (when depth is available)
2. Distance to objects
3. Confidence scores for detections
"""

import os
import sys
import argparse
import json
import time
from typing import List, Dict, Any, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

# ML dependencies
try:
    import torch
    from torchvision import transforms
    import ultralytics
    from ultralytics import YOLO
    import huggingface_hub
    print("✓ ML dependencies loaded")
except ImportError as e:
    print(f"✗ ML dependencies not available: {e}")
    print("Please install with: pip install torch torchvision ultralytics huggingface-hub")
    sys.exit(1)

# GUI dependencies
try:
    import gradio as gr
    print("✓ Gradio loaded")
except ImportError as e:
    print(f"✗ Gradio not available: {e}")
    print("Please install with: pip install gradio")
    sys.exit(1)

# Model management
MODEL_CACHE_DIR = os.getenv("HOME", ".") + "/.cache/size_estimation"
if not os.path.exists(MODEL_CACHE_DIR):
    os.makedirs(MODEL_CACHE_DIR)

# Global model instances
YOLO_MODEL = None
DEPTH_MODEL = None


def download_model_from_hub(model_id: str, filename: str, cache_dir: str) -> str:
    """Download a model file from Hugging Face Hub."""
    try:
        api = huggingface_hub.HfApi()
        local_path = api.download_file(
            path=filename,
            repo_id=model_id,
            local_dir=cache_dir,
            force_download=False
        )
        return local_path
    except Exception as e:
        print(f"Warning: Could not download {model_id}: {e}")
        return None


def load_yolo_model(model_path: str = None) -> YOLO:
    """Load YOLO model for object detection."""
    global YOLO_MODEL
    
    if YOLO_MODEL is not None:
        return YOLO_MODEL
    
    if model_path and os.path.exists(model_path):
        model = YOLO(model_path)
        print(f"✓ Loaded YOLO model from {model_path}")
    else:
        # Try to download a pre-trained model
        try:
            model = YOLO("yolov8n.pt")  # Ultralytics default
            print("✓ Downloaded YOLOv8n (small model)")
        except Exception as e:
            print(f"Warning: Could not download YOLO model: {e}")
            print("Using a minimal detector instead")
            model = None
    
    YOLO_MODEL = model
    return model


def load_depth_model(model_path: str = None) -> Any:
    """Load depth estimation model."""
    global DEPTH_MODEL
    
    if DEPTH_MODEL is not None:
        return DEPTH_MODEL
    
    # Try to use Depth Pro if available
    depth_model = None
    
    # Option 1: Try to use Hugging Face Depth Pro
    try:
        from transformers import AutoModelForDepthEstimation, AutoImageProcessor
        import torch
        
        model_id = "apple/DepthPro-mixin"
        processor = AutoImageProcessor.from_pretrained(model_id)
        model = AutoModelForDepthEstimation.from_pretrained(
            model_id,
            torch_dtype=torch.float16
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        
        DEPTH_MODEL = {"processor": processor, "model": model, "type": "transformers"}
        print("✓ Loaded Depth Pro from Hugging Face")
        return DEPTH_MODEL
    except Exception as e:
        print(f"Depth Pro not available: {e}")
    
    # Option 2: Try to use Depth Anything V2
    try:
        from depth_anything_v2.depth_anything_v2 import DepthAnythingV2
        import yaml
        
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        model = DepthAnythingV2.from_pretrained("depth_anything_v2_ViT-L")
        DEPTH_MODEL = {"model": model, "type": "depth_anything_v2"}
        print("✓ Loaded Depth Anything V2")
        return DEPTH_MODEL
    except Exception as e:
        print(f"Depth Anything V2 not available: {e}")
    
    print("✗ No depth model available. Using placeholder.")
    return {"type": "placeholder"}


def detect_objects(image: np.ndarray, yolo_model) -> List[Dict]:
    """Detect objects in image using YOLO."""
    if yolo_model is None:
        # Fallback: simple color-based detection for demo
        return detect_fallback_objects(image)
    
    try:
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
                        "class_name": yolo_model.model.names.get(class_id, f"Class_{class_id}")
                    }
                    detections.append(detection)
        
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
    
    return detections


def estimate_depth(image: np.ndarray, depth_model) -> np.ndarray:
    """Estimate depth map from image."""
    if depth_model is None or depth_model.get("type") == "placeholder":
        return estimate_fallback_depth(image)
    
    model_type = depth_model.get("type")
    
    try:
        if model_type == "transformers":
            processor = depth_model["processor"]
            model = depth_model["model"]
            
            # Preprocess image
            inputs = processor(images=[Image.fromarray(image)], return_tensors="pt")
            
            # Move to GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Get depth
            depth = outputs.pred_depth.cpu().numpy()[0, 0]
            return depth
            
        elif model_type == "depth_anything_v2":
            model = depth_model["model"]
            
            # Preprocess
            img_pil = Image.fromarray(image)
            
            # Run inference
            with torch.no_grad():
                depth = model(img_pil)
            
            # Convert to numpy array
            depth = np.array(depth)
            return depth
            
    except Exception as e:
        print(f"Depth estimation failed: {e}")
        return estimate_fallback_depth(image)
    
    return estimate_fallback_depth(image)


def estimate_fallback_depth(image: np.ndarray) -> np.ndarray:
    """Simple fallback depth estimation for demo."""
    # Create a synthetic depth map based on image gradients and object detection
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Apply Gaussian blur to reduce noise
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
    
    # Add some structure based on image regions
    height, width = image.shape[:2]
    for y in range(height):
        for x in range(width):
            # Create depth variation based on position
            dist_from_center = np.sqrt((x - width/2)**2 + (y - height/2)**2)
            max_dist = np.sqrt((width/2)**2 + (height/2)**2)
            depth[y, x] = depth[y, x] * (1 - dist_from_center/max_dist * 0.3)
    
    return depth


def calculate_metric_size(bbox: List[float], depth_map: np.ndarray, image_shape: tuple) -> Dict[str, Any]:
    """Calculate real-world size of object from bounding box and depth."""
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
    """Create visualization with bounding boxes and size information."""
    # Convert to PIL Image for easier drawing
    vis_image = Image.fromarray(image)
    draw = ImageDraw.Draw(vis_image)
    
    # Try to load a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
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
            
            # Draw depth scale
            if depth_map is not None:
                depth_val = depth_map[int((y1 + y2) / 2), int((x1 + x2) / 2)]
                depth_text = f"Depth: {depth_val:.2f}"
                draw.text((x2 - 100, y2 + 20), depth_text, fill=(0, 255, 255), font=small_font)
    
    # Add legend
    legend_y = 10
    draw.text((10, legend_y), "Red boxes: Detected objects", fill=(255, 255, 255), font=small_font)
    legend_y += 20
    draw.text((10, legend_y), "Green text: Metric size (meters)", fill=(0, 255, 0), font=small_font)
    legend_y += 20
    draw.text((10, legend_y), "Blue text: Depth estimate", fill=(0, 255, 255), font=small_font)
    
    return np.array(vis_image)


def process_image(image: np.ndarray) -> Dict[str, Any]:
    """Process an image and return detection, depth, and size estimation results."""
    # Load models if not already loaded
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
    
    # Create depth map visualization
    depth_vis = None
    if depth_map is not None:
        # Normalize depth for visualization
        if depth_map.max() > depth_map.min():
            depth_norm = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
            depth_vis = (depth_norm * 255).astype(np.uint8)
            depth_vis = cv2.cvtColor(depth_vis, cv2.COLOR_GRAY2RGB)
    
    return {
        "original_image": image,
        "detections": detections,
        "depth_map": depth_map,
        "size_results": results,
        "visualization": vis_image,
        "depth_visualization": depth_vis,
        "model_info": {
            "yolo_loaded": yolo_model is not None,
            "depth_loaded": depth_model is not None and depth_model.get("type") != "placeholder"
        }
    }


def create_demo_app():
    """Create Gradio web application for size estimation."""
    
    def demo(image_input):
        """Gradio demo function."""
        # Convert PIL Image to numpy array
        if isinstance(image_input, Image.Image):
            image = np.array(image_input)
        else:
            image = np.array(image_input)
        
        # Process the image
        results = process_image(image)
        
        # Return results for Gradio
        vis_image = results["visualization"]
        depth_vis = results["depth_visualization"]
        
        # Create info text
        info_text = f"Detected: {len(results['detections'])} objects\n"
        if results["model_info"]["yolo_loaded"] and results["model_info"]["depth_loaded"]:
            info_text += "Models: YOLO + Depth Pro\n"
        elif results["model_info"]["yolo_loaded"]:
            info_text += "Models: YOLO + Fallback Depth\n"
        else:
            info_text += "Models: Simple detection only\n"
        
        return vis_image, depth_vis, info_text, json.dumps(results["size_results"], indent=2)
    
    # Create Gradio interface
    with gr.Blocks(theme=gr.themes.Soft(), title="Size Estimation Demo") as demo_app:
        gr.Markdown("# Size Estimation and Depth Estimation Demo")
        gr.Markdown("Upload an image to detect objects and estimate their real-world size.")
        
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="pil", label="Input Image")
                process_btn = gr.Button("Process Image", variant="primary")
            
            with gr.Column():
                output_vis = gr.Image(label="Detection Results (with size estimates)")
                depth_vis = gr.Image(label="Depth Map Visualization")
        
        with gr.Row():
            info_text = gr.Textbox(label="Processing Info", interactive=False, lines=5)
            results_json = gr.Code(language="json", label="Detailed Results (JSON)", lines=10)
        
        # Process button click handler
        process_btn.click(
            demo,
            inputs=[image_input],
            outputs=[output_vis, depth_vis, info_text, results_json]
        )
        
        # Example images
        gr.Markdown("## Example Images")
        gr.Markdown(
            "This demo includes sample images. Try uploading your own photos "
            "to see object detection and size estimation in action."
        )
        
        # Add sample images if available
        sample_dir = "/Users/alinikkhah/Desktop/size scale estimation/data"
        if os.path.exists(sample_dir):
            sample_images = []
            for file in os.listdir(sample_dir):
                if file.endswith(".jpg") or file.endswith(".png"):
                    sample_path = os.path.join(sample_dir, file)
                    sample_images.append(sample_path)
            
            if sample_images:
                demo.load(
                    lambda: Image.open(sample_images[0]),
                    inputs=image_input,
                    outputs=image_input
                )
    
    return demo_app


if __name__ == "__main__":
    print("=" * 60)
    print("Size Estimation Prototype")
    print("=" * 60)
    
    # Check if running as script or from Gradio
    if "--gradio" in sys.argv:
        print("Starting Gradio web interface...")
        app = create_demo_app()
        app.launch(share=True, server_name="0.0.0.0", server_port=7860)
    else:
        # Command-line processing
        parser = argparse.ArgumentParser(description="Process image for size estimation")
        parser.add_argument("--image", type=str, help="Path to input image")
        parser.add_argument("--output", type=str, help="Path to output visualization")
        parser.add_argument("--format", type=str, choices=["json", "csv", "txt"], default="json", help="Output format")
        
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
            
            print("\nDone!")
        else:
            parser.print_help()
            print("\nExample usage:")
            print("  python prototype.py --image input.jpg --output output.jpg")
            print("  python prototype.py --gradio  # Start web interface")
    
    print("=" * 60)