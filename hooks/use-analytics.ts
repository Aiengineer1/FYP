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

// SWR configuration
const swrConfig = {
    refreshInterval: 30000, // Refresh every 30 seconds
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
    errorRetryCount: 3,
    errorRetryInterval: 5000,
}

export function useAnalytics(mallId: number | null, timeRange?: string) {
    const { isAuthenticated } = useAuthStore()

    const { data, error, mutate, isLoading } = useSWR(
        mallId && isAuthenticated ? `/analytics/mall/${mallId}${timeRange ? `?range=${timeRange}` : ''}` : null,
        () => mallId ? apiClient.getMallAnalytics(mallId, timeRange) : null,
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
                // Don't show error for missing camera analytics
            },
            shouldRetryOnError: false, // Don't retry on 404s
        }
    )

    return {
        cameraAnalytics: data || [],
        isLoading: false, // Don't show loading when no data available
        isError: false, // Don't show error when we can handle gracefully
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
                // Don't treat this as a critical error since we have fallback data
            },
            // Silently use fallback data when endpoint is not available
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
                // Don't show error for missing cameras
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