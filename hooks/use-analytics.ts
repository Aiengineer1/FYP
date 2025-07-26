import useSWR from 'swr'
import { apiClient } from '@/lib/api-client'
import { useAuthStore } from '@/stores/auth-store'
import { MallAnalytics, CameraAnalytics, RealTimeMetrics } from '@/types'

// Mock data for fallback
const mockAnalyticsData: MallAnalytics = {
    totalVisitors: 1245,
    activeVisitors: 45,
    averageDwellTime: 45,
    peakHours: ['10:00-11:00', '14:00-15:00', '18:00-19:00'],
    popularSections: [
        { name: 'Electronics', visitorCount: 320 },
        { name: 'Clothing', visitorCount: 290 },
        { name: 'Food Court', visitorCount: 245 },
        { name: 'Books', visitorCount: 180 },
        { name: 'Home & Garden', visitorCount: 210 },
    ],
}

const mockRealTimeMetrics: RealTimeMetrics = {
    activeVisitors: 45,
    currentPeakHour: false,
}

// Mock data for new endpoints
const mockHeatmapData = {
    mallId: 1,
    zones: [
        { name: "Electronics", visitors: 150, intensity: 0.8, coordinates: { x: 20, y: 30 } },
        { name: "Clothing", visitors: 200, intensity: 0.9, coordinates: { x: 60, y: 40 } },
        { name: "Food Court", visitors: 300, intensity: 1.0, coordinates: { x: 40, y: 70 } },
    ],
    timestamp: new Date().toISOString()
}

const mockSectionData = [
    { rack: "Rack 1", male: 45, female: 65, name: "Rack 1", section: "Electronics" },
    { rack: "Rack 2", male: 55, female: 40, name: "Rack 2", section: "Clothing" },
    { rack: "Rack 3", male: 35, female: 70, name: "Rack 3", section: "Food" },
]

const mockCustomerData = {
    total: 1245,
    male: 600,
    female: 645,
    averageAge: 32,
    ageGroups: {
        '18-25': 200,
        '26-35': 400,
        '36-45': 300,
        '46-55': 200,
        '55+': 145
    }
}

const mockAlertsData = [
    { id: 1, type: "high_traffic", message: "High traffic detected in Electronics section", severity: "warning", time: "2 min ago" },
    { id: 2, type: "queue_length", message: "Queue forming at checkout counter 3", severity: "info", time: "5 min ago" },
]

const mockTimeSeriesData = [
    { time: "09:00", visitors: 45, interactions: 120 },
    { time: "10:00", visitors: 78, interactions: 210 },
    { time: "11:00", visitors: 120, interactions: 340 },
    { time: "12:00", visitors: 200, interactions: 580 },
]

// SWR configuration
const swrConfig = {
    refreshInterval: 30000, // Refresh every 30 seconds
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
    errorRetryCount: 3,
    errorRetryInterval: 5000,
}

