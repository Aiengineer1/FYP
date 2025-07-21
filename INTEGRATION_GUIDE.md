# 📚 InsightCart Backend API: Frontend Integration Guide

---

## 1. **Authentication & User Management (`/auth`)**

### **POST /auth/signup**
- **Purpose:** Register a new user.
- **Body:**  
  `{ "email": "...", "password": "...", "name": "..." }`
- **Response:**  
  `{ "id": 1, "email": "...", "name": "...", ... }`
- **Frontend:** Use for user registration.

---

### **POST /auth/login**
- **Purpose:** User login.
- **Body:**  
  `{ "email": "...", "password": "..." }`
- **Response:**  
  `{ "access_token": "...", "user_id": 1, "name": "...", "email": "...", "mall_id": ... }`
- **Frontend:** Save `access_token` for authenticated requests.

---

### **GET /auth/verify**
- **Purpose:** Verify JWT token.
- **Headers:**  
  `Authorization: Bearer <token>`
- **Response:**  
  `{ "valid": true, "user": { ... } }`
- **Frontend:** Use to check if user is logged in.

---

### **GET /auth/check-mall/{user_id}**
- **Purpose:** Check if user has a mall.
- **Frontend:** Use after login to check mall status.

---

### **GET /auth/user/me**
- **Purpose:** Get current user profile.
- **Headers:**  
  `Authorization: Bearer <token>`
- **Frontend:** Use to show user profile.

---

### **PUT /auth/user/update**
- **Purpose:** Update user profile.
- **Body:**  
  `{ "name": "...", "password": "...", ... }`
- **Frontend:** Use for profile update.

---

### **DELETE /auth/user/{user_id}**  
### **DELETE /auth/account/delete**
- **Purpose:** Delete user account.
- **Frontend:** Use for account deletion.

---

## 2. **Mall Management (`/mall`)**

### **POST /mall/create**
- **Purpose:** Create a new mall.
- **Form Data:**  
  - `name` (string)
  - `address` (string)
  - `user_id` (int)
  - `map_image` (file)
- **Frontend:** Use in admin/setup screens.

---

### **GET /mall/{mall_id}**
- **Purpose:** Get mall details.
- **Frontend:** Use to display mall info.

---

### **GET /mall/{mall_id}/image**
- **Purpose:** Get mall map image.
- **Frontend:** Use to display mall map.

---

### **PUT /mall/{mall_id}**
- **Purpose:** Update mall info.
- **Form Data:**  
  - Any of: `name`, `address`, `contact_email`, `contact_number`, `map_image`
- **Frontend:** Use for mall settings.

---

### **DELETE /mall/delete-my-mall**  
### **DELETE /mall/{mall_id}**
- **Purpose:** Delete mall.
- **Frontend:** Use for admin panel.

---

### **POST /mall/{mall_id}/setup**
- **Purpose:** Setup/configure mall.
- **Frontend:** Use for initial mall setup.

---

## 3. **Camera Management (`/camera`)**

### **POST /camera/add_camera**
- **Purpose:** Add a new camera.
- **Body:**  
  `{ "name": "...", "ip_address": "...", "username": "...", "password": "...", "location": "...", "mall_id": ... }`
- **Frontend:** Use in admin panel.

---

### **GET /camera/{camera_id}**
- **Purpose:** Get camera details.
- **Frontend:** Use to show camera info.

---

### **GET /camera/mall/{mall_id}/cameras**
- **Purpose:** List all cameras for a mall.
- **Frontend:** Use to show/select cameras.

---

### **PUT /camera/{camera_id}**
- **Purpose:** Update camera info.
- **Body:**  
  Same as add_camera.
- **Frontend:** Use for camera settings.

---

### **DELETE /camera/{camera_id}**
- **Purpose:** Delete camera.
- **Frontend:** Use for camera management.

---

### **POST /camera/camera/frame**
- **Purpose:** Get latest frame from camera.
- **Body:**  
  `{ "rtsp_url": "...", "camera_id": ... }`
- **Frontend:** Use for live preview.

---

### **GET /camera/{camera_id}/stream**  
### **GET /camera/{camera_id}/live**
- **Purpose:** Get live camera stream (JPEG/multipart).
- **Frontend:** Use for live video.

---

### **POST /camera/homography/save-mappings**
- **Purpose:** Save homography mappings for a camera.
- **Body:**  
  `{ "camera_id": ..., "zones": [...] }`
- **Frontend:** Use for mapping setup.

---

