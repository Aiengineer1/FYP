 
## Multi-Camera Person Tracking and Analytics System

A sophisticated AI-powered surveillance system that performs real-time person detection, tracking, age/gender classification, and behavioral analytics across multiple cameras.

## 🚀 Features

### Core Capabilities
- **Multi-Camera Person Detection** using YOLOv11
- **Real-time Person Tracking** with embedding-based re-identification
- **Cross-Camera Person Matching** using ResNet50 embeddings
- **Age & Gender Classification** with 93% accuracy
- **Face Detection & Recognition** using YOLOv11n-face
- **Object Interaction Analysis** and duration tracking
- **Heatmap Generation** from person movement patterns
- **Zone-based Analytics** with homography transformations

### Advanced Features
- **Dynamic Similarity Thresholds** based on lighting conditions
- **Atomic Person Registration** to prevent race conditions
- **Automatic Memory Cleanup** for optimal performance
- **Real-time Performance Monitoring** with FPS tracking
- **Quality-based Overlap Detection** between camera zones
- **Comprehensive Analytics** and visualization

## 📁 Project Structure

```
AI MODULES FINAL1.2/
├── main.py                          # Main orchestrator
├── camera_tracker.py                # Camera processing threads
├── tracking_core.py                 # Core tracking logic
├── registry.py                      # Global person registry
├── zone_utils.py                    # Geometric utilities
├── config.py                        # Configuration management
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── homo_applied_6111.py            # Homography mapping tool
├── *.json                          # Camera mapping files
├── *.pt                            # AI model files
└── *.png                           # Output visualizations
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenCV 4.8+
- PyTorch 2.0+
- CUDA (optional, for GPU acceleration)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_MODULES_FINAL1.2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify model files**
   Ensure the following model files are present:
   - `person_detect_yolov11.pt` (5.2MB)
   - `yolo11n-seg.pt` (5.9MB)
   - `yolov11n-face.pt` (5.2MB)
   - `ResNet-18 Age 0.60 + Gender 93.pt` (43MB)

4. **Configure cameras**
   - Update `config.py` with your camera RTSP URLs
   - Create homography mapping files for each camera using `homo_applied_6111.py`

## 🎯 Usage

### Quick Start

1. **Run the main application**
   ```bash
   python main.py
   ```

2. **Select mode**
   - **Mode 1**: Single camera tracking
   - **Mode 2**: Multi-camera tracking

3. **Provide floorplan image**
   - Enter the path to your mall/floorplan image
   - The system will use this for coordinate mapping

### Camera Configuration

#### Single Camera Mode
```bash
# Select camera when prompted
Enter camera name or number (e.g., 1, cam1, ...): cam1
```

#### Multi-Camera Mode
```bash
# All available cameras will be used automatically
# Overlap analysis will be performed
```

### Homography Mapping

Use the interactive mapping tool to set up camera zones:

```bash
python homo_applied_6111.py
```

This tool allows you to:
- Select camera and floorplan
- Define global zones for each camera
- Map objects and interaction areas
- Save mappings to JSON files

## 🔧 Configuration

### Camera Settings
Edit `config.py` to customize:

```python
CAMERA_RTSP = {
    'cam1': 'rtsp://your-camera-url',
    # Add more cameras...
}

CAMERA_OFFSETS = {
    'cam1': {'x_offset': 250, 'y_offset': -120},
    # Adjust offsets for each camera...
}
```

### Tracking Parameters
```python
TRACKING = {
    'embedding_similarity_threshold': 0.88,
    'memory_duration': 250,
    'fps_log_interval': 30,
}
```

### Registry Settings
```python
REGISTRY = {
    'similarity_threshold': 0.75,
    'history_size': 5,
    'cleanup_interval': 300,  # seconds
}
```

## 📊 Analytics & Outputs

### Generated Files
- **`person_routes_camX.json`**: Detailed person movement data
- **`heatmap_overlay_camX.png`**: Movement heatmap visualization
- **`person_object_interaction_camX.png`**: Interaction bar charts
- **`age_object_interaction_camX.png`**: Age-based interaction analysis
- **`performance_report.json`**: System performance metrics

### Analytics Features
- **Person Route Tracking**: Complete movement paths
- **Interaction Duration**: Time spent near objects
- **Age/Gender Distribution**: Demographic analysis
- **Zone Occupancy**: Area utilization patterns
- **Cross-Camera Transitions**: Person movement between cameras

## 🔍 Performance Monitoring

The system provides real-time performance metrics:

```
==================================================
PERFORMANCE SUMMARY
==================================================
Runtime: 120.5 seconds
Total frames processed: 3600
Total frames dropped: 45
Drop rate: 1.25%
Overlap events: 12

