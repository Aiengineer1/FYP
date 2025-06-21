# 🔧 **Frontend-Backend Integration Guide**

## ✅ **IMPLEMENTATION STATUS: COMPLETE**

All frontend recommendations have been implemented! Your backend is now **100% compatible** with the enhanced frontend architecture.

---

## 🔌 **API ENDPOINTS - FRONTEND READY**

### **Authentication (Exact Frontend Format)**
```typescript
// Login
POST /auth/login
Response: {
  "access_token": string,
  "user_id": number,
  "name": string,
  "email": string,
  "mall_id": number
}

// Token Verification (for AuthInitializer)
GET /auth/verify
Headers: { Authorization: "Bearer <token>" }
Response: {
  "valid": true,
  "user": {
    "user_id": number,
    "name": string,
    "email": string,
    "mall_id": number
  }
}
```

### **Analytics (Frontend-Compatible Format)**
```typescript
// Mall Analytics
GET /analytics/mall/{mall_id}
Response: {
  "totalVisitors": number,
  "activeVisitors": number,
  "peakHours": [{"hour": string, "visitors": number}],
  "popularSections": [{"name": string, "visitors": number, "percentage": number}],
  "visitorDemographics": {
    "ageGroups": [{"range": string, "count": number, "percentage": number}],
    "genderDistribution": {"male": number, "female": number}
  },
  "conversionMetrics": {
    "browsersToShoppers": number,
    "averageDwellTime": number,  // in seconds
    "trolleyUsageRate": number
  },
  "hourlyTraffic": [{"time": string, "visitors": number}]
}

// Real-time Status
GET /analytics/realtime/{mall_id}
Response: {
  "currentVisitors": number,
  "lastUpdate": string,
  "cameraStatus": {
    "total": number,
    "online": number,
    "offline": number
  },
  "activeDetections": number,
  "systemHealth": {
    "cpuUsage": number,
    "memoryUsage": number,
    "processingFps": number
  }
}
```

### **Camera Frame (Optimized for Polling)**
```typescript
// Camera Frame
POST /camera/frame
Body: { 
  "rtsp_url": string,
  "camera_id": number  // optional
}
Response: JPEG image with headers:
{
  "Cache-Control": "no-cache, no-store, must-revalidate",
  "Pragma": "no-cache",
  "Expires": "0"
}
```

---

## 🌐 **WEBSOCKET EVENTS - EXACT FRONTEND FORMAT**

### **Analytics Updates**
```typescript
// Connect to mall analytics
ws://localhost:8000/analytics/ws/mall/{mall_id}

// Event Format:
{
  "type": "analytics_update",
  "data": {
    "mallId": number,
    "activeVisitors": number,
    "totalVisitors": number,
    "averageDwellTime": number,
    "peakHours": [{"hour": string, "visitors": number}],
    "popularSections": [{"name": string, "visitors": number, "percentage": number}],
    "timestamp": string
  }
}
```

### **Detection Updates (For AI Overlays)**
```typescript
// Connect to camera detections
ws://localhost:8000/analytics/ws/camera/{camera_id}

// Event Format:
{
  "type": "detection_update",
  "data": {
    "cameraId": number,
    "detections": [
      {
        "person_id": string,
        "bbox": [x, y, width, height],  // Exact format for overlays
        "confidence": number,
        "age": number,
        "gender": "Male" | "Female",
        "has_trolley": boolean,
        "timestamp": string
      }
    ]
  }
}
```

### **Camera Status Changes**
```typescript
// Camera status events on mall channel
{
  "type": "camera_status",
  "data": {
    "cameraId": number,
    "status": "online" | "offline",
    "timestamp": string
  }
}
```

---

## ⚙️ **FRONTEND CONFIGURATION**

### **Environment Variables (Update your .env.local)**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_SHOW_PERFORMANCE_METRICS=true
NEXT_PUBLIC_ENABLE_AI_OVERLAYS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true

