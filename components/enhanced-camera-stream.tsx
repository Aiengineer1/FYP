"use client"

import { useEffect, useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Play, Pause, Loader2, Users, ShoppingCart, User } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useSocket } from "@/lib/socket-client"
import { DetectionEvent } from "@/types"

interface EnhancedCameraStreamProps {
    camera: {
        id: number
        name: string
        location: string
        status: string
        username: string
        password: string
        ip_address: string
    }
    showDetections?: boolean
    showAnalytics?: boolean
}

interface DetectionOverlayProps {
    detection: DetectionEvent
    imageWidth: number
    imageHeight: number
}

function DetectionOverlay({ detection, imageWidth, imageHeight }: DetectionOverlayProps) {
    const [x, y, width, height] = detection.bbox

    // Calculate overlay position and size
    const overlayStyle = {
        left: `${(x / imageWidth) * 100}%`,
        top: `${(y / imageHeight) * 100}%`,
        width: `${(width / imageWidth) * 100}%`,
        height: `${(height / imageHeight) * 100}%`,
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute border-2 border-primary bg-primary/10 backdrop-blur-sm"
            style={overlayStyle}
        >
            {/* Detection info badge */}
            <div className="absolute -top-8 left-0 flex gap-1">
                <Badge variant="secondary" className="text-xs bg-primary text-primary-foreground">
                    <User className="w-3 h-3 mr-1" />
                    {detection.age}y {detection.gender}
                </Badge>
            </div>

            {/* Confidence indicator */}
            <div className="absolute -bottom-6 left-0">
                <Badge variant="outline" className="text-xs">
                    {Math.round(detection.confidence * 100)}%
                </Badge>
            </div>
        </motion.div>
    )
}