### **POST /camera/fov/update-zone**
- **Purpose:** Update FOV zone for a camera.
- **Body:**  
  `{ "camera_id": ..., "zone": {...} }`
- **Frontend:** Use for zone management.

---

### **DELETE /camera/fov/delete-zone/{camera_id}/{zone_name}**
- **Purpose:** Delete a FOV zone.
- **Frontend:** Use for zone management.

---

### **GET /camera/camera/{camera_id}/test-mappings**
- **Purpose:** Test camera mappings (returns diagnostic image).
- **Frontend:** Use for mapping verification.

---

## 4. **Analytics & Tracking (`/analytics`)**

### **GET /analytics/mall/{mall_id}**
- **Purpose:** Get comprehensive analytics for a mall.
- **Frontend:** Use for dashboard/analytics.

---

### **GET /analytics/realtime/{mall_id}**
- **Purpose:** Get real-time metrics.
- **Frontend:** Use for live dashboard.

---

### **GET /analytics/mall/{mall_id}/heatmap**
- **Purpose:** Get heatmap data.
- **Frontend:** Use for heatmap visualization.

---

### **GET /analytics/camera/{camera_id}/details**
- **Purpose:** Get analytics for a specific camera.
- **Frontend:** Use for camera analytics.

---

### **GET /analytics/system/status**
- **Purpose:** Get system-wide analytics status.
- **Frontend:** Use for admin/system health.

---

### **POST /analytics/camera/{camera_id}/start**  
### **POST /analytics/camera/{camera_id}/stop**
- **Purpose:** Start/stop camera processing.
- **Frontend:** Use for camera control.

---

### **POST /analytics/mall/{mall_id}/start_all_cameras**
- **Purpose:** Start all cameras in a mall.
- **Frontend:** Use for admin control.

---

### **POST /analytics/start-person-tracking/**
- **Purpose:** Start person tracking (default or selected camera).
- **Frontend:** Use to trigger tracking (e.g., via button).

---

### **WebSocket Endpoints**
- **/analytics/ws/mall/{mall_id}**: Real-time mall analytics.
- **/analytics/ws/camera/{camera_id}**: Real-time camera detections.
- **/analytics/ws/system**: System-wide status.
- **Frontend:** Use Socket.io or WebSocket client for live updates.

---

## 5. **Customer/Person Management (`/customer`)**

### **POST /customer/add_customer**
- **Purpose:** Add a new customer (for manual entry/testing).
- **Frontend:** Rarely used; mostly for admin/testing.

---

### **GET /customer/{customer_id}**
- **Purpose:** Get customer details.
- **Frontend:** Use to show tracked person details.

---

### **PUT /customer/{customer_id}**
- **Purpose:** Update customer info.
- **Frontend:** Use for admin/testing.

---

### **DELETE /customer/{customer_id}**
- **Purpose:** Delete customer.
- **Frontend:** Use for admin/testing.

---

## 6. **ID Management (`/id-management`)**

### **GET /id-management/statistics**
- **Purpose:** Get ID statistics for all models (gaps, efficiency, next IDs).
- **Frontend:** Use for admin/monitoring.

---

### **GET /id-management/next-available**
- **Purpose:** Get next available ID for each model.
- **Frontend:** Use for admin/monitoring.

---

### **GET /id-management/statistics/{model_name}**
- **Purpose:** Get ID stats for a specific model.
- **Frontend:** Use for admin/monitoring.

---

### **POST /id-management/reset-sequence/{model_name}**
- **Purpose:** Reset auto-increment sequence for a model.
- **Frontend:** Use for admin/maintenance.

---

### **GET /id-management/demo/scenario**
- **Purpose:** Demonstrate ID management scenario.
- **Frontend:** Use for admin/education.

---

## 7. **General Integration Notes**

- **Authentication:**  
  Always send `Authorization: Bearer <token>` for protected routes.
- **WebSocket:**  
  Use JWT token and mall_id as query params for real-time features.
- **Error Handling:**  
  Handle 400/401/403/500 errors gracefully in the UI.
- **Data Refresh:**  
  Use polling or WebSocket events to refresh analytics and tracking data in real time.

---

## 8. **Example Frontend Flow**

1. **User logs in** → Save JWT token.
2. **User selects mall/camera** → Fetch mall/camera list.
3. **User starts tracking** → Call `/analytics/start-person-tracking/`.
4. **Frontend connects to WebSocket** for live updates.
5. **Show analytics, heatmaps, and live detections** using `/analytics/mall/{mall_id}` and WebSocket events. 