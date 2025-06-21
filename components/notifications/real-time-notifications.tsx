"use client"

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bell, AlertTriangle, CheckCircle, Info, X } from 'lucide-react'
import { useSocket } from '@/lib/socket-client'
import { useToast } from '@/hooks/use-toast'
import { useAuthStore } from '@/stores/auth-store'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface Notification {
    id: string
    type: 'success' | 'warning' | 'error' | 'info'
    title: string
    message: string
    timestamp: Date
    cameraId?: number
    mallId?: number
    autoHide?: boolean
}

const notificationIcons = {
    success: CheckCircle,
    warning: AlertTriangle,
    error: AlertTriangle,
    info: Info,
}

const notificationColors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
}

function NotificationItem({
    notification,
    onDismiss
}: {
    notification: Notification
    onDismiss: (id: string) => void
}) {
    const Icon = notificationIcons[notification.type]

    useEffect(() => {
        if (notification.autoHide) {
            const timer = setTimeout(() => {
                onDismiss(notification.id)
            }, 5000)
            return () => clearTimeout(timer)
        }
    }, [notification.id, notification.autoHide, onDismiss])

    return (
        <motion.div
            initial={{ opacity: 0, y: -50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-sm"
        >
            <Card className={`${notificationColors[notification.type]} border`}>
                <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Icon className="w-4 h-4" />
                            <CardTitle className="text-sm font-medium">
                                {notification.title}
                            </CardTitle>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 hover:bg-black/10"
                            onClick={() => onDismiss(notification.id)}
                        >
                            <X className="w-3 h-3" />
                        </Button>
                    </div>
                </CardHeader>
                <CardContent className="pt-0">
                    <p className="text-sm">{notification.message}</p>
                    <div className="flex items-center justify-between mt-2">
                        <p className="text-xs opacity-70">
                            {notification.timestamp.toLocaleTimeString()}
                        </p>
                        {notification.cameraId && (
                            <Badge variant="outline" className="text-xs">
                                Camera {notification.cameraId}
                            </Badge>
                        )}
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    )
}

export function RealTimeNotifications() {
    const { socket } = useSocket()
    const { user } = useAuthStore()
    const { toast } = useToast()
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [showNotifications, setShowNotifications] = useState(false)

    const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
        const newNotification: Notification = {
            ...notification,
            id: Date.now().toString(),
            timestamp: new Date(),
        }

        setNotifications(prev => [newNotification, ...prev.slice(0, 9)]) // Keep max 10 notifications

        // Also show as toast for immediate attention
        toast({
            title: notification.title,
            description: notification.message,
            variant: notification.type === 'error' ? 'destructive' : 'default',
        })
    }

    const dismissNotification = (id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id))
    }

    const clearAllNotifications = () => {
        setNotifications([])
    }

    useEffect(() => {
        if (socket.isSocketConnected() && user?.mall_id) {
            // Join mall room for notifications
            socket.joinMallRoom(user.mall_id)

            // Camera status updates
            socket.onCameraStatusUpdate((data) => {
                const { cameraId, status, timestamp } = data

                if (status === 'offline') {
                    addNotification({
                        type: 'error',
                        title: 'Camera Offline',
                        message: `Camera ${cameraId} has gone offline and needs attention.`,
                        cameraId,
                        autoHide: false,
                    })
                } else if (status === 'online') {
                    addNotification({
                        type: 'success',
                        title: 'Camera Online',
                        message: `Camera ${cameraId} is back online and operational.`,
                        cameraId,
                        autoHide: true,
                    })
                }
            })

            // Analytics alerts
            socket.onAnalyticsUpdate((data) => {
                // Check for unusual patterns or thresholds
                if (data.activeVisitors > 100) {
                    addNotification({
                        type: 'warning',
                        title: 'High Traffic Alert',
                        message: `Unusually high visitor count detected: ${data.activeVisitors} active visitors.`,
                        mallId: data.mallId,
                        autoHide: true,
                    })
                }

                if (data.averageDwellTime > 300) { // 5 minutes
                    addNotification({
                        type: 'info',
                        title: 'Extended Dwell Time',
                        message: `Customers are spending more time in the mall (avg: ${Math.round(data.averageDwellTime / 60)} minutes).`,
                        mallId: data.mallId,
                        autoHide: true,
                    })
                }
            })

            // Detection alerts for security
            socket.onDetectionUpdate((data) => {
                const suspiciousCount = data.detections.filter(d => d.confidence < 0.5).length

                if (suspiciousCount > 3) {
                    addNotification({
                        type: 'warning',
                        title: 'Detection Quality Alert',
                        message: `Multiple low-confidence detections on Camera ${data.cameraId}. Check camera positioning.`,
                        cameraId: data.cameraId,
                        autoHide: true,
                    })
                }
            })

            return () => {
                if (user?.mall_id) {
                    socket.leaveMallRoom(user.mall_id)
                }
                socket.off('camera_status')
                socket.off('analytics_update')
                socket.off('detection_update')
            }
        }
    }, [socket, user?.mall_id])

    const unreadCount = notifications.filter(n => n.type === 'error' || n.type === 'warning').length

    return (
        <>
            {/* Notification Bell Icon */}
            <div className="relative">
                <Button
                    variant="ghost"
                    size="sm"
                    className="relative"
                    onClick={() => setShowNotifications(!showNotifications)}
                >
                    <Bell className="w-5 h-5" />
                    {unreadCount > 0 && (
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
                        >
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </motion.div>
                    )}
                </Button>

                {/* Notifications Panel */}
                <AnimatePresence>
                    {showNotifications && (
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            className="absolute right-0 top-full mt-2 z-50"
                        >
                            <Card className="w-80 max-h-96 overflow-hidden">
                                <CardHeader className="pb-2">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-sm">Notifications</CardTitle>
                                        {notifications.length > 0 && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={clearAllNotifications}
                                                className="text-xs"
                                            >
                                                Clear All
                                            </Button>
                                        )}
                                    </div>
                                </CardHeader>
                                <CardContent className="p-0">
                                    {notifications.length === 0 ? (
                                        <div className="p-4 text-center text-muted-foreground">
                                            <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                            <p className="text-sm">No notifications</p>
                                        </div>
                                    ) : (
                                        <div className="max-h-80 overflow-y-auto space-y-2 p-2">
                                            {notifications.map((notification) => (
                                                <NotificationItem
                                                    key={notification.id}
                                                    notification={notification}
                                                    onDismiss={dismissNotification}
                                                />
                                            ))}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Floating Notifications */}
            <div className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
                <AnimatePresence>
                    {notifications
                        .filter(n => n.type === 'error')
                        .slice(0, 3)
                        .map((notification) => (
                            <div key={notification.id} className="pointer-events-auto">
                                <NotificationItem
                                    notification={notification}
                                    onDismiss={dismissNotification}
                                />
                            </div>
                        ))}
                </AnimatePresence>
            </div>
        </>
    )
} 