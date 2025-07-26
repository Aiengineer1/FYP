# 🚀 AI Modules Flexible Pipeline - Usage Guide

## 📋 Overview

The AI Modules Final Year Project now provides **maximum flexibility** for running the camera tracking system in various modes:

- **Individual Camera Mode** - Run one camera in isolation
- **Single Camera Mode** - Run one camera with registry (for future expansion)
- **Multi-Camera Mode** - Run all available cameras together
- **Custom Camera Selection** - Choose specific cameras to run together
- **Command Line Interface** - Full CLI support for automation

## 🎯 Available Execution Methods

### 1. **Interactive Main Script** (`main_flexible.py`)
The most user-friendly way to run the system with guided prompts.

### 2. **Command Line Pipeline** (`flexible_pipeline.py`)
Advanced CLI interface for automation and scripting.

### 3. **Quick Start Script** (`quick_start.py`)
Guided setup with system validation.

### 4. **Original Main Script** (`main.py`)
Legacy version with basic functionality.

## 🎮 Interactive Usage

### **Method 1: Flexible Main Script**
```bash
python main_flexible.py
```

**Features:**
- ✅ Interactive mode selection
- ✅ Camera validation
- ✅ Real-time performance monitoring
- ✅ Automatic analytics generation
- ✅ User-friendly prompts

**Mode Options:**
1. **Individual Camera Mode** - Isolated tracking (no registry)
2. **Single Camera Mode** - With registry for future expansion
3. **Multi-Camera Mode** - All available cameras
4. **Custom Camera Selection** - Choose specific cameras

### **Method 2: Quick Start Script**
```bash
python quick_start.py
```

**Features:**
- ✅ System validation
- ✅ Prerequisites checking
- ✅ Guided setup
- ✅ Error handling

## ⚡ Command Line Usage

### **Method 3: Flexible Pipeline CLI**
```bash
# List available cameras
python flexible_pipeline.py --list-cameras

# Run system test first
python flexible_pipeline.py --test --mode multi

# Individual camera mode
python flexible_pipeline.py --mode individual --cameras cam1

# Single camera mode
python flexible_pipeline.py --mode single --cameras cam2

# Multi-camera mode (all available)
python flexible_pipeline.py --mode multi

# Custom camera selection
python flexible_pipeline.py --mode multi --cameras cam1 cam3 cam4

# With custom floorplan
python flexible_pipeline.py --mode multi --floorplan my_floorplan.png

# With duration limit (30 seconds)
python flexible_pipeline.py --mode multi --duration 30

# Camera groups (run different combinations)
python flexible_pipeline.py --mode group --cameras "cam1,cam2" "cam3,cam4"
```

## 🔧 Configuration Options

### **Environment-Based Configuration**
```bash
# Development mode (more verbose logging)
export ENVIRONMENT=development
python main_flexible.py

# Production mode (minimal logging)
export ENVIRONMENT=production
python main_flexible.py
```

### **Custom Configuration**
Edit `config.py` to customize:
- Camera RTSP URLs
- Model paths
- Tracking parameters
- Performance settings

## 📊 Operation Modes Explained

### **1. Individual Camera Mode**
- **Purpose**: Test a single camera in isolation
- **Registry**: ❌ No global registry
- **Use Case**: Development, testing, debugging
- **Benefits**: Fast startup, no cross-camera dependencies

```bash
python main_flexible.py
# Select Mode 1
# Choose camera (e.g., cam1)
```

### **2. Single Camera Mode**
- **Purpose**: Run one camera with registry for future expansion
- **Registry**: ✅ Global registry enabled
- **Use Case**: Single camera deployment with future multi-camera capability
- **Benefits**: Person tracking with global IDs

```bash
python main_flexible.py
# Select Mode 2
# Choose camera (e.g., cam2)
```

### **3. Multi-Camera Mode**
- **Purpose**: Run all available cameras with cross-camera person tracking
- **Registry**: ✅ Global registry with person re-identification
- **Use Case**: Full surveillance system
- **Benefits**: Complete person tracking across cameras

```bash
python main_flexible.py
# Select Mode 3
# All available cameras will be used
```

### **4. Custom Camera Selection**
- **Purpose**: Choose specific cameras to run together
- **Registry**: ✅ Global registry for selected cameras
- **Use Case**: Partial system deployment, testing specific combinations
- **Benefits**: Flexible camera selection

