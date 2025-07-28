# Mall Analytics API - Route Reference

This document provides a comprehensive overview of all API endpoints available in the backend, including authentication, mall management, camera operations, customer management, analytics, and ID management. Each section lists the route, HTTP method, parameters, expected responses, and a brief description.

---

## 1. Authentication Routes (`/auth`)

### POST `/auth/signup`
- **Purpose:** Register a new user.
- **Request Body:** `UserCreate` (name, email, password, etc.)
- **Response:** `UserResponse` (user details)
- **Errors:** 400 (Email exists), 500 (Creation failed)

### POST `/auth/login`
- **Purpose:** Authenticate user and return JWT token.
- **Request Body:** `UserLogin` (email, password)
- **Response:** `LoginResponse` (access_token, user_id, name, email, mall_id)
- **Errors:** 400 (Invalid credentials), 500 (Unexpected error)

### GET `/auth/check-mall/{user_id}`
- **Purpose:** Check if a user is associated with a mall.
- **Response:** `MallStatusResponse`
- **Errors:** 404 (User not found)

### GET `/auth/verify`
- **Purpose:** Verify JWT token and return user data.
- **Response:** `{valid: bool, user: {...}}`
- **Errors:** 401 (Invalid token)

### POST `/auth/refresh-token`
- **Purpose:** Refresh/extend JWT token expiration time.
- **Response:** New access token with extended expiration
- **Errors:** 401 (Invalid token), 500 (Refresh failed)

### DELETE `/auth/user/{user_id}`
- **Purpose:** Delete a specific user and their mall (self-deletion only).
- **Response:** Success message
- **Errors:** 403 (Not allowed), 404 (User not found), 500 (Failed)

### DELETE `/auth/account/delete`
- **Purpose:** Delete the current user's account and mall.
- **Response:** Success message
- **Errors:** 404 (Not found), 500 (Failed)

### GET `/auth/user/me`
- **Purpose:** Get current user's profile.
- **Response:** `UserResponse`
- **Errors:** 404 (User not found), 500 (Failed)

### PUT `/auth/user/update`
- **Purpose:** Update current user's profile.
- **Request Body:** `UserUpdate`
- **Response:** `UserResponse`
- **Errors:** 400 (No update data), 404 (User not found), 500 (Failed)

---

## 2. Mall Routes (`/mall`)

### POST `/mall/create`
- **Purpose:** Create a new mall for a user.
- **Request:** Form data (name, address, user_id, map_image)
- **Response:** `MallResponse`
- **Errors:** 404 (User not found), 400 (Already has mall or invalid image), 500 (Failed)

### GET `/mall/{mall_id}`
- **Purpose:** Get mall details.
- **Response:** `MallResponse`
- **Errors:** 404 (Mall not found), 500 (Failed)

### GET `/mall/{mall_id}/cameras`
- **Purpose:** Get all cameras for a mall.
- **Response:** List[`CameraResponse`]
- **Errors:** 500 (Failed)

### GET `/mall/{mall_id}/cameras/{camera_id}`
- **Purpose:** Get a specific camera by ID within a mall.
- **Response:** `CameraResponse`
- **Errors:** 404 (Camera not found), 500 (Failed)

### GET `/mall/{mall_id}/image`
- **Purpose:** Get mall map image.
- **Response:** Image (JPEG)
- **Errors:** 404 (Mall or image not found), 500 (Failed)

### PUT `/mall/{mall_id}`
- **Purpose:** Update mall details.
- **Request:** Form data (optional fields)
- **Response:** `MallResponse`
- **Errors:** 404 (Mall not found), 500 (Failed)

### DELETE `/mall/delete-my-mall`
- **Purpose:** Delete current user's mall.
- **Response:** Success message
- **Errors:** 404 (No mall), 500 (Failed)

### DELETE `/mall/{mall_id}`
- **Purpose:** Delete a mall (owner only).
- **Response:** Success message
- **Errors:** 403 (Not owner), 404 (Mall not found), 500 (Failed)

