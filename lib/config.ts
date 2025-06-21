/**
 * Application Configuration
 * Centralized configuration management for environment variables and settings
 */

export const config = {
    // API Configuration
    api: {
        baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
        timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000'),
        retryAttempts: parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3'),
        retryDelay: parseInt(process.env.NEXT_PUBLIC_API_RETRY_DELAY || '1000'),
    },

    // WebSocket Configuration
    websocket: {
        url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'http://localhost:8000',
        reconnectAttempts: parseInt(process.env.NEXT_PUBLIC_WS_RECONNECT_ATTEMPTS || '5'),
        reconnectDelay: parseInt(process.env.NEXT_PUBLIC_WS_RECONNECT_DELAY || '1000'),
        maxReconnectDelay: parseInt(process.env.NEXT_PUBLIC_WS_MAX_RECONNECT_DELAY || '30000'),
        pingInterval: parseInt(process.env.NEXT_PUBLIC_WS_PING_INTERVAL || '25000'),
        pongTimeout: parseInt(process.env.NEXT_PUBLIC_WS_PONG_TIMEOUT || '5000'),
    },

    // Authentication Configuration
    auth: {
        tokenKey: 'insightcart_token',
        refreshTokenKey: 'insightcart_refresh_token',
        userKey: 'insightcart_user',
        tokenExpiryBuffer: parseInt(process.env.NEXT_PUBLIC_TOKEN_EXPIRY_BUFFER || '300'), // 5 minutes
    },

    // Camera Configuration
    camera: {
        defaultPollInterval: parseInt(process.env.NEXT_PUBLIC_CAMERA_POLL_INTERVAL || '1000'),
        maxRetries: parseInt(process.env.NEXT_PUBLIC_CAMERA_MAX_RETRIES || '3'),
        streamTimeout: parseInt(process.env.NEXT_PUBLIC_CAMERA_STREAM_TIMEOUT || '10000'),
        detectionTimeout: parseInt(process.env.NEXT_PUBLIC_DETECTION_TIMEOUT || '5000'),
    },

    // Analytics Configuration
    analytics: {
        refreshInterval: parseInt(process.env.NEXT_PUBLIC_ANALYTICS_REFRESH_INTERVAL || '30000'),
        realTimeRefreshInterval: parseInt(process.env.NEXT_PUBLIC_REALTIME_REFRESH_INTERVAL || '5000'),
        chartAnimationDuration: parseInt(process.env.NEXT_PUBLIC_CHART_ANIMATION_DURATION || '1000'),
        maxDataPoints: parseInt(process.env.NEXT_PUBLIC_MAX_DATA_POINTS || '50'),
    },

    // UI Configuration
    ui: {
        toastDuration: parseInt(process.env.NEXT_PUBLIC_TOAST_DURATION || '5000'),
        notificationTimeout: parseInt(process.env.NEXT_PUBLIC_NOTIFICATION_TIMEOUT || '5000'),
        loadingDelayMs: parseInt(process.env.NEXT_PUBLIC_LOADING_DELAY_MS || '200'),
        animationDuration: parseInt(process.env.NEXT_PUBLIC_ANIMATION_DURATION || '300'),
    },

    // Feature Flags
    features: {
        enableRealTimeUpdates: process.env.NEXT_PUBLIC_ENABLE_REALTIME_UPDATES !== 'false',
        enableNotifications: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS !== 'false',
        enableDetectionOverlays: process.env.NEXT_PUBLIC_ENABLE_DETECTION_OVERLAYS !== 'false',
        enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS !== 'false',
        enableDarkMode: process.env.NEXT_PUBLIC_ENABLE_DARK_MODE !== 'false',
        enableDebugMode: process.env.NEXT_PUBLIC_DEBUG_MODE === 'true',
    },

    // Development Configuration
    dev: {
        logLevel: process.env.NEXT_PUBLIC_LOG_LEVEL || 'info',
        enableMockData: process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA === 'true',
        showPerformanceMetrics: process.env.NEXT_PUBLIC_SHOW_PERFORMANCE_METRICS === 'true',
        enableHotReload: process.env.NODE_ENV === 'development',
    },

    // Security Configuration
    security: {
        enableCSRFProtection: process.env.NEXT_PUBLIC_ENABLE_CSRF_PROTECTION !== 'false',
        enableRateLimiting: process.env.NEXT_PUBLIC_ENABLE_RATE_LIMITING !== 'false',
        maxLoginAttempts: parseInt(process.env.NEXT_PUBLIC_MAX_LOGIN_ATTEMPTS || '5'),
        lockoutDuration: parseInt(process.env.NEXT_PUBLIC_LOCKOUT_DURATION || '900000'), // 15 minutes
    },

    // Cache Configuration
    cache: {
        enableSWRCache: process.env.NEXT_PUBLIC_ENABLE_SWR_CACHE !== 'false',
        cacheTimeout: parseInt(process.env.NEXT_PUBLIC_CACHE_TIMEOUT || '300000'), // 5 minutes
        maxCacheSize: parseInt(process.env.NEXT_PUBLIC_MAX_CACHE_SIZE || '50'),
        enablePersistentCache: process.env.NEXT_PUBLIC_ENABLE_PERSISTENT_CACHE !== 'false',
    },
} as const

/**
 * Type-safe environment variable getter
 */
export function getEnvVar(key: string, fallback?: string): string {
    const value = process.env[key]
    if (!value && !fallback) {
        throw new Error(`Environment variable ${key} is required but not set`)
    }
    return value || fallback || ''
}

/**
 * Validate required environment variables
 */
export function validateConfig(): void {
    const requiredVars = [
        'NEXT_PUBLIC_API_BASE_URL',
    ]

    const missing = requiredVars.filter(key => !process.env[key])

    if (missing.length > 0) {
        console.warn('Missing environment variables:', missing)
        console.warn('Using default values. Check your .env file for production deployment.')
    }
}

/**
 * Get API endpoint URL
 */
export function getApiUrl(endpoint: string): string {
    const baseUrl = config.api.baseUrl.replace(/\/$/, '')
    const cleanEndpoint = endpoint.replace(/^\//, '')
    return `${baseUrl}/${cleanEndpoint}`
}

/**
 * Get WebSocket URL
 */
export function getWebSocketUrl(): string {
    return config.websocket.url.replace(/^http/, 'ws')
}

/**
 * Check if we're in development mode
 */
export function isDevelopment(): boolean {
    return process.env.NODE_ENV === 'development'
}

/**
 * Check if we're in production mode
 */
export function isProduction(): boolean {
    return process.env.NODE_ENV === 'production'
}

/**
 * Log configuration on startup (development only)
 * Note: This will only run after environment variables are loaded
 */
export function logConfiguration(): void {
    if (isDevelopment()) {
        console.log('InsightCart Configuration:', {
            api: config.api,
            features: config.features,
            environment: process.env.NODE_ENV,
        })

        // Validate configuration after logging
        validateConfig()
    }
} 