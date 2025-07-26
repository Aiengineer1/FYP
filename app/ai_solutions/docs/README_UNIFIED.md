# 🤖 AI Modules Final Year Project - Unified System

## 🎯 **Unified Multi-Camera Person Tracking and Analytics System**

This is the **complete, unified solution** that combines all functionality from the previous files into one powerful system.

---

## 🚀 **Quick Start**

### **Interactive Mode (Recommended)**
```bash
python main_unified.py
```

### **Command Line Mode**
```bash
# List available cameras
python main_unified.py --list-cameras

# Run single camera
python main_unified.py --mode single --cameras cam1

# Run multi-camera
python main_unified.py --mode multi

# Run with duration limit
python main_unified.py --mode multi --duration 300

# Run with custom floorplan
python main_unified.py --mode multi --floorplan my_floorplan.png
```

---

## 📋 **System Modes**

### **1. Individual Camera Mode**
- **Purpose**: Isolated tracking without registry
- **Use Case**: Testing single camera, debugging
- **Features**: Person detection, tracking, analytics
- **Registry**: ❌ Disabled

### **2. Single Camera Mode**
- **Purpose**: Single camera with registry for future expansion
- **Use Case**: Production single camera deployment
- **Features**: Person detection, tracking, registry, analytics
- **Registry**: ✅ Enabled

### **3. Multi-Camera Mode**
- **Purpose**: Multiple cameras with shared registry
- **Use Case**: Production multi-camera deployment
- **Features**: Person detection, tracking, cross-camera matching, analytics
- **Registry**: ✅ Enabled

### **4. Custom Camera Selection**
- **Purpose**: Select specific cameras for multi-camera mode
- **Use Case**: Testing specific camera combinations
- **Features**: All multi-camera features with custom selection
- **Registry**: ✅ Enabled

---

## 🔧 **System Features**

### **🎯 Core AI Capabilities**
- **Person Detection**: YOLO-based real-time detection
- **Face Detection**: Face detection and analysis
- **Age/Gender Classification**: ResNet-based classification
- **Person Tracking**: Multi-object tracking with embeddings
- **Cross-Camera Matching**: Global person registry
- **Zone Analysis**: Overlap detection and validation

### **📊 Analytics & Visualization**
- **Heatmaps**: Person movement heatmaps
- **Route Analysis**: Individual person routes
- **Interaction Analysis**: Person-object interactions
- **Age-based Analytics**: Age group interaction patterns
- **Performance Monitoring**: Real-time system metrics

### **⚙️ Performance Features**
- **Real-time Processing**: Live video stream processing
- **Multi-threading**: Concurrent camera processing
- **Memory Management**: Efficient object memory
- **Performance Monitoring**: FPS, drop rates, statistics
- **Duration Limits**: Configurable runtime limits

---

## 🛠️ **Installation & Setup**

### **1. Prerequisites**
```bash
# Install dependencies
pip install -r requirements.txt
```

### **2. Model Files**
Ensure these model files are in the project directory:
- `person_detect_yolov11.pt` - Person detection model
- `yolo11n-seg.pt` - Segmentation model
- `yolov11n-face.pt` - Face detection model
- `ResNet-18 Age 0.60 + Gender 93.pt` - Age/Gender classification

### **3. Configuration Files**
- `homography_mappings_cam1.json` - Camera 1 mapping
- `homography_mappings_cam4.json` - Camera 4 mapping
- `floorplan_gui.png` - Floorplan image

### **4. System Test**
```bash
# Test system configuration
python test_main.py

# Test basic functionality
python test_simple.py
```

---

## 📖 **Usage Examples**

### **Example 1: Interactive Multi-Camera Mode**
```bash
python main_unified.py
# Select mode 3 (Multi-Camera)
# System will automatically detect and use all available cameras
```

### **Example 2: Command Line Single Camera**
```bash
python main_unified.py --mode single --cameras cam1 --duration 600
# Runs cam1 for 10 minutes
```

