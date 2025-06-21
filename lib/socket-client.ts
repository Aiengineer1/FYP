import { io, Socket } from 'socket.io-client'
import { config, getWebSocketUrl } from './config'
import { DetectionEvent, AnalyticsUpdate, CameraStatusUpdate, VisitorUpdate } from '@/types'

interface SocketConfig {
    url: string
    options: {
        transports: ['websocket']
        autoConnect: boolean
        reconnection: boolean
        reconnectionAttempts: number
        reconnectionDelay: number
        timeout: number
    }
}

class SocketManager {
    private sockets: Map<string, Socket> = new Map()
    private isConnected = false
    private currentMallId: number | null = null

    private getSocketConfig(): SocketConfig {
        return {
            url: config.websocket.url,
            options: {
                transports: ['websocket'],
                autoConnect: false,
                reconnection: true,
                reconnectionAttempts: config.websocket.reconnectAttempts,
                reconnectionDelay: config.websocket.reconnectDelay,
                timeout: config.websocket.pingInterval,
            }
        }
    }

    /**
     * Initialize WebSocket connections based on your backend endpoints
     */
    async initialize(mallId: number, token?: string): Promise<void> {
        this.currentMallId = mallId
        const { url, options } = this.getSocketConfig()

        try {
            // 1. Mall Analytics WebSocket - /analytics/ws/mall/{mall_id}
            const mallSocket = io(`${url}`, {
                ...options,
                auth: { token },
                query: {
                    mall_id: mallId,
                    token: token
                }
            })

            // 2. System Notifications WebSocket - /analytics/ws/system  
            const systemSocket = io(`${url}`, {
                ...options,
                auth: { token },
                query: {
                    token: token
                }
            })

            this.sockets.set('mall', mallSocket)
            this.sockets.set('system', systemSocket)

            // Set up connection handlers
            this.setupConnectionHandlers()

            // Connect all sockets
            mallSocket.connect()
            systemSocket.connect()

            console.log('✅ WebSocket connections initialized for mall:', mallId)
        } catch (error) {
            console.error('❌ Failed to initialize WebSocket connections:', error)
        }
    }

    /**
     * Connect to camera-specific WebSocket - /analytics/ws/camera/{camera_id}
     */
    async connectToCamera(cameraId: number, token?: string): Promise<void> {
        const { url, options } = this.getSocketConfig()
        const socketKey = `camera_${cameraId}`

        if (this.sockets.has(socketKey)) {
            return // Already connected
        }

        try {
            const cameraSocket = io(`${url}/analytics/ws/camera/${cameraId}`, {
                ...options,
                auth: { token },
                query: { camera_id: cameraId }
            })

            this.sockets.set(socketKey, cameraSocket)
            this.setupCameraHandlers(cameraSocket, cameraId)
            cameraSocket.connect()

            console.log('✅ Connected to camera WebSocket:', cameraId)
        } catch (error) {
            console.error('❌ Failed to connect to camera WebSocket:', error)
        }
    }

    /**
     * Disconnect from camera WebSocket
     */
    disconnectFromCamera(cameraId: number): void {
        const socketKey = `camera_${cameraId}`
        const socket = this.sockets.get(socketKey)

        if (socket) {
            socket.disconnect()
            this.sockets.delete(socketKey)
            console.log('🔌 Disconnected from camera WebSocket:', cameraId)
        }
    }

    private setupConnectionHandlers(): void {
        this.sockets.forEach((socket, key) => {
            socket.on('connect', () => {
                console.log(`✅ ${key} WebSocket connected`)
                this.isConnected = true
            })

            socket.on('disconnect', (reason) => {
                console.log(`🔌 ${key} WebSocket disconnected:`, reason)
                this.isConnected = false
            })

            socket.on('connect_error', (error) => {
                console.error(`❌ ${key} WebSocket connection error:`, error)
            })

            socket.on('reconnect', (attemptNumber) => {
                console.log(`🔄 ${key} WebSocket reconnected after ${attemptNumber} attempts`)
                this.isConnected = true
            })
        })
    }

    private setupCameraHandlers(socket: Socket, cameraId: number): void {
        // Detection updates from your backend
        socket.on('detection_update', (data) => {
            console.log(`🎯 Detection update for camera ${cameraId}:`, data)
            this.emit('detection_update', { cameraId, ...data })
        })

        // Camera status changes
        socket.on('camera_status', (data) => {
            console.log(`📹 Camera status update:`, data)
            this.emit('camera_status', data)
        })
    }