### POST `/mall/{mall_id}/setup`
- **Purpose:** Setup/configure a mall.
- **Request:** Form data (optional fields)
- **Response:** `MallResponse`
- **Errors:** 404 (Mall not found), 500 (Failed)

---

## 3. Camera Routes (`/camera`)

### POST `/camera/frame`
- **Purpose:** Get latest camera frame (for polling).
- **Request Body:** `{rtsp_url: str, camera_id: int (optional)}`
- **Response:** JPEG image
- **Errors:** 400 (Missing RTSP), 404 (Not available), 500 (Failed)

### POST `/camera/add_camera`
- **Purpose:** Add a new camera.
- **Request Body:** `CameraCreate`
- **Response:** `CameraResponse`

### GET `/camera/{camera_id}`
- **Purpose:** Get camera details.
- **Response:** `CameraResponse`
- **Errors:** 404 (Not found)

### GET `/camera/mall/{mall_id}/cameras`
- **Purpose:** List all cameras for a mall.
- **Response:** List[`CameraResponse`]

### PUT `/camera/{camera_id}`
- **Purpose:** Update camera details.
- **Request Body:** `CameraCreate`
- **Response:** `CameraResponse`
- **Errors:** 400 (Missing fields), 404 (Not found), 500 (Failed)

### DELETE `/camera/{camera_id}`
- **Purpose:** Delete a camera.
- **Response:** Success message

### GET `/camera/{camera_id}/stream`
- **Purpose:** Get optimized camera stream.
- **Query:** `quality` (low, medium, high)
- **Response:** Streaming JPEG

### GET `/camera/{camera_id}/live`
- **Purpose:** Get live camera stream (multipart JPEG).
- **Response:** Streaming JPEG

### POST `/camera/homography/save-mappings`
- **Purpose:** Save homography mappings for a camera.
- **Request Body:** `HomographyMappingRequest`
- **Response:** Success message

### POST `/camera/fov/update-zone`
- **Purpose:** Update FOV zone for a camera.
- **Request Body:** `FOVZoneRequest`
- **Response:** Success message

### DELETE `/camera/fov/delete-zone/{camera_id}/{zone_name}`
- **Purpose:** Delete a FOV zone from a camera.
- **Response:** Success message

### GET `/camera/{camera_id}/test-mappings`
- **Purpose:** Test camera homography mappings.
- **Response:** Streaming JPEG

---

## 4. Customer Routes (`/customer`)

### POST `/add_customer`
- **Purpose:** Add a new customer.
- **Request Body:** `CustomerCreate`
- **Response:** `CustomerResponse`

### GET `/{customer_id}`
- **Purpose:** Get customer details.
- **Response:** `CustomerResponse`
- **Errors:** 404 (Not found)

### PUT `/{customer_id}`
- **Purpose:** Update customer details.
- **Request Body:** `CustomerCreate`
- **Response:** `CustomerResponse`
- **Errors:** 404 (Not found)

### DELETE `/{customer_id}`
- **Purpose:** Delete a customer.
- **Response:** Success message

---

## 5. Analytics Routes (`/analytics`)

### GET `/analytics/mall/{mall_id}`
- **Purpose:** Get comprehensive analytics for a mall.
- **Query:** `range`, `gender`, `ageGroup`, `zone`, `cameraId`
- **Response:** `MallAnalytics`

### GET `/analytics/mall/{mall_id}/realtime`
- **Purpose:** Get real-time metrics for a mall.
- **Response:** `RealTimeMetrics`

### GET `/analytics/mall/{mall_id}/heatmap`
- **Purpose:** Get heatmap data for a mall.
- **Query:** `range`, `gender`, `ageGroup`, `timeOfDay`, `zone`
- **Response:** `HeatmapData`