### **Example 3: Custom Multi-Camera**
```bash
python main_unified.py --mode multi --cameras cam1 cam4 --duration 1800
# Runs cam1 and cam4 for 30 minutes
```

### **Example 4: System Testing**
```bash
# Test system first
python main_unified.py --test

# List available cameras
python main_unified.py --list-cameras
```

---

## 📊 **Output Files**

### **Analytics Outputs**
- `heatmap_overlay_cam1.png` - Person movement heatmap
- `person_object_interaction_cam1.png` - Interaction charts
- `age_object_interaction_cam1.png` - Age-based analytics
- `person_routes_cam1.json` - Person route data

### **Performance Reports**
- `performance_report.json` - System performance metrics
- Console output with real-time statistics

---

## 🔍 **System Architecture**

### **Core Components**
```
main_unified.py
├── UnifiedAISystem
│   ├── PerformanceMonitor
│   ├── GlobalPersonRegistry
│   └── CameraTracker(s)
├── Interactive Mode
├── Command Line Mode
└── Analytics Generation
```

### **Data Flow**
```
Camera Streams → Person Detection → Tracking → Registry → Analytics
     ↓              ↓              ↓         ↓         ↓
  RTSP URLs    YOLO Models   Embeddings  Cross-Match  Reports
```

---

## ⚡ **Performance Optimization**

### **Recommended Settings**
- **CPU**: Multi-core processor (4+ cores)
- **RAM**: 8GB+ for multi-camera mode
- **GPU**: Optional (CUDA support available)
- **Network**: Stable RTSP connections

### **Configuration Tuning**
- Adjust `similarity_threshold` in config for matching sensitivity
- Modify `memory_duration` for tracking persistence
- Tune `fps_log_interval` for performance monitoring

---

## 🐛 **Troubleshooting**

### **Common Issues**

**1. Camera Connection Failed**
```bash
# Check RTSP URLs in config.py
# Verify network connectivity
# Test with VLC player first
```

**2. Model Loading Errors**
```bash
# Verify model files exist
# Check file permissions
# Ensure correct model paths
```

**3. Performance Issues**
```bash
# Reduce number of cameras
# Lower resolution settings
# Check system resources
```

### **Debug Mode**
```bash
# Enable debug output
python main_unified.py --test
```

---

## 📈 **Advanced Features**

### **Custom Analytics**
- Modify analytics functions in `UnifiedAISystem`
- Add new chart types
- Custom data processing

### **API Integration**
- Extend for web API
- Database integration
- Real-time dashboards

### **Scalability**
- Horizontal scaling support
- Load balancing
- Distributed processing

---

## 🎉 **Success Indicators**

### **✅ System Working Correctly**
- Real-time person detection
- Smooth tracking
- Cross-camera matching
- Analytics generation
- Performance monitoring

### **📊 Expected Outputs**
- Heatmaps showing person movement
- Interaction charts
- Performance reports
- Route data files

---

## 🔄 **Migration from Old Files**

### **Replaced Files**
- ❌ `main.py` - Basic functionality
- ❌ `flexible_pipeline.py` - Pipeline functionality  
- ❌ `main_flexible.py` - Interactive functionality

### **New Unified File**
- ✅ `main_unified.py` - All functionality combined

### **Migration Steps**
1. Use `main_unified.py` instead of old files
2. Update any scripts calling old files
3. Test with new unified system
4. Remove old files after verification

---

## 📞 **Support**

### **System Status**
- ✅ **Fully Functional**
- ✅ **All Modes Working**
- ✅ **Analytics Complete**
- ✅ **Performance Optimized**

### **Next Steps**
1. Deploy to production
2. Monitor performance
3. Scale as needed
4. Add custom features

---

**🎯 This unified system provides everything needed for a production-ready AI camera tracking and analytics solution!** 