export function EnhancedCameraStream({
    camera,
    showDetections = true,
    showAnalytics = true
}: EnhancedCameraStreamProps) {
    const [isStreaming, setIsStreaming] = useState(false)
    const [streamUrl, setStreamUrl] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [detections, setDetections] = useState<DetectionEvent[]>([])
    const [imageSize, setImageSize] = useState({ width: 640, height: 480 })
    const { toast } = useToast()
    const { socket } = useSocket()
    const imageRef = useRef<HTMLImageElement>(null)

    // Real-time detection updates
    useEffect(() => {
        if (socket.isSocketConnected() && showDetections) {
            socket.joinCameraRoom(camera.id)

            socket.onDetectionUpdate((data) => {
                if (data.cameraId === camera.id) {
                    setDetections(data.detections)
                    // Auto-clear detections after 5 seconds
                    setTimeout(() => {
                        setDetections([])
                    }, 5000)
                }
            })

            return () => {
                socket.leaveCameraRoom(camera.id)
                socket.off('detection_update')
            }
        }
    }, [socket, camera.id, showDetections])

    // Handle image load to get dimensions
    const handleImageLoad = () => {
        if (imageRef.current) {
            setImageSize({
                width: imageRef.current.naturalWidth,
                height: imageRef.current.naturalHeight
            })
        }
    }

    const startStream = async () => {
        if (!camera) return

        try {
            setIsLoading(true)
            const token = localStorage.getItem("token")
            if (!token) {
                throw new Error("No authentication token found")
            }

            // Construct RTSP URL
            const rtspUrl = `rtsp://${camera.username}:${camera.password}@${camera.ip_address}:554/cam/realmonitor?channel=1&subtype=0`

            // Get initial frame
            const response = await fetch("http://localhost:8000/camera/frame", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ rtsp_url: rtspUrl })
            })

            if (!response.ok) {
                throw new Error("Failed to get camera frame")
            }

            const blob = await response.blob()
            const objectUrl = URL.createObjectURL(blob)
            setStreamUrl(objectUrl)
            setIsStreaming(true)

            // Start polling for new frames
            const pollInterval = setInterval(async () => {
                try {
                    const frameResponse = await fetch("http://localhost:8000/camera/frame", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify({ rtsp_url: rtspUrl })
                    })

                    if (!frameResponse.ok) {
                        throw new Error("Failed to get camera frame")
                    }

                    const frameBlob = await frameResponse.blob()
                    const newObjectUrl = URL.createObjectURL(frameBlob)

                    // Clean up old URL
                    if (streamUrl) {
                        URL.revokeObjectURL(streamUrl)
                    }

                    setStreamUrl(newObjectUrl)
                } catch (error) {
                    console.error("Error polling camera frame:", error)
                    clearInterval(pollInterval)
                    setIsStreaming(false)
                    toast({
                        title: "Error",
                        description: "Failed to get camera frame",
                        variant: "destructive"
                    })
                }
            }, 1000) // Poll every second

            // Clean up interval on unmount
            return () => {
                clearInterval(pollInterval)
                if (streamUrl) {
                    URL.revokeObjectURL(streamUrl)
                }
            }
        } catch (error) {
            console.error("Error starting stream:", error)
            toast({
                title: "Error",
                description: error instanceof Error ? error.message : "Failed to start stream",
                variant: "destructive"
            })
        } finally {
            setIsLoading(false)
        }
    }

    const stopStream = () => {
        setIsStreaming(false)
        setDetections([]) // Clear detections when stopping
        if (streamUrl) {
            URL.revokeObjectURL(streamUrl)
            setStreamUrl(null)
        }
    }

    // Analytics calculations
    const activeDetections = detections.length

    return (
        <Card className="overflow-hidden">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="text-base">{camera.name}</CardTitle>
                        <CardDescription>{camera.location}</CardDescription>
                    </div>
                    {showAnalytics && activeDetections > 0 && (
                        <div className="flex gap-2">
                            <Badge variant="outline" className="flex items-center gap-1">
                                <Users className="w-3 h-3" />
                                {activeDetections}
                            </Badge>
                        </div>
                    )}
                </div>
            </CardHeader>

            <CardContent className="p-0">
                <div className="relative aspect-video bg-muted">
                    {camera.status === "Active" ? (
                        <>
                            {streamUrl ? (
                                <div className="relative w-full h-full">
                                    <img
                                        ref={imageRef}
                                        src={streamUrl}
                                        alt={`${camera.name} stream`}
                                        className="w-full h-full object-cover"
                                        onLoad={handleImageLoad}
                                    />

                                    {/* Detection overlays */}
                                    {showDetections && (
                                        <AnimatePresence>
                                            {detections.map((detection) => (
                                                <DetectionOverlay
                                                    key={detection.person_id}
                                                    detection={detection}
                                                    imageWidth={imageSize.width}
                                                    imageHeight={imageSize.height}
                                                />
                                            ))}
                                        </AnimatePresence>
                                    )}
                                </div>
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-center">
                                        <p className="text-muted-foreground mb-4">Click the button below to start streaming</p>
                                    </div>
                                </div>
                            )}

                            <div className="absolute top-2 right-2 flex gap-2">
                                <Badge variant="outline" className="bg-green-50 text-green-700">
                                    {isStreaming ? "Live" : "Offline"}
                                </Badge>
                                {socket.isSocketConnected() && showDetections && (
                                    <Badge variant="outline" className="bg-blue-50 text-blue-700">
                                        AI Active
                                    </Badge>
                                )}
                            </div>

                            <div className="absolute bottom-2 left-2">
                                <Button
                                    variant={isStreaming ? "destructive" : "default"}
                                    size="sm"
                                    onClick={isStreaming ? stopStream : startStream}
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                            Starting...
                                        </>
                                    ) : isStreaming ? (
                                        <>
                                            <Pause className="h-4 w-4 mr-2" />
                                            Stop Stream
                                        </>
                                    ) : (
                                        <>
                                            <Play className="h-4 w-4 mr-2" />
                                            Start Stream
                                        </>
                                    )}
                                </Button>
                            </div>
                        </>
                    ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                                <p className="text-muted-foreground">This camera is currently inactive</p>
                            </div>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    )
} 