### GET `/analytics/mall/{mall_id}/sections`
- **Purpose:** Get section/rack analytics.
- **Query:** `range`, `gender`, `ageGroup`, `section`, `rack`
- **Response:** List[`SectionAnalytics`]

### GET `/analytics/mall/{mall_id}/customers`
- **Purpose:** Get customer insights for a mall.
- **Query:** `range`, `gender`, `ageGroup`
- **Response:** `CustomerStats`

### GET `/analytics/mall/{mall_id}/cameras`
- **Purpose:** List all cameras for a mall (analytics view).
- **Response:** List of camera info

### GET `/analytics/cameras/mall/{mall_id}`
- **Purpose:** Get camera analytics for a mall.
- **Response:** List[`CameraAnalytics`]

### GET `/analytics/mall/{mall_id}/alerts`
- **Purpose:** Get alerts for a mall.
- **Query:** `since`, `zone`, `severity`
- **Response:** List[`Alert`]

### GET `/analytics/mall/{mall_id}/timeseries`
- **Purpose:** Get time series data for a mall.
- **Query:** `metric`, `range`, `zone`, `cameraId`
- **Response:** List[`TimeSeriesPoint`]

### GET `/analytics/system/status`
- **Purpose:** Get system status.
- **Response:** System status info

### POST `/analytics/camera/{camera_id}/start`
- **Purpose:** Start camera processing.
- **Response:** Success message

### POST `/analytics/camera/{camera_id}/stop`
- **Purpose:** Stop camera processing.
- **Response:** Success message

### POST `/analytics/mall/{mall_id}/start_all_cameras`
- **Purpose:** Start all cameras for a mall.
- **Response:** Success message

### WebSocket `/analytics/ws/analytics/{mall_id}`
- **Purpose:** Real-time analytics updates for a mall.

### WebSocket `/analytics/ws/camera/{camera_id}`
- **Purpose:** Real-time camera updates.

### WebSocket `/analytics/ws/system`
- **Purpose:** System-wide real-time updates.

---

## 6. ID Management Routes (`/id-management`)

### GET `/id-management/statistics`
- **Purpose:** Get ID statistics for all models.
- **Response:** Statistics summary

### GET `/id-management/next-available`
- **Purpose:** Get next available ID for each model.
- **Response:** Next IDs

### GET `/id-management/statistics/{model_name}`
- **Purpose:** Get ID statistics for a specific model.
- **Response:** Model statistics
- **Errors:** 400 (Invalid model)

### POST `/id-management/reset-sequence/{model_name}`
- **Purpose:** Reset auto-increment sequence for a model.
- **Response:** Success message
- **Errors:** 400 (Invalid model)

### GET `/id-management/demo/scenario`
- **Purpose:** Demonstrate ID management scenario.
- **Response:** Scenario explanation

---

## 7. General/Root Routes

### GET `/`
- **Purpose:** API root. Returns a welcome message.

### GET `/health`
- **Purpose:** Health check endpoint.
- **Response:** `{status: "healthy", message: "API is operational"}`

---

## Notes on Route Conflicts & Overlaps

- **Camera Endpoints:** `/camera` and `/analytics/camera` both operate on cameras but serve different purposes (CRUD vs. analytics/control). Ensure frontend uses correct base path.
- **Mall Endpoints:** `/mall` and `/analytics/mall` are distinct: `/mall` is for CRUD, `/analytics/mall` is for analytics data.
- **Authentication:** All `/auth` endpoints are for user management and authentication. No overlap with other modules.
- **ID Management:** All `/id-management` endpoints are for backend admin/maintenance use.
- **WebSocket Endpoints:** All analytics WebSocket endpoints are under `/analytics/ws/`.

---

## Usage
- All endpoints (except `/`, `/health`, `/auth/signup`, `/auth/login`) require authentication via JWT Bearer token.
- For file uploads (e.g., mall map), use `multipart/form-data`.
- For WebSocket endpoints, use a compatible WebSocket client.

---

*This document is auto-generated from code and may require updates if routes change.*
