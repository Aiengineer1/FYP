"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { Map, Plus, Save, Play, Square, Trash2, Loader2, RefreshCw, AlertCircle } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

interface Camera {
  id: number
  name: string
  ip_address: string
  username: string
  password: string
  location: string
  homography_map: any
  fov_zones: any[]
  mall_id: number
  created_at: string
}

interface Point {
  x: number
  y: number
}

interface FOVZone {
  name: string
  points: Point[]
}

export default function HomographyMappingPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [cameras, setCameras] = useState<Camera[]>([])
  const [selectedCamera, setSelectedCamera] = useState<string>("")
  const [currentStep, setCurrentStep] = useState<number>(1)
  const [zoneName, setZoneName] = useState<string>("")
  const [objectName, setObjectName] = useState<string>("")
  const [zones, setZones] = useState<FOVZone[]>([])
  const [objects, setObjects] = useState<any[]>([])
  const [systemRunning, setSystemRunning] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState(true)
  const [mallMapImage, setMallMapImage] = useState<string>("")
  const [cameraFrame, setCameraFrame] = useState<string>("")
  const [isCapturing, setIsCapturing] = useState(false)
  const [captureError, setCaptureError] = useState<string | null>(null)

  // Fetch cameras and mall map when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        const userData = localStorage.getItem("user")
        const token = localStorage.getItem("token")

        if (!userData || !token) {
          throw new Error("User data or token not found")
        }

        const user = JSON.parse(userData)

        // Fetch mall map image
        const mallResponse = await fetch(`http://localhost:8000/mall/${user.mall_id}/image`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })

        if (!mallResponse.ok) {
          throw new Error("Failed to fetch mall map")
        }

        const mallImageBlob = await mallResponse.blob()
        const mallImageUrl = URL.createObjectURL(mallImageBlob)
        setMallMapImage(mallImageUrl)

        // Fetch cameras for the mall
        const camerasResponse = await fetch(`http://localhost:8000/mall/${user.mall_id}/cameras`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })

        if (!camerasResponse.ok) {
          throw new Error("Failed to fetch cameras")
        }

        const camerasData = await camerasResponse.json()
        if (!Array.isArray(camerasData)) {
          throw new Error("Invalid cameras data received")
        }
        setCameras(camerasData)
      } catch (error) {
        console.error("Error fetching data:", error)
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch data",
          variant: "destructive",
        })
        setCameras([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [toast])

  // Function to get camera frame from backend
  const getCameraFrame = async (camera: Camera) => {
    try {
      setIsCapturing(true)
      setCaptureError(null)

      const token = localStorage.getItem("token")
      if (!token) {
        toast({
          title: "Authentication Required",
          description: "Please login to continue",
          variant: "destructive",
        })
        router.push("/login")
        return
      }

      // Construct RTSP URL with correct format
      const rtspUrl = `rtsp://${camera.username}:${camera.password}@${camera.ip_address}:554/cam/realmonitor?channel=1&subtype=0`

      // Log the RTSP URL for debugging (without password)
      console.log("Attempting to access camera:", {
        ip: camera.ip_address,
        username: camera.username,
        url: `rtsp://${camera.username}:****@${camera.ip_address}:554/cam/realmonitor?channel=1&subtype=0`
      })

      const response = await fetch("http://localhost:8000/camera/frame", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token.trim()}`
        },
        body: JSON.stringify({ rtsp_url: rtspUrl })
      })

      // Log response details for debugging
      console.log("Response status:", response.status)
      console.log("Response headers:", Object.fromEntries(response.headers.entries()))

      if (response.status === 401) {
        toast({
          title: "Session Expired",
          description: "Your session has expired. Please login again.",
          variant: "destructive",
        })
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        router.push("/login")
        return
      }

      if (!response.ok) {
        const contentType = response.headers.get("content-type")
        console.log("Response content type:", contentType)

        let errorMessage = "Failed to get camera frame"

        if (contentType && contentType.includes("application/json")) {
          try {
            const errorData = await response.json()
            console.log("Error response data:", errorData)

            // Handle specific RTSP authentication errors
            if (errorData.detail && errorData.detail.includes("Unauthorized")) {
              errorMessage = "Camera authentication failed. Please check camera credentials."
            } else {
              errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData)
            }
          } catch (e) {
            console.error("Error parsing JSON response:", e)
          }
        } else {
          try {
            const text = await response.text()
            console.log("Non-JSON response:", text)
            errorMessage = text || "Unknown error occurred"
          } catch (e) {
            console.error("Error reading response text:", e)
          }
        }

        setCaptureError(errorMessage)
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        })
        return
      }

      try {
        const blob = await response.blob()
        const objectUrl = URL.createObjectURL(blob)
        setCameraFrame(objectUrl)
      } catch (e) {
        console.error("Error processing image:", e)
        setCaptureError("Failed to process camera frame")
        toast({
          title: "Error",
          description: "Failed to process camera frame",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error capturing frame:", error)
      setCaptureError(error instanceof Error ? error.message : "Failed to capture frame")
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to capture frame",
        variant: "destructive",
      })
    } finally {
      setIsCapturing(false)
    }
  }

  // Clean up object URLs when component unmounts
  useEffect(() => {
    return () => {
      if (cameraFrame) {
        URL.revokeObjectURL(cameraFrame)
      }
    }
  }, [cameraFrame])

  // Add authentication check only on initial component mount
  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      toast({
        title: "Authentication Required",
        description: "Please login to continue",
        variant: "destructive",
      })
      router.push("/login")
    }
  }, []) // Empty dependency array means this runs only once on mount

  // Handle camera selection
  const handleCameraSelect = (value: string) => {
    setSelectedCamera(value)
    setCurrentStep(1)
    setZones([])
    setObjects([])

    // Get frame for selected camera
    const camera = cameras.find(c => c.id.toString() === value)
    if (camera) {
      getCameraFrame(camera)
    }
  }

  // Handle adding a new zone
  const handleAddZone = () => {
    if (!zoneName) return

    const newZone: FOVZone = {
      name: zoneName,
      points: []
    }

    setZones([...zones, newZone])
    setZoneName("")
    setCurrentStep(3)
  }

  // Handle saving homography mapping
  const handleSaveHomography = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) {
        throw new Error("No authentication token found")
      }

      const cameraId = parseInt(selectedCamera)
      const response = await fetch(`http://localhost:8000/${cameraId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          homography_map: {
            points: objects.map(obj => ({ x: obj.x, y: obj.y }))
          }
        })
      })

      if (!response.ok) {
        throw new Error("Failed to save homography mapping")
      }

      toast({
        title: "Success",
        description: "Homography mapping saved successfully",
      })
    } catch (error) {
      console.error("Error saving homography:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save homography mapping",
        variant: "destructive",
      })
    }
  }

  // Handle saving FOV zones
  const handleSaveFOVZones = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) {
        throw new Error("No authentication token found")
      }

      const cameraId = parseInt(selectedCamera)
      const response = await fetch(`http://localhost:8000/${cameraId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          fov_zones: zones
        })
      })

      if (!response.ok) {
        throw new Error("Failed to save FOV zones")
      }

      toast({
        title: "Success",
        description: "FOV zones saved successfully",
      })
    } catch (error) {
      console.error("Error saving FOV zones:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save FOV zones",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Homography Mapping</h1>
          <p className="text-muted-foreground">Map camera views to your mall's top-view for accurate tracking</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Camera Selection</CardTitle>
            <CardDescription>Select a camera to begin the homography mapping process</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="camera-select">Select Camera</Label>
                <Select value={selectedCamera} onValueChange={handleCameraSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a camera" />
                  </SelectTrigger>
                  <SelectContent>
                    {cameras.map((camera) => (
                      <SelectItem key={camera.id} value={camera.id.toString()}>
                        {camera.name} ({camera.location})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="md:col-span-2 flex items-end space-x-2">
                <Button
                  variant={systemRunning ? "destructive" : "default"}
                  className="flex-1"
                  onClick={() => setSystemRunning(!systemRunning)}
                >
                  {systemRunning ? (
                    <>
                      <Square className="h-4 w-4 mr-2" />
                      Stop System
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start System
                    </>
                  )}
                </Button>

                <Button variant="outline" className="flex-1" onClick={handleSaveHomography}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Mapping
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {selectedCamera && (
          <Card>
            <CardHeader>
              <CardTitle>Homography Mapping</CardTitle>
              <CardDescription>
                {currentStep === 1 && "Draw zones on both images to map areas"}
                {currentStep === 2 && "Add a new zone or select an existing one to edit"}
                {currentStep === 3 && "Map objects within the selected zone"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="mapping" className="space-y-4">
                <TabsList>
                  <TabsTrigger value="mapping">Mapping Interface</TabsTrigger>
                  <TabsTrigger value="zones">Zones & Objects</TabsTrigger>
                </TabsList>

                <TabsContent value="mapping" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium">Mall Top-View Map</h3>
                      </div>
                      <div className="relative w-full h-[500px] bg-muted rounded-md overflow-hidden">
                        {mallMapImage ? (
                          <img
                            src={mallMapImage}
                            alt="Mall top-view map"
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <p className="text-muted-foreground">Loading mall map...</p>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium">Camera View</h3>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">
                            {cameras.find((c) => c.id.toString() === selectedCamera)?.name}
                          </Badge>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const camera = cameras.find(c => c.id.toString() === selectedCamera)
                              if (camera) {
                                getCameraFrame(camera)
                              }
                            }}
                            disabled={isCapturing}
                          >
                            {isCapturing ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Capturing...
                              </>
                            ) : (
                              <>
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Refresh Frame
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                      <div className="relative w-full h-[500px] bg-muted rounded-md overflow-hidden">
                        {captureError ? (
                          <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center">
                            <AlertCircle className="h-8 w-8 text-destructive mb-2" />
                            <p className="text-destructive font-medium">Failed to capture frame</p>
                            <p className="text-sm text-muted-foreground">{captureError}</p>
                          </div>
                        ) : cameraFrame ? (
                          <img
                            src={cameraFrame}
                            alt="Camera view"
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <p className="text-muted-foreground">No camera frame available</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {currentStep === 1 && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2 md:col-span-2">
                          <Label htmlFor="zone-name">Zone Name</Label>
                          <Input
                            id="zone-name"
                            value={zoneName}
                            onChange={(e) => setZoneName(e.target.value)}
                            placeholder="e.g., Checkout Counter"
                          />
                        </div>

                        <div className="flex items-end">
                          <Button className="w-full" onClick={handleAddZone} disabled={!zoneName}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Zone
                          </Button>
                        </div>
                      </div>

                      <div className="bg-muted/50 p-4 rounded-md">
                        <p className="text-sm text-muted-foreground">
                          <strong>Instructions:</strong> Draw a zone on both images by clicking to place points. The
                          zone should represent the same physical area in both views.
                        </p>
                      </div>
                    </div>
                  )}

                  {currentStep === 3 && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2 md:col-span-2">
                          <Label htmlFor="object-name">Object Name</Label>
                          <Input
                            id="object-name"
                            value={objectName}
                            onChange={(e) => setObjectName(e.target.value)}
                            placeholder="e.g., Shelf A"
                          />
                        </div>

                        <div className="flex items-end space-x-2">
                          <Button className="flex-1" onClick={() => {
                            if (objectName) {
                              setObjects([...objects, { name: objectName, points: [] }])
                              setObjectName("")
                            }
                          }} disabled={!objectName}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Object
                          </Button>

                          <Button
                            variant="outline"
                            className="flex-1"
                            onClick={handleSaveFOVZones}
                            disabled={objects.length === 0}
                          >
                            <Save className="h-4 w-4 mr-2" />
                            Save Zone
                          </Button>
                        </div>
                      </div>

                      <div className="bg-muted/50 p-4 rounded-md">
                        <p className="text-sm text-muted-foreground">
                          <strong>Instructions:</strong> Select four points on both images to map an object. The points
                          should correspond to the same physical object in both views.
                        </p>
                      </div>

                      {objects.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="font-medium">Objects in Current Zone</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {objects.map((object, index) => (
                              <div key={index} className="flex items-center justify-between p-2 border rounded-md">
                                <div>
                                  <p className="font-medium">{object.name}</p>
                                  <p className="text-xs text-muted-foreground">{object.points.length} points mapped</p>
                                </div>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => {
                                    setObjects(objects.filter((_, i) => i !== index))
                                  }}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="zones" className="space-y-4">
                  {zones.length > 0 ? (
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Defined Zones</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {zones.map((zone, index) => (
                          <Card key={index}>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-base">{zone.name}</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-sm text-muted-foreground">{zone.points.length} points mapped</p>
                            </CardContent>
                            <CardFooter className="flex justify-end gap-2 pt-0">
                              <Button variant="outline" size="sm" onClick={() => setCurrentStep(3)}>
                                Edit
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => {
                                  setZones(zones.filter((_, i) => i !== index))
                                }}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </CardFooter>
                          </Card>
                        ))}
                      </div>

                      <Button onClick={() => setCurrentStep(1)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add New Zone
                      </Button>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-8">
                      <Map className="h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-lg font-medium">No Zones Defined</h3>
                      <p className="text-muted-foreground mb-4">
                        Create zones to map areas between your mall map and camera views
                      </p>
                      <Button onClick={() => setCurrentStep(1)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Zone
                      </Button>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </AuthenticatedLayout>
  )
}