export function useAnalytics(mallId: number | null, timeRange?: string, filters?: any) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}${timeRange ? `?range=${timeRange}` : ''}` : null,
        () => mallId ? apiClient.getMallAnalytics(mallId, timeRange, filters) : null,
        {
            ...swrConfig,
            fallbackData: mockAnalyticsData, // Use mock data as fallback
            onError: (error) => {
                console.error('Error fetching analytics:', error)
            },
        }
    )

    return {
        analytics: data || mockAnalyticsData,
        isLoading,
        isError: error,
        refresh: mutate,
    }
}

export function useRealTimeMetrics(mallId: number | null) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}/realtime` : null,
        () => mallId ? apiClient.getRealTimeMetrics(mallId) : null,
        {
            refreshInterval: 5000, // Refresh every 5 seconds for real-time data
            revalidateOnFocus: true,
            fallbackData: mockRealTimeMetrics,
            onError: (error) => {
                console.warn('Real-time metrics endpoint not available, using fallback data:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        realTimeMetrics: data || mockRealTimeMetrics,
        isLoading: false, // Don't show loading when using fallback
        isError: false, // Don't show error when we have fallback data
        refresh: mutate,
    }
}

export function useHeatmapData(mallId: number | null, filters?: any) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}/heatmap` : null,
        () => mallId ? apiClient.getHeatmapData(mallId, filters) : null,
        {
            ...swrConfig,
            fallbackData: mockHeatmapData,
            onError: (error) => {
                console.warn('Heatmap data not available, using fallback:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        heatmapData: data || mockHeatmapData,
        isLoading: false,
        isError: false,
        refresh: mutate,
    }
}

export function useSectionAnalytics(mallId: number | null, filters?: any) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}/sections` : null,
        () => mallId ? apiClient.getSectionAnalytics(mallId, filters) : null,
        {
            ...swrConfig,
            fallbackData: mockSectionData,
            onError: (error) => {
                console.warn('Section analytics not available, using fallback:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        sectionData: data || mockSectionData,
        isLoading: false,
        isError: false,
        refresh: mutate,
    }
}

export function useCustomerInsights(mallId: number | null, filters?: any) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}/customers` : null,
        () => mallId ? apiClient.getCustomerInsights(mallId, filters) : null,
        {
            ...swrConfig,
            fallbackData: mockCustomerData,
            onError: (error) => {
                console.warn('Customer insights not available, using fallback:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        customerData: data || mockCustomerData,
        isLoading: false,
        isError: false,
        refresh: mutate,
    }
}

export function useAlerts(mallId: number | null, filters?: any) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}/alerts` : null,
        () => mallId ? apiClient.getAlerts(mallId, filters) : null,
        {
            refreshInterval: 10000, // Refresh every 10 seconds for alerts
            fallbackData: mockAlertsData,
            onError: (error) => {
                console.warn('Alerts not available, using fallback:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        alerts: data || mockAlertsData,
        isLoading: false,
        isError: false,
        refresh: mutate,
    }
}

export function useTimeSeriesData(mallId: number | null, filters?: any) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}/timeseries` : null,
        () => mallId ? apiClient.getTimeSeriesData(mallId, filters) : null,
        {
            ...swrConfig,
            fallbackData: mockTimeSeriesData,
            onError: (error) => {
                console.warn('Time series data not available, using fallback:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        timeSeriesData: data || mockTimeSeriesData,
        isLoading: false,
        isError: false,
        refresh: mutate,
    }
}

export function useCameraAnalytics(mallId: number | null) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/cameras/mall/${mallId}` : null,
        () => mallId ? apiClient.getCameraAnalytics(mallId) : null,
        {
            ...swrConfig,
            refreshInterval: 60000, // Refresh every minute for camera analytics
            onError: (error) => {
                console.warn('Camera analytics not available:', error.message)
            },
            shouldRetryOnError: false,
        }
    )

    return {
        cameraAnalytics: data || [],
        isLoading: false, // Don't show loading when no data available
        isError: false, // Don't show error when we can handle gracefully
        refresh: mutate,
    }
}

export function useMall(mallId: number | null) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/mall/${mallId}` : null,
        () => mallId ? apiClient.getMall(mallId) : null,
        {
            refreshInterval: 300000, // Refresh every 5 minutes
            revalidateOnFocus: false,
        }
    )

    return {
        mall: data,
        isLoading,
        isError: error,
        refresh: mutate,
    }
}

export function useCameras(mallId: number | null) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/mall/${mallId}/cameras` : null,
        () => mallId ? apiClient.getCameras(mallId) : null,
        {
            refreshInterval: 30000, // Refresh every 30 seconds
            revalidateOnFocus: true,
            onError: (error) => {
                console.warn('Cameras not available:', error.message)
            },
            shouldRetryOnError: false, // Don't retry on 404s
        }
    )

    return {
        cameras: data || [],
        isLoading: false, // Don't show loading when no data available
        isError: false, // Don't show error when we can handle gracefully
        refresh: mutate,
    }
}

export function useCamera(cameraId: number | null) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        cameraId && isAuthenticated ? `/camera/${cameraId}` : null,
        () => cameraId ? apiClient.getCamera(cameraId) : null,
        {
            refreshInterval: 60000, // Refresh every minute
            revalidateOnFocus: true,
        }
    )

    return {
        camera: data,
        isLoading,
        isError: error,
        refresh: mutate,
    }
} 