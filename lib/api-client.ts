import { MallAnalytics, CameraAnalytics, CameraDetails, RealTimeMetrics } from "@/types"
import { config, getApiUrl } from './config'
import { performanceMonitor } from './performance'

// Custom error class for API errors
export class APIError extends Error {
    constructor(public status: number, message: string, public data?: any) {
        super(message)
        this.name = 'APIError'
    }
}

// API client configuration using centralized config
const API_CONFIG = {
    baseURL: config.api.baseUrl,
    timeout: config.api.timeout,
    retries: config.api.retryAttempts,
    retryDelay: config.api.retryDelay,
}

class APIClient {
    private baseURL: string
    private timeout: number
    private retries: number
    private retryDelay: number

    constructor() {
        this.baseURL = API_CONFIG.baseURL
        this.timeout = API_CONFIG.timeout
        this.retries = API_CONFIG.retries
        this.retryDelay = API_CONFIG.retryDelay
    }

    private async getAuthToken(): Promise<string | null> {
        if (typeof window === 'undefined') return null
        return localStorage.getItem('token')
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {},
        retryCount = 0
    ): Promise<T> {
        const token = await this.getAuthToken()
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), this.timeout)

        // Start performance monitoring
        const metricName = `API_${options.method || 'GET'}_${endpoint.replace(/[^a-zA-Z0-9]/g, '_')}`
        performanceMonitor.start(metricName, 'api', {
            endpoint,
            method: options.method || 'GET',
            retryCount,
        })

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { Authorization: `Bearer ${token}` }),
                    ...options.headers,
                },
                ...options,
            })

            clearTimeout(timeoutId)

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`
                let errorData = null

                try {
                    errorData = await response.json()
                    errorMessage = errorData.detail || errorData.message || errorMessage
                } catch {
                    // Response is not JSON, use status text
                }

                // Handle specific status codes
                if (response.status === 401) {
                    // Token expired, clear auth data
                    if (typeof window !== 'undefined') {
                        localStorage.removeItem('token')
                        localStorage.removeItem('user')
                        window.location.href = '/login'
                    }
                }

                throw new APIError(response.status, errorMessage, errorData)
            }

            // Handle different content types
            const contentType = response.headers.get('content-type')
            if (contentType?.includes('application/json')) {
                return response.json()
            } else if (contentType?.includes('image/')) {
                return response.blob() as T
            } else {
                return response.text() as T
            }

        } catch (error) {
            clearTimeout(timeoutId)

            // End performance monitoring on error
            performanceMonitor.end(metricName)

            // Retry logic for network errors
            if (retryCount < this.retries &&
                (error instanceof TypeError || error.name === 'AbortError')) {
                await new Promise(resolve => setTimeout(resolve, this.retryDelay * (retryCount + 1)))
                return this.request<T>(endpoint, options, retryCount + 1)
            }

            if (error instanceof APIError) {
                throw error
            }

            // Network or other errors
            throw new APIError(0, error instanceof Error ? error.message : 'Network error')
        } finally {
            // Ensure performance monitoring ends
            performanceMonitor.end(metricName)
        }
    }

    // Authentication endpoints
    async login(email: string, password: string) {
        return this.request<{
            access_token: string
            user_id: number
            name: string
            email: string
            mall_id: number | null
        }>('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        })
    }

    async signup(name: string, email: string, password: string) {
        return this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        })
    }

    async verifyToken() {
        return this.request('/auth/verify')
    }

    // Mall endpoints
    async getMall(mallId: number) {
        return this.request(`/mall/${mallId}`)
    }

    async createMall(mallData: FormData) {
        return this.request('/mall/create', {
            method: 'POST',
            headers: {}, // Don't set Content-Type for FormData
            body: mallData,
        })
    }

    async getMallImage(mallId: number): Promise<Blob> {
        return this.request<Blob>(`/mall/${mallId}/image`)
    }

    async deleteMall(mallId: number) {
        return this.request(`/mall/${mallId}`, {
            method: 'DELETE',
        })
    }

    async deleteMyMall() {
        return this.request('/mall/delete-my-mall', {
            method: 'DELETE',
        })
    }

    // Analytics endpoints - matching your backend implementation
    async getMallAnalytics(mallId: number, timeRange?: string): Promise<MallAnalytics> {
        const params = timeRange ? `?range=${timeRange}` : ''
        return this.request<MallAnalytics>(`/analytics/mall/${mallId}${params}`)
    }

    async getCameraAnalytics(cameraId: number): Promise<CameraAnalytics> {
        return this.request<CameraAnalytics>(`/analytics/camera/${cameraId}`)
    }

    async getRealTimeMetrics(mallId: number): Promise<RealTimeMetrics> {
        try {
            return this.request<RealTimeMetrics>(`/analytics/mall/${mallId}/realtime`)
        } catch (error) {
            // If the endpoint doesn't exist yet, return mock data gracefully
            if (error instanceof APIError && error.status === 404) {
                console.warn('Real-time metrics endpoint not implemented yet, using mock data')
                return {
                    activeVisitors: Math.floor(Math.random() * 50) + 20, // Random 20-70
                    currentPeakHour: new Date().getHours() >= 10 && new Date().getHours() <= 20,
                    timestamp: new Date().toISOString()
                }
            }
            throw error
        }
    }

    async getHeatmapData(mallId: number): Promise<any> {
        return this.request(`/analytics/mall/${mallId}/heatmap`)
    }

    async getSystemStatus(): Promise<{ processing_time: number; fps: number; queue_size: number }> {
        return this.request('/analytics/system/status')
    }

    // Camera control endpoints
    async startCameraProcessing(cameraId: number): Promise<any> {
        return this.request(`/analytics/camera/${cameraId}/start`, {
            method: 'POST',
        })
    }

    async stopCameraProcessing(cameraId: number): Promise<any> {
        return this.request(`/analytics/camera/${cameraId}/stop`, {
            method: 'POST',
        })
    }

    // Camera endpoints
    async getCameras(mallId: number) {
        return this.request(`/mall/${mallId}/cameras`)
    }

    async getCamera(cameraId: number): Promise<CameraDetails> {
        return this.request<CameraDetails>(`/camera/${cameraId}`)
    }

    async createCamera(mallId: number, cameraData: any) {
        return this.request(`/mall/${mallId}/cameras`, {
            method: 'POST',
            body: JSON.stringify(cameraData),
        })
    }

    async updateCamera(cameraId: number, cameraData: any) {
        return this.request(`/camera/${cameraId}`, {
            method: 'PUT',
            body: JSON.stringify(cameraData),
        })
    }

    async deleteCamera(cameraId: number) {
        return this.request(`/camera/${cameraId}`, {
            method: 'DELETE',
        })
    }

    async getCameraFrame(rtspUrl: string): Promise<Blob> {
        return this.request<Blob>('/camera/frame', {
            method: 'POST',
            body: JSON.stringify({ rtsp_url: rtspUrl }),
        })
    }

    // Homography mapping endpoints
    async saveHomographyMapping(cameraId: number, mappingData: any) {
        return this.request(`/camera/${cameraId}/homography`, {
            method: 'POST',
            body: JSON.stringify(mappingData),
        })
    }

    async getHomographyMapping(cameraId: number) {
        return this.request(`/camera/${cameraId}/homography`)
    }

    // User settings endpoints
    async updateUserProfile(userData: any) {
        return this.request('/user/profile', {
            method: 'PUT',
            body: JSON.stringify(userData),
        })
    }

    async updatePassword(currentPassword: string, newPassword: string) {
        return this.request('/user/password', {
            method: 'PUT',
            body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
        })
    }

    async deleteUser() {
        return this.request('/user', {
            method: 'DELETE',
        })
    }

    async deleteMyAccount() {
        return this.request('/auth/account/delete', {
            method: 'DELETE',
        })
    }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export types for use in components
export type { APIError } 