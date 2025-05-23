"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Play, Pause, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface CameraStreamProps {
    camera: {
        id: number
        name: string
        location: string
        status: string
        username: string
        password: string
        ip_address: string
    }
}

export function CameraStream({ camera }: CameraStreamProps) {
    const [isStreaming, setIsStreaming] = useState(false)
    const [streamUrl, setStreamUrl] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const { toast } = useToast()

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
        if (streamUrl) {
            URL.revokeObjectURL(streamUrl)
            setStreamUrl(null)
        }
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-base">{camera.name}</CardTitle>
                <CardDescription>{camera.location}</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
                <div className="aspect-video bg-muted relative">
                    {camera.status === "Active" ? (
                        <>
                            {streamUrl ? (
                                <img
                                    src={streamUrl}
                                    alt={`${camera.name} stream`}
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-center">
                                        <p className="text-muted-foreground mb-4">Click the button below to start streaming</p>
                                    </div>
                                </div>
                            )}
                            <div className="absolute top-2 right-2">
                                <Badge variant="outline" className="bg-green-50 text-green-700">
                                    {isStreaming ? "Live" : "Offline"}
                                </Badge>
                            </div>
                            <div className="absolute bottom-4 right-4">
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