    /**
     * Analytics update handler - matches your backend format
     */
    onAnalyticsUpdate(callback: (data: AnalyticsUpdate) => void): void {
        const mallSocket = this.sockets.get('mall')
        if (mallSocket) {
            mallSocket.on('analytics_update', (data) => {
                console.log('📊 Analytics update received:', data)
                callback(data)
            })
        }
    }

    /**
     * Detection update handler - matches your backend format
     */
    onDetectionUpdate(callback: (data: { cameraId: number; detections: DetectionEvent[] }) => void): void {
        this.on('detection_update', callback)
    }

    /**
     * Camera status update handler
     */
    onCameraStatusUpdate(callback: (data: CameraStatusUpdate) => void): void {
        const systemSocket = this.sockets.get('system')
        if (systemSocket) {
            systemSocket.on('camera_status', callback)
        }
    }

    /**
     * System notifications handler - matches your backend alerts
     */
    onSystemMessage(callback: (data: { type: string; level: string; message: string; timestamp: string }) => void): void {
        const systemSocket = this.sockets.get('system')
        if (systemSocket) {
            systemSocket.on('system_message', (data) => {
                console.log('🔔 System notification:', data)
                callback(data)
            })
        }
    }

    /**
     * Performance metrics handler
     */
    onPerformanceUpdate(callback: (data: { processing_time: number; fps: number; queue_size: number }) => void): void {
        const mallSocket = this.sockets.get('mall')
        if (mallSocket) {
            mallSocket.on('performance_update', callback)
        }
    }

    /**
     * Join mall room (if your backend uses rooms)
     */
    joinMallRoom(mallId: number): void {
        const mallSocket = this.sockets.get('mall')
        if (mallSocket) {
            mallSocket.emit('join_mall', { mall_id: mallId })
        }
    }

    /**
     * Leave mall room
     */
    leaveMallRoom(mallId: number): void {
        const mallSocket = this.sockets.get('mall')
        if (mallSocket) {
            mallSocket.emit('leave_mall', { mall_id: mallId })
        }
    }

    /**
     * Join camera room
     */
    joinCameraRoom(cameraId: number): void {
        this.connectToCamera(cameraId)
    }

    /**
     * Leave camera room
     */
    leaveCameraRoom(cameraId: number): void {
        this.disconnectFromCamera(cameraId)
    }

    /**
     * Generic event emitter
     */
    private events: Map<string, Function[]> = new Map()

    private emit(event: string, data: any): void {
        const handlers = this.events.get(event)
        if (handlers) {
            handlers.forEach(handler => handler(data))
        }
    }

    private on(event: string, handler: Function): void {
        if (!this.events.has(event)) {
            this.events.set(event, [])
        }
        this.events.get(event)?.push(handler)
    }

    private off(event: string, handler?: Function): void {
        if (!handler) {
            this.events.delete(event)
            return
        }

        const handlers = this.events.get(event)
        if (handlers) {
            const index = handlers.indexOf(handler)
            if (index > -1) {
                handlers.splice(index, 1)
            }
        }
    }

    /**
     * Check if any socket is connected
     */
    isSocketConnected(): boolean {
        return this.isConnected && this.sockets.size > 0
    }

    /**
     * Disconnect all sockets
     */
    disconnect(): void {
        this.sockets.forEach((socket, key) => {
            socket.disconnect()
            console.log(`🔌 Disconnected ${key} WebSocket`)
        })
        this.sockets.clear()
        this.isConnected = false
        this.events.clear()
    }

    /**
     * Get connection status for debugging
     */
    getConnectionStatus(): { [key: string]: boolean } {
        const status: { [key: string]: boolean } = {}
        this.sockets.forEach((socket, key) => {
            status[key] = socket.connected
        })
        return status
    }
}

// Global socket manager instance
const socketManager = new SocketManager()

// React hook for easy WebSocket usage
import { useEffect, useState } from 'react'
import { useAuthStore } from '@/stores/auth-store'

export function useSocket() {
    const { user, token } = useAuthStore()
    const [isConnected, setIsConnected] = useState(false)

    useEffect(() => {
        if (user?.mall_id && token) {
            socketManager.initialize(user.mall_id, token)
                .then(() => setIsConnected(true))
                .catch((error) => {
                    console.error('Socket initialization failed:', error)
                    setIsConnected(false)
                })

            return () => {
                socketManager.disconnect()
                setIsConnected(false)
            }
        }
    }, [user?.mall_id, token])

    return {
        socket: socketManager,
        isConnected,
        connectionStatus: socketManager.getConnectionStatus()
    }
}

export default socketManager 