import { MallData, MallAnalytics, CameraAnalytics } from "@/types"
import { config } from "./config"

const API_BASE_URL = config.api.baseUrl

export async function fetchMallAnalytics(mallId: number, token: string): Promise<MallAnalytics> {
  const response = await fetch(`${API_BASE_URL}/mall/${mallId}/analytics`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })

  if (!response.ok) {
    throw new Error("Failed to fetch mall analytics")
  }

  return response.json()
}

export async function fetchCameraAnalytics(mallId: number, token: string): Promise<CameraAnalytics[]> {
  const response = await fetch(`${API_BASE_URL}/mall/${mallId}/cameras/analytics`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })

  if (!response.ok) {
    throw new Error("Failed to fetch camera analytics")
  }

  return response.json()
}

export async function fetchRealTimeData(mallId: number, token: string): Promise<{
  activeVisitors: number
  currentPeakHour: boolean
}> {
  const response = await fetch(`${API_BASE_URL}/mall/${mallId}/realtime`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })

  if (!response.ok) {
    throw new Error("Failed to fetch real-time data")
  }

  return response.json()
} 