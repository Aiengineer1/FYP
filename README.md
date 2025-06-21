# 🏢 InsightCart Mall Analytics Backend

## 🎯 Project Overview
**InsightCart** is a comprehensive mall analytics system that provides real-time visitor insights through AI-powered computer vision and analytics.

**Project Status**: ✅ **COMPLETE AND OPERATIONAL**  
**Timeline**: 21-day sprint (June 21 - July 15, 2025)  
**Current Phase**: Backend complete, ready for AI integration

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Virtual environment

### Installation
```bash
# Clone and setup
git clone <repository>
cd fyp_app_Backend

# Create virtual environment
python -m venv fyp_env
fyp_env\Scripts\activate  # Windows
# source fyp_env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start server
python run.py
```

Server will be available at: `http://localhost:8000`

## 🏗️ Architecture

### Core Components
- **FastAPI Backend**: Modern async REST API
- **PostgreSQL Database**: Analytics data storage
- **Socket.io Integration**: Real-time bidirectional communication
- **AI Detection Pipeline**: YOLOv11n + tracking + demographics
- **Analytics Engine**: Real-time metrics and insights

### Key Features
- 🎯 **Real-time person detection and tracking**
- 👥 **Age and gender estimation**
- 🛒 **Shopping trolley detection and tracking**
- 📊 **Zone-based analytics and heatmaps**
- 📈 **Live dashboard with comprehensive metrics**
- 🔐 **JWT authentication and security**

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration  
- `GET /auth/verify` - Token validation

### Analytics
- `GET /analytics/mall/{id}` - Complete mall analytics
- `GET /analytics/realtime/{id}` - Real-time dashboard metrics
- `GET /analytics/mall/{id}/heatmap` - Heatmap visualization

### Real-time WebSockets
- `ws://localhost:8000/analytics/ws/mall/{id}` - Live mall analytics
- `ws://localhost:8000/analytics/ws/camera/{id}` - Camera detections
- **Socket.io**: `ws://localhost:8000/socket.io/` - Frontend integration

## 🔧 Configuration

### Environment Variables
Copy `backend.env.example` to `.env` and configure:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/retail_analytics

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 👥 Team & Responsibilities

- **Ghulam**: Backend/Frontend Integration
- **Saim**: AI/ML Development  
- **Maheen**: Documentation & Presentation

## 📚 Documentation

### Current Documentation (Updated June 21, 2025)
- `PROJECT_COMPLETION_SUMMARY.md` - Complete implementation overview
- `SOCKETIO_IMPLEMENTATION_STATUS.md` - Real-time communication details
- `SOCKETIO_VERSION_FIX.md` - Technical compatibility resolution
- `FRONTEND_INTEGRATION_GUIDE.md` - Frontend integration instructions
- `project_workflow_diagram.md` - System architecture diagrams

### AI Integration
- `app/ai_solutions/modules/README_FOR_SAIM.md` - AI module requirements

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/
```

### WebSocket Test
```bash
curl "http://localhost:8000/socket.io/?EIO=4&transport=polling"
```

### API Test
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'
```

## 📊 Current Status

### ✅ Completed Features
- [x] Complete FastAPI backend infrastructure
- [x] PostgreSQL database with Alembic migrations
- [x] JWT authentication system
- [x] Real-time Socket.io integration
- [x] Analytics engine with live calculations
- [x] Camera worker for RTSP processing
- [x] WebSocket broadcasting (5-second intervals)
- [x] Frontend-compatible API responses
- [x] Production-ready error handling

### 🔄 In Progress
- [ ] AI module integration (Saim's responsibility)
- [ ] Frontend integration testing
- [ ] Production deployment preparation

## 🚀 Next Steps

1. **AI Integration**: Saim to implement detection modules
2. **Frontend Testing**: Begin real-time integration
3. **Performance Optimization**: Monitor and scale
4. **Production Deployment**: Staging environment setup

## 📞 Support

For technical issues or questions:
- Backend: Check `PROJECT_COMPLETION_SUMMARY.md`
- Socket.io: Check `SOCKETIO_IMPLEMENTATION_STATUS.md`
- Integration: Check `FRONTEND_INTEGRATION_GUIDE.md`

---

**🎊 Backend implementation complete! Ready for next development phase.**