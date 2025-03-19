"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Camera, CameraOff, Edit, Trash2, Play, Pause } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Mock data - in a real app, this would come from an API
const getCameraDetails = (id: string) => {
  // Convert id to number
  const numId = Number.parseInt(id)

  // Check if camera is active (id 1-7) or inactive (id 8-12)
  const isActive = numId <= 7

  return {
    id: numId,
    name: isActive
      ? [
          "Entrance North",
          "Food Court",
          "Main Hallway",
          "Parking A",
          "Electronics Section",
          "Kids Zone",
          "Clothing Department",
        ][numId % 7]
      : ["Entrance South", "Storage Area", "Parking B", "Staff Room", "Emergency Exit"][numId % 5],
    location: ["North Entrance", "Level 2", "Level 1", "Basement", "Level 3"][numId % 5],
    type: ["Entrance", "Tracking", "Shelf"][numId % 3],
    rtspUrl: `rtsp://192.168.1.${numId}:554/stream`,
    username: "admin",
    password: "********",
    status: isActive ? "Active" : "Inactive",
    lastActive: isActive ? "Just now" : "3 days ago",
    fovZones: [
      {
        id: 1,
        name: "Zone A",
        coordinates: [
          [10, 10],
          [100, 10],
          [100, 100],
          [10, 100],
        ],
      },
      {
        id: 2,
        name: "Zone B",
        coordinates: [
          [120, 120],
          [200, 120],
          [200, 200],
          [120, 200],
        ],
      },
    ],
  }
}

export default function CameraDetailsPage() {
  const params = useParams()
  const [camera, setCamera] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isStreaming, setIsStreaming] = useState(false)

  useEffect(() => {
    // Simulate API call
    const fetchCamera = async () => {
      try {
        await new Promise((resolve) => setTimeout(resolve, 1000))
        const cameraData = getCameraDetails(params.id as string)
        setCamera(cameraData)
      } catch (error) {
        console.error("Error fetching camera:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCamera()
  }, [params.id])

  if (isLoading) {
    return (
      <AuthenticatedLayout>
        <div className="flex items-center justify-center h-[calc(100vh-200px)]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </AuthenticatedLayout>
    )
  }

  if (!camera) {
    return (
      <AuthenticatedLayout>
        <div className="flex flex-col items-center justify-center h-[calc(100vh-200px)]">
          <h2 className="text-2xl font-bold">Camera not found</h2>
          <p className="text-muted-foreground">
            The camera you're looking for doesn't exist or you don't have access to it.
          </p>
        </div>
      </AuthenticatedLayout>
    )
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              {camera.status === "Active" ? (
                <Camera className="h-6 w-6 text-green-500" />
              ) : (
                <CameraOff className="h-6 w-6 text-destructive" />
              )}
              {camera.name}
            </h1>
            <p className="text-muted-foreground">
              {camera.location} • {camera.type} Camera
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button variant="destructive" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>

        <Tabs defaultValue="stream">
          <TabsList>
            <TabsTrigger value="stream">Live Stream</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="zones">FOV Zones</TabsTrigger>
          </TabsList>

          <TabsContent value="stream" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Live Stream</CardTitle>
                <CardDescription>
                  {camera.status === "Active"
                    ? "View the live feed from this camera"
                    : "This camera is currently inactive"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative aspect-video bg-muted rounded-md overflow-hidden">
                  {camera.status === "Active" ? (
                    <>
                      <div className="absolute inset-0 flex items-center justify-center">
                        {isStreaming ? (
                          <img
                            src="/placeholder.svg?height=720&width=1280"
                            alt="Camera stream"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="text-center">
                            <p className="text-muted-foreground mb-4">Click the button below to start streaming</p>
                          </div>
                        )}
                      </div>

                      <div className="absolute bottom-4 right-4">
                        <Button
                          variant={isStreaming ? "destructive" : "default"}
                          size="sm"
                          onClick={() => setIsStreaming(!isStreaming)}
                        >
                          {isStreaming ? (
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
                        <CameraOff className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-muted-foreground">This camera is currently inactive</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter>
                <p className="text-sm text-muted-foreground">Last active: {camera.lastActive}</p>
              </CardFooter>
            </Card>
          </TabsContent>

          <TabsContent value="details" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Camera Details</CardTitle>
                <CardDescription>Technical information about this camera</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Camera Name</h3>
                      <p className="text-base font-medium">{camera.name}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Location</h3>
                      <p className="text-base font-medium">{camera.location}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Camera Type</h3>
                      <p className="text-base font-medium">{camera.type}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Status</h3>
                      <Badge variant={camera.status === "Active" ? "success" : "destructive"}>{camera.status}</Badge>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">RTSP URL</h3>
                      <p className="text-base font-medium font-mono">{camera.rtspUrl}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Username</h3>
                      <p className="text-base font-medium">{camera.username}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Password</h3>
                      <p className="text-base font-medium">{camera.password}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Last Active</h3>
                      <p className="text-base font-medium">{camera.lastActive}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="zones" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Field of View (FOV) Zones</CardTitle>
                <CardDescription>Defined zones for tracking and analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="relative aspect-video bg-muted rounded-md overflow-hidden">
                    <img
                      src="/placeholder.svg?height=720&width=1280"
                      alt="Camera view with zones"
                      className="w-full h-full object-cover"
                    />

                    {/* This would be replaced with actual zone visualization */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <p className="text-muted-foreground">Zone visualization would appear here</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Defined Zones</h3>

                    {camera.fovZones.map((zone: any) => (
                      <div key={zone.id} className="p-4 border rounded-md">
                        <h4 className="font-medium">{zone.name}</h4>
                        <p className="text-sm text-muted-foreground">{zone.coordinates.length} points defined</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button>Edit Zones</Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AuthenticatedLayout>
  )
}