```bash
python main_flexible.py
# Select Mode 4
# Enter camera names (e.g., cam1 cam3)
```

## 🧪 Testing and Validation

### **System Test**
```bash
python test_system.py
```

**Tests:**
- ✅ Module imports
- ✅ Model files
- ✅ Mapping files
- ✅ Floorplan validation
- ✅ Registry functionality
- ✅ Zone analysis
- ✅ YOLO models
- ✅ Configuration validation

### **Quick Validation**
```bash
python quick_start.py --help
```

## 📈 Performance Monitoring

### **Real-Time Metrics**
- FPS per camera
- Frame drop rates
- Registry statistics
- Overlap events
- Lighting conditions

### **Performance Reports**
Automatically generated:
- `performance_report.json` - Detailed metrics
- `performance_report_dev.json` - Development mode
- `performance_report_prod.json` - Production mode

## 📊 Analytics Output

### **Generated Files**
- `person_routes_camX.json` - Person movement data
- `heatmap_overlay_camX.png` - Movement heatmaps
- `person_object_interaction_camX.png` - Interaction charts
- `age_object_interaction_camX.png` - Age-based analysis

## 🔍 Troubleshooting

### **Common Issues**

1. **Camera Connection Failed**
   ```bash
   # Check RTSP URLs in config.py
   # Verify network connectivity
   # Test with individual camera mode first
   ```

2. **Mapping Files Missing**
   ```bash
   # Run homography mapping tool
   python homo_applied_6111.py
   ```

3. **Model Files Not Found**
   ```bash
   # Verify all .pt files are in project directory
   python test_system.py
   ```

4. **Low Performance**
   ```bash
   # Use individual camera mode for testing
   # Check GPU availability
   # Adjust tracking parameters in config.py
   ```

### **Debug Mode**
```bash
# Enable debug logging
export ENVIRONMENT=development
python main_flexible.py
```

## 🚀 Advanced Usage

### **Automation Scripts**
```bash
#!/bin/bash
# Run different camera combinations
python flexible_pipeline.py --mode group --cameras "cam1,cam2" "cam3,cam4" --duration 60
```

### **Scheduled Execution**
```bash
# Cron job example
0 9 * * * cd /path/to/project && python flexible_pipeline.py --mode multi --duration 3600
```

### **Integration with Other Systems**
```bash
# Output to specific directory
python flexible_pipeline.py --mode multi --output-dir /var/www/analytics
```

## 📋 Best Practices

### **For Development**
1. Start with individual camera mode
2. Use system test before running
3. Monitor performance metrics
4. Check logs for errors

### **For Production**
1. Use production configuration
2. Set appropriate duration limits
3. Monitor system resources
4. Regular performance reports

### **For Testing**
1. Use camera groups mode
2. Test different combinations
3. Validate analytics output
4. Check cross-camera tracking

## 🎯 Use Case Examples

### **Research/Development**
```bash
# Test individual components
python flexible_pipeline.py --mode individual --cameras cam1 --duration 30
```

### **Single Camera Deployment**
```bash
# Deploy to single location
python flexible_pipeline.py --mode single --cameras cam2
```

### **Multi-Camera Surveillance**
```bash
# Full system deployment
python flexible_pipeline.py --mode multi
```

### **Custom Configuration**
```bash
# Specific camera combination
python flexible_pipeline.py --mode multi --cameras cam1 cam3 cam4
```

## 🔄 Migration from Old System

### **From main.py to main_flexible.py**
1. **Backup**: Keep original `main.py`
2. **Test**: Run `test_system.py`
3. **Migrate**: Use `main_flexible.py` for new features
4. **Validate**: Compare outputs

### **Configuration Migration**
1. **Update**: Edit `config.py` with your settings
2. **Validate**: Run configuration validation
3. **Test**: Use quick start script
4. **Deploy**: Use flexible pipeline

## 📞 Support

### **Getting Help**
1. Run system test: `python test_system.py`
2. Check logs for errors
3. Use debug mode: `export ENVIRONMENT=development`
4. Review this usage guide

### **Common Commands Reference**
```bash
# System validation
python test_system.py

# Quick start
python quick_start.py

# Interactive mode
python main_flexible.py

# Command line mode
python flexible_pipeline.py --help

# List cameras
python flexible_pipeline.py --list-cameras
```

---

**🎉 The flexible pipeline system provides maximum control and ease of use for all your AI camera tracking needs!** 