Average FPS by Camera:
  cam1: 29.8 FPS
  cam2: 30.1 FPS
  cam3: 28.9 FPS
  cam4: 29.5 FPS

Registry Statistics:
  Total persons tracked: 8
  Supervisor distribution: {'cam1': 3, 'cam2': 2, 'cam3': 2, 'cam4': 1}
  Lighting conditions: {'cam1': 'normal', 'cam2': 'bright', 'cam3': 'normal', 'cam4': 'low_light'}
==================================================
```

## 🚨 Troubleshooting

### Common Issues

1. **Model files not found**
   ```
   Error: Model file not found: person_detect_yolov11.pt
   ```
   **Solution**: Ensure all model files are in the project directory

2. **Camera connection failed**
   ```
   Error: Failed to capture frame from RTSP stream
   ```
   **Solution**: Check RTSP URLs and network connectivity

3. **Mapping files missing**
   ```
   Warning: Mapping file for cam1 not found. Skipping this camera.
   ```
   **Solution**: Create homography mappings using `homo_applied_6111.py`

4. **Low FPS performance**
   - Reduce frame resolution in `config.py`
   - Enable GPU acceleration with CUDA
   - Adjust tracking parameters

### Performance Optimization

1. **GPU Acceleration**
   ```bash
   # Install CUDA-enabled PyTorch
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Memory Management**
   - Adjust `cleanup_interval` in registry settings
   - Monitor memory usage with performance reports

3. **Frame Processing**
   - Reduce `fps_log_interval` for less frequent logging
   - Adjust `age_gender_skip` for faster processing

## 🔬 Technical Details

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Camera 1      │    │   Camera 2      │    │   Camera N      │
│   (Thread)      │    │   (Thread)      │    │   (Thread)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Global Person Registry  │
                    │   (Thread-Safe)           │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Analytics Generator     │
                    │   (Heatmaps, Charts)      │
                    └───────────────────────────┘
```

### AI Models Used

1. **YOLOv11 Person Detection**
   - Model: `person_detect_yolov11.pt`
   - Purpose: Real-time person detection
   - Performance: High accuracy, real-time processing

2. **YOLOv11n Segmentation**
   - Model: `yolo11n-seg.pt`
   - Purpose: Person segmentation and tracking
   - Performance: Precise boundary detection

3. **YOLOv11n Face Detection**
   - Model: `yolov11n-face.pt`
   - Purpose: Face detection for age/gender analysis
   - Performance: Robust face detection

4. **ResNet-18 Age/Gender**
   - Model: `ResNet-18 Age 0.60 + Gender 93.pt`
   - Purpose: Age and gender classification
   - Performance: 93% gender accuracy, 60% age accuracy

5. **ResNet-50 Embeddings**
   - Purpose: Person re-identification
   - Performance: Cross-camera person matching

### Key Algorithms

1. **Embedding Similarity**
   ```python
   similarity = np.dot(emb1_norm, emb2_norm)
   ```

2. **Homography Transformation**
   ```python
   H, _ = cv2.findHomography(src_pts, dst_pts)
   mapped_pt = cv2.perspectiveTransform(pt, H)
   ```

3. **Dynamic Threshold Adjustment**
   ```python
   adaptive_threshold = base_threshold + lighting_adjustment
   ```

## 📈 Future Enhancements

### Planned Features
- **Web Dashboard**: Real-time monitoring interface
- **Database Integration**: Persistent storage for analytics
- **Alert System**: Real-time notifications for events
- **Mobile App**: Remote monitoring capabilities
- **Advanced Analytics**: Machine learning insights

### Research Opportunities
- **Behavioral Analysis**: Anomaly detection
- **Crowd Density Estimation**: Occupancy analytics
- **Predictive Analytics**: Movement forecasting
- **Privacy-Preserving AI**: Federated learning

## 🤝 Contributing

This is a Final Year Project. For academic use:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is developed for academic purposes as part of a Final Year Project.

## 👨‍💻 Author

**Final Year Project Student**
- **University**: [Your University]
- **Department**: [Your Department]
- **Supervisor**: [Your Supervisor]

## 🙏 Acknowledgments

- **Ultralytics**: YOLO models and framework
- **OpenCV**: Computer vision library
- **PyTorch**: Deep learning framework
- **Academic Community**: Research and development support

---

**Note**: This system is designed for research and educational purposes. Ensure compliance with privacy laws and ethical guidelines when deploying in real-world scenarios.