export interface Camera {
  id: number
  name: string
  location: string
  status: "active" | "inactive"
  mall_id: number
  created_at?: string
  updated_at?: string
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