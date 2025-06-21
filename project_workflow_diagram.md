# 🏢 Mall Analytics System - Complete Workflow Diagram

## 📊 System Architecture Overview

```mermaid
graph TB
    subgraph "📹 Camera Layer"
        C1[Camera 1 - RTSP Stream]
        C2[Camera 2 - RTSP Stream]
        C3[Camera N - RTSP Stream]
    end
    
    subgraph "🖥️ Backend Processing Layer"
        subgraph "🎯 AI Detection Pipeline"
            YOLO[YOLOv8 Person Detection]
            AGE[Age/Gender Detection]
            TROLLEY[Trolley Detection]
            TRACKER[DeepSORT Tracker]
        end
        
        subgraph "🗄️ Data Processing"
            HOMO[Homography Mapping]
            ANALYTICS[Analytics Engine]
            LOGGER[Data Logger]
        end
        
        subgraph "🔐 Authentication & APIs"
            AUTH[JWT Authentication]
            API[FastAPI Endpoints]
            DB[(PostgreSQL Database)]
        end
    end
    
    subgraph "💻 Frontend Layer"
        DASH[Dashboard]
        ANALYTICS_UI[Analytics Page]
        CAMERA_UI[Camera Management]
        SETTINGS[Settings]
    end
    
    C1 --> YOLO
    C2 --> YOLO
    C3 --> YOLO
    
    YOLO --> AGE
    YOLO --> TROLLEY
    YOLO --> TRACKER
    
    AGE --> HOMO
    TROLLEY --> HOMO
    TRACKER --> HOMO
    
    HOMO --> ANALYTICS
    HOMO --> LOGGER
    
    LOGGER --> DB
    ANALYTICS --> DB
    
    DB --> API
    AUTH --> API
    
    API --> DASH
    API --> ANALYTICS_UI
    API --> CAMERA_UI
    API --> SETTINGS
```

## 🔄 Real-Time Data Flow

```mermaid
sequenceDiagram
    participant Camera as 📹 Camera
    participant Worker as 🖥️ Camera Worker
    participant AI as 🧠 AI Pipeline
    participant DB as 🗄️ Database
    participant API as 🔌 FastAPI
    participant Frontend as 💻 Frontend
    
    loop Every Frame (10 FPS)
        Camera->>Worker: RTSP Frame
        Worker->>AI: Process Frame
        
        AI->>AI: Person Detection
        AI->>AI: Age/Gender Detection
        AI->>AI: Trolley Detection
        AI->>AI: Tracking Update
        
        AI->>Worker: Detection Results
        Worker->>DB: Log Analytics Data
        
        Note over DB: Store: person_id, age, gender,<br/>trolley_status, zone, coordinates
    end
    
    loop Every 5 Seconds
        Frontend->>API: GET /analytics
        API->>DB: Query Analytics
        DB->>API: Analytics Data
        API->>Frontend: Real-time Stats
        
        Note over Frontend: Update: visitor count,<br/>dwell time, heatmap, demographics
    end
```

## 🎯 AI Detection Pipeline Workflow

```mermaid
flowchart TD
    A[📹 Camera Frame Input] --> B[🖼️ Frame Preprocessing]
    B --> C[👤 YOLOv8 Person Detection]
    
    C --> D{Person Detected?}
    D -->|Yes| E[🆔 DeepSORT Tracking]
    D -->|No| Z[⏭️ Next Frame]
    
    E --> F[👥 Age/Gender Detection]
    E --> G[🛒 Trolley Detection]
    
    F --> H[🗺️ Homography Mapping]
    G --> H
    
    H --> I[📍 Zone Assignment]
    I --> J[📊 Analytics Calculation]
    
    J --> K[💾 Database Logging]
    K --> L[🔄 Update Tracking]
    L --> M[⏭️ Next Frame]
    
    Z --> M
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
    style G fill:#fce4ec
    style H fill:#f1f8e9
    style K fill:#e3f2fd
```

