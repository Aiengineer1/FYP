export interface Camera {
  id: number
  name: string
  location: string
  status: "active" | "inactive"
  mall_id: number
  created_at?: string
  updated_at?: string
  ip_address?: string
  username?: string
  password?: string
  rtsp_url?: string
  homography_map?: any
  fov_zones?: any
}

export interface MallAnalytics {
  totalVisitors: number
  activeVisitors: number
  averageDwellTime: number
  peakHours: string[]
  popularSections: {
    name: string
    visitorCount: number
  }[]
}

export interface CameraAnalytics {
  id: number
  name: string
  location: string
  status: "active" | "inactive"
  visitorCount: number
  lastActive: string
  healthStatus: "good" | "warning" | "critical"
}

export interface MallData {
  id: number
  name: string
  address: string
  created_at: string
  cameras: Camera[]
  analytics: MallAnalytics
}

// New types for enhanced functionality
export interface RealTimeMetrics {
  activeVisitors: number
  currentPeakHour: boolean
  timestamp?: string
}

export interface CameraDetails extends Camera {
  rtsp_url: string
  username: string
  password: string
  type: "entrance" | "tracking" | "shelf"
  lastActive: string
  fovZones: Array<{
    id: number
    name: string
    coordinates: number[][]
  }>
}

export interface DetectionEvent {
  person_id: string
  age: number
  gender: 'male' | 'female'
  zone: string
  confidence: number
  bbox: [number, number, number, number]
  timestamp: string
  camera_id: number
}

export interface AnalyticsFilter {
  timeRange: 'hour' | 'day' | 'week' | 'month'
  cameras: number[]
  zones: string[]
  ageGroups: string[]
  gender: 'all' | 'male' | 'female'
}

export interface HeatmapData {
  mallId: number
  zones: Array<{
    name: string
    visitorCount: number
    coordinates: number[][]
    density: number
  }>
  timestamp: string
}

export interface User {
  user_id: number
  name: string
  email: string
  mall_id: number | null
  created_at?: string
  updated_at?: string
}

export interface AuthUser extends User {
  token: string
}

export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

export interface PaginatedResponse<T = any> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

export interface ChartDataPoint {
  name: string
  value: number
  timestamp?: string
}

export interface VisitorStats {
  total: number
  male: number
  female: number
  averageAge: number
  ageGroups: {
    '18-25': number
    '26-35': number
    '36-45': number
    '46-55': number
    '55+': number
  }
} 