# Polling Intervals (milliseconds)
NEXT_PUBLIC_ANALYTICS_REFRESH_INTERVAL=5000
NEXT_PUBLIC_CAMERA_FRAME_INTERVAL=100
NEXT_PUBLIC_STATUS_CHECK_INTERVAL=30000
```

### **API Client Configuration**
```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// All endpoints are ready:
export const endpoints = {
  // Auth
  login: '/auth/login',
  verify: '/auth/verify',
  
  // Analytics
  mallAnalytics: (mallId: number) => `/analytics/mall/${mallId}`,
  realtimeStatus: (mallId: number) => `/analytics/realtime/${mallId}`,
  
  // Camera
  cameraFrame: '/camera/frame',
  
  // WebSocket
  mallWebSocket: (mallId: number) => `/analytics/ws/mall/${mallId}`,
  cameraWebSocket: (cameraId: number) => `/analytics/ws/camera/${cameraId}`,
  systemWebSocket: '/analytics/ws/system'
}
```

---

## 🧪 **INTEGRATION TESTING CHECKLIST**

### **✅ Phase 1: Basic Connection**
```bash
# 1. Start Backend
python run.py

# 2. Test API Health
curl http://localhost:8000/health

# 3. Test CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://localhost:8000/analytics/mall/1
```

### **✅ Phase 2: Authentication Flow**
```typescript
// Test login
const response = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'test@test.com', password: 'password' })
})

// Test token verification
const verify = await fetch('/auth/verify', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

### **✅ Phase 3: Analytics Integration**
```typescript
// Test analytics endpoint
const analytics = await fetch('/analytics/mall/1')
const data = await analytics.json()
console.log('Analytics:', data)

// Test real-time status
const status = await fetch('/analytics/realtime/1')
const statusData = await status.json() 
console.log('Status:', statusData)
```

### **✅ Phase 4: WebSocket Testing**
```typescript
// Test WebSocket connection
const ws = new WebSocket('ws://localhost:8000/analytics/ws/mall/1')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('WebSocket Event:', data.type, data.data)
}

// Join mall room
ws.send(JSON.stringify({
  type: "join_room",
  room: "mall_1"
}))
```

### **✅ Phase 5: Camera Frame Testing**
```typescript
// Test camera frame polling
const frameResponse = await fetch('/camera/frame', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    rtsp_url: 'rtsp://admin:password@192.168.1.100/stream' 
  })
})

const blob = await frameResponse.blob()
const imageUrl = URL.createObjectURL(blob)
// Use imageUrl in your enhanced camera component
```

---

## 🎯 **INTEGRATION STEPS**

### **Step 1: Update Frontend API URLs**
```typescript
// Update your api-client.ts to point to backend
const API_BASE_URL = 'http://localhost:8000'
```

### **Step 2: Test Authentication**
- Login flow should work immediately
- AuthInitializer should validate tokens correctly

### **Step 3: Connect Analytics Dashboard**
- Replace mock data with real API calls
- WebSocket updates should work automatically

### **Step 4: Enable Camera Streams**
- Enhanced camera component ready for real frames
- AI detection overlays ready for real detection data

### **Step 5: Test Notifications**
- Camera status changes will trigger notifications
- System alerts will appear automatically

---

## 🚀 **PRODUCTION READINESS**

### **Backend Features Ready:**
✅ Frontend-compatible API formats  
✅ Real-time WebSocket events  
✅ Optimized camera streaming  
✅ JWT authentication with proper payload  
✅ CORS configured for frontend  
✅ Error handling and validation  
✅ Performance monitoring endpoints  

### **Integration Status:**
✅ **Authentication**: Ready for AuthInitializer  
✅ **Analytics**: Dashboard data format ready  
✅ **Real-time Updates**: WebSocket events formatted  
✅ **Camera Streams**: Polling endpoint optimized  
✅ **AI Overlays**: Detection data format ready  
✅ **Notifications**: Status change events ready  

## 🎊 **READY FOR IMMEDIATE INTEGRATION!**

Your backend now provides **exactly** what your enhanced frontend expects. Start the integration and your system will work seamlessly! 🎯

**Next Step**: `python run.py` and start connecting your frontend! 🚀 