## 🗄️ Database Schema Workflow

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email
        string password
        int mall_id FK
        datetime created_at
    }
    
    MALLS {
        int id PK
        string name
        string address
        binary map_image
        datetime created_at
    }
    
    CAMERAS {
        int id PK
        int mall_id FK
        string name
        string ip_address
        string username
        string password
        string location
        json homography_map
        json fov_zones
        datetime created_at
    }
    
    CUSTOMERS {
        int id PK
        int mall_id FK
        int age
        string gender
        datetime entry_time
        datetime exit_time
        string trolley_id
        string trolley_sub_id
        json routes
        json interactions
        json visited_zones
    }
    
    USERS ||--|| MALLS : "owns"
    MALLS ||--o{ CAMERAS : "has"
    MALLS ||--o{ CUSTOMERS : "tracks"
    CAMERAS ||--o{ CUSTOMERS : "monitors"
```

## 🔐 Authentication & API Workflow

```mermaid
flowchart LR
    subgraph "🔐 Authentication Flow"
        A[👤 User Login] --> B[🔑 JWT Token Generation]
        B --> C[📝 Token Storage]
        C --> D[🔒 API Request with Token]
        D --> E[✅ Token Validation]
        E --> F[📊 Data Access]
    end
    
    subgraph "🔌 API Endpoints"
        G[/auth/login] --> H[/auth/signup]
        I[/mall/create] --> J[/mall/{id}]
        K[/camera/add] --> L[/camera/{id}/live]
        M[/analytics] --> N[/customer/track]
    end
    
    F --> G
    F --> I
    F --> K
    F --> M
```

## 📊 Analytics Processing Workflow

```mermaid
flowchart TD
    A[📈 Raw Detection Data] --> B[🔄 Data Aggregation]
    
    B --> C[👥 Visitor Analytics]
    B --> D[⏱️ Dwell Time Analysis]
    B --> E[🗺️ Heatmap Generation]
    B --> F[🛒 Trolley Analytics]
    B --> G[👨‍👩‍👧‍👦 Demographics]
    
    C --> H[📊 Real-time Metrics]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I[💾 Database Storage]
    I --> J[🔌 API Response]
    J --> K[📱 Frontend Display]
    
    style A fill:#e3f2fd
    style H fill:#e8f5e8
    style K fill:#fff3e0
```

## 🎨 Frontend User Journey

```mermaid
journey
    title Mall Analytics Dashboard User Journey
    section Authentication
      Login: 5: User
      Dashboard: 5: User
    section Mall Management
      Create Mall: 4: User
      Upload Map: 4: User
      Configure Cameras: 3: User
    section Camera Setup
      Add Camera: 3: User
      Test Connection: 4: User
      Set FOV Zones: 2: User
    section Analytics
      View Real-time Stats: 5: User
      Check Heatmap: 4: User
      Analyze Demographics: 4: User
      Export Reports: 3: User
```

## 🔧 System Components Integration

```mermaid
graph LR
    subgraph "🎯 Core AI Models"
        YOLO[YOLOv8]
        SORT[DeepSORT]
        AGE[Age/Gender]
        TROLLEY[Trolley Detector]
    end
    
    subgraph "🖥️ Backend Services"
        WORKER[Camera Worker]
        ANALYTICS[Analytics Engine]
        API[FastAPI Server]
        DB[(PostgreSQL)]
    end
    
    subgraph "💻 Frontend"
        DASH[Dashboard]
        CHARTS[Charts]
        MAPS[Maps]
        SETTINGS[Settings]
    end
    
    YOLO --> WORKER
    SORT --> WORKER
    AGE --> WORKER
    TROLLEY --> WORKER
    
    WORKER --> ANALYTICS
    ANALYTICS --> DB
    DB --> API
    API --> DASH
    API --> CHARTS
    API --> MAPS
    API --> SETTINGS
```

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "🌐 Production Environment"
        subgraph "🖥️ Backend Server"
            API[FastAPI App]
            WORKER[Camera Workers]
            AI[AI Models]
        end
        
        subgraph "🗄️ Database"
            DB[(PostgreSQL)]
            REDIS[(Redis Cache)]
        end
        
        subgraph "📹 Camera Network"
            CAM1[Camera 1]
            CAM2[Camera 2]
            CAMN[Camera N]
        end
        
        subgraph "💻 Frontend"
            WEB[Web App]
            MOBILE[Mobile App]
        end
    end
    
    CAM1 --> WORKER
    CAM2 --> WORKER
    CAMN --> WORKER
    
    WORKER --> AI
    AI --> API
    API --> DB
    API --> REDIS
    
    DB --> API
    REDIS --> API
    
    API --> WEB
    API --> MOBILE
```

## 📋 Key Workflow Features

### 🔄 **Real-time Processing**
- **10 FPS** frame processing
- **Live analytics** updates every 5 seconds
- **Background workers** for each camera
- **Automatic cleanup** of inactive connections

### 🎯 **AI Pipeline**
- **Multi-stage detection**: Person → Age/Gender → Trolley → Tracking
- **Homography mapping**: Camera coordinates to mall map
- **Zone-based analytics**: FOV zone tracking
- **Route analysis**: Customer path tracking

### 📊 **Analytics Engine**
- **Real-time metrics**: Visitor count, dwell time, demographics
- **Heatmap generation**: Zone popularity visualization
- **Trolley analytics**: Shopping behavior insights
- **Historical data**: Trend analysis and reporting

### 🔐 **Security & Performance**
- **JWT authentication**: Secure API access
- **Connection pooling**: Database optimization
- **Error handling**: Graceful failure recovery
- **Caching**: Redis for performance

This workflow diagram shows the complete end-to-end system from camera input to frontend analytics display, highlighting all the key components and data flows in your mall analytics platform. 