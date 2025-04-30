"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"
import { Map, Plus, Save, Play, Square, Trash2, Loader2, RefreshCw, AlertCircle } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Camera, saveHomographyMappings } from '@/app/api/camera'

interface Point {
  x: number
  y: number
  id?: number
}

interface MappingObject {
  name: string
  src_points: Point[]
  dst_points: Point[]
  selected?: boolean
  zone_name: string
  zone_points: Point[]
  object_name: string
}

export default function HomographyMappingPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [cameras, setCameras] = useState<Camera[]>([])
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null)
  const [currentStep, setCurrentStep] = useState<number>(1)
  const [zoneName, setZoneName] = useState<string>("")
  const [zones, setZones] = useState<{ name: string; points: Point[]; x: number; y: number }[]>([])
  const [objectName, setObjectName] = useState<string>("")
  const [objects, setObjects] = useState<{ name: string; points: Point[] }[]>([])
  const [systemRunning, setSystemRunning] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState(true)
  const [mallMapImage, setMallMapImage] = useState<string>("")
  const [cameraFrame, setCameraFrame] = useState<string | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [captureError, setCaptureError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [labMap, setLabMap] = useState<string | null>(null)
  const [mappingObjects, setMappingObjects] = useState<MappingObject[]>([])
  const [currentObject, setCurrentObject] = useState<{
    name: string
    src_points: Point[]
    dst_points: Point[]
  }>({
    name: "",
    src_points: [],
    dst_points: []
  })
  const [selectionSequence, setSelectionSequence] = useState<"camera" | "map">("camera")
  const [isSelecting, setIsSelecting] = useState(false)
  const [selectedObject, setSelectedObject] = useState<MappingObject | null>(null)
  const [isMappingMode, setIsMappingMode] = useState(false)
  const [currentZone, setCurrentZone] = useState<{ name: string; points: Point[]; x: number; y: number } | null>(null)
  const [isAddingObject, setIsAddingObject] = useState(false)
  const [hoverPoint, setHoverPoint] = useState<Point | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isZoneMappingComplete, setIsZoneMappingComplete] = useState(false)
  const [currentZonePoints, setCurrentZonePoints] = useState<Point[]>([])
  const [zoneMappingMode, setZoneMappingMode] = useState<"camera" | "map">("camera")
  const [cameraZonePoints, setCameraZonePoints] = useState<Point[]>([])
  const [mapZonePoints, setMapZonePoints] = useState<Point[]>([])
  const [additionalPoints, setAdditionalPoints] = useState<number>(0)
  const [showPointPrompt, setShowPointPrompt] = useState(false)
  const [showSavePrompt, setShowSavePrompt] = useState(false)
  const [showMappingPrompt, setShowMappingPrompt] = useState(false)
  const [tempError, setTempError] = useState<string | null>(null)

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
    const camera = cameras.find(c => c.id.toString() === value)
    setSelectedCamera(camera || null)
    setCurrentStep(1)
    setZones([])
    setObjects([])
    setCameraFrame(null)
  }

  // Modify handleZoneSubmit
  const handleZoneSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!zoneName) return

    const newZone = {
      name: zoneName,
      points: [],
      x: 0,
      y: 0
    }

    setZones([...zones, newZone])
    setCurrentZone(newZone)
    setZoneName("")
    setCurrentStep(2) // Move to zone mapping step
  }

  // Modify handleZonePointMapping
  const handleZonePointMapping = (event: React.MouseEvent<HTMLImageElement>, type: "camera" | "map") => {
    if (!currentZone || currentStep !== 2 || type !== zoneMappingMode) return
    // Prevent point selection if prompt is shown
    if (type === "camera" && showPointPrompt) return
    // Prevent selecting more points on map than camera
    if (type === "map" && mapZonePoints.length >= cameraZonePoints.length) return

    const img = event.currentTarget
    const rect = img.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    if (type === "camera") {
      const newPoints = [...cameraZonePoints, { x, y }]
      setCameraZonePoints(newPoints)

      // Check if we've reached 5 points
      if (newPoints.length === 5) {
        setShowPointPrompt(true)
      }

      // Check if we've reached the total points (5 + additional)
      if (additionalPoints > 0 && newPoints.length === 5 + additionalPoints) {
        setZoneMappingMode("map")
        setShowPointPrompt(false)
      }
    } else {
      setMapZonePoints(prev => [...prev, { x, y }])
    }
  }

  // Add function to complete zone mapping
  const handleCompleteZoneMapping = () => {
    if (currentZone && cameraZonePoints.length >= 3 && mapZonePoints.length >= 3) {
      const updatedZone = {
        ...currentZone,
        points: mapZonePoints // Store map points as the final zone points
      }

      setZones(prev => prev.map(z =>
        z.name === currentZone.name ? updatedZone : z
      ))

      setIsZoneMappingComplete(true)
      setCurrentStep(3) // Move to object creation step
      setCameraZonePoints([])
      setMapZonePoints([])
      setZoneMappingMode("camera")

      toast({
        title: "Success",
        description: "Zone mapping completed",
      })
    } else {
      toast({
        title: "Error",
        description: "Please select at least 3 points on both views",
        variant: "destructive",
      })
    }
  }

  // Add function to switch mapping mode
  const handleSwitchMappingMode = () => {
    if (zoneMappingMode === "camera" && cameraZonePoints.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one point on camera view first",
        variant: "destructive",
      })
      return
    }
    setZoneMappingMode(prev => prev === "camera" ? "map" : "camera")
  }

  // Add function to remove last point
  const handleRemoveLastPoint = () => {
    if (zoneMappingMode === "camera") {
      setCameraZonePoints(prev => prev.slice(0, -1))
    } else {
      setMapZonePoints(prev => prev.slice(0, -1))
    }
  }

  // Modify handleObjectCreate
  const handleObjectCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!objectName || !currentZone || !isZoneMappingComplete) return

    const newObject = {
      name: `${currentZone.name}_${objectName}`,
      src_points: [],
      dst_points: [],
      zone_name: currentZone.name,
      zone_points: [],
      object_name: objectName
    }

    setMappingObjects(prev => [...prev, newObject])
    setSelectedObject(newObject)
    setIsMappingMode(true)
    setSelectionSequence("camera")
    setObjectName("")
    setCurrentStep(4)
  }

  // Modify handleSaveHomography to handle partial saves
  const handleSaveHomography = async () => {
    if (!selectedCamera) {
      toast({
        title: "Error",
        description: "Please select a camera first",
        variant: "destructive"
      });
      return;
    }

    try {
      // Filter out incomplete mappings
      const completedMappings = mappingObjects.filter(
        obj => obj.src_points.length === 4 && obj.dst_points.length === 4
      );

      if (completedMappings.length === 0) {
        toast({
          title: "Error",
          description: "No completed mappings to save",
          variant: "destructive"
        });
        return;
      }

      // Group mappings by zone
      const zones = completedMappings.reduce((acc, mapping) => {
        const zoneName = mapping.zone_name;
        if (!acc[zoneName]) {
          acc[zoneName] = {
            name: zoneName,
            points: mapping.zone_points,
            objects: []
          };
        }
        acc[zoneName].objects.push({
          name: mapping.object_name,
          src_points: mapping.src_points,
          dst_points: mapping.dst_points
        });
        return acc;
      }, {} as Record<string, any>);

      // Convert to array format
      const zonesArray = Object.values(zones);

      // Save to backend
      const updatedCamera = await saveHomographyMappings({
        camera_id: selectedCamera.id,
        zones: zonesArray
      });

      toast({
        title: "Success",
        description: "Homography mappings saved successfully"
      });

      // Update local state with the response
      setMappingObjects([]);
      setCurrentZonePoints([]);
      setSelectedCamera(updatedCamera as Camera | null);

    } catch (error) {
      console.error('Error saving homography mappings:', error);
      toast({
        title: "Error",
        description: "Failed to save homography mappings",
        variant: "destructive"
      });
    }
  };

  // Modify the areMappingsComplete function to be less restrictive
  const areMappingsComplete = () => {
    if (!selectedCamera || !isZoneMappingComplete) return false

    // Check if current zone has at least one complete object mapping
    return mappingObjects.some(obj =>
      obj.name.startsWith(currentZone?.name || '') &&
      obj.src_points.length === 4 &&
      obj.dst_points.length === 4
    )
  }

  // Add function to check if point is inside zone
  const isPointInsideZone = (point: Point, zone: { points: Point[] }): boolean => {
    if (zone.points.length < 3) return false

    let inside = false
    for (let i = 0, j = zone.points.length - 1; i < zone.points.length; j = i++) {
      const xi = zone.points[i].x
      const yi = zone.points[i].y
      const xj = zone.points[j].x
      const yj = zone.points[j].y

      const intersect = ((yi > point.y) !== (yj > point.y)) &&
        (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi)
      if (intersect) inside = !inside
    }
    return inside
  }

  // Add function to check if all objects are within zone
  const areAllObjectsInZone = () => {
    return mappingObjects.every(obj => {
      const zone = zones.find(z => obj.name.startsWith(z.name))
      if (!zone) return false
      return obj.dst_points.every(point => isPointInsideZone(point, zone))
    })
  }

  // Add function to show temporary error
  const showTemporaryError = (message: string) => {
    setTempError(message)
    setTimeout(() => setTempError(null), 2000) // Clear error after 2 seconds
  }

  // Modify handleImageClick for object mapping
  const handleImageClick = (event: React.MouseEvent<HTMLImageElement>, type: "camera" | "map") => {
    if (!isSelecting && !isMappingMode) return
    if (isMappingMode && type !== selectionSequence) return

    const img = event.currentTarget
    const rect = img.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    if (isMappingMode && selectedObject) {
      const currentZone = zones.find(zone => selectedObject.name.startsWith(zone.name))
      if (!currentZone) return

      if (type === "camera" && selectedObject.src_points.length < 4) {
        const newSrcPoints = [...selectedObject.src_points, { x, y, id: selectedObject.src_points.length + 1 }]
        setSelectedObject(prev => ({
          ...prev!,
          src_points: newSrcPoints
        }))

        if (newSrcPoints.length === 4) {
          setSelectionSequence("map")
          toast({
            title: "Camera points complete",
            description: "Now select corresponding points on the map view",
          })
        }
      } else if (type === "map" && selectedObject.dst_points.length < 4) {
        // Only show error if point is outside zone
        if (!isPointInsideZone({ x, y }, currentZone)) {
          showTemporaryError("You are out of zone. Please select the object inside the zone.")
          return
        }

        const newDstPoints = [...selectedObject.dst_points, { x, y, id: selectedObject.dst_points.length + 1 }]
        setSelectedObject(prev => ({
          ...prev!,
          dst_points: newDstPoints
        }))

        if (newDstPoints.length === 4) {
          setMappingObjects(prev =>
            prev.map(obj =>
              obj.name === selectedObject.name ? selectedObject : obj
            )
          )
          setSelectedObject(null)
          setIsMappingMode(false)
          setSelectionSequence("camera")
          setShowMappingPrompt(true)
        }
      }
    }
  }

  // Modify handleObjectSelect
  const handleObjectSelect = (object: MappingObject) => {
    setSelectedObject(object)
    setIsMappingMode(true)
    setSelectionSequence("camera")
    setCurrentStep(4)
  }

  // Add function to handle mapping completion
  const handleMappingComplete = () => {
    if (selectedObject && selectedObject.src_points.length === 4 && selectedObject.dst_points.length === 4) {
      setMappingObjects(prev =>
        prev.map(obj =>
          obj.name === selectedObject.name ? selectedObject : obj
        )
      )
      setSelectedObject(null)
      setIsMappingMode(false)
      setSelectionSequence("camera")
      setCurrentStep(3)
      toast({
        title: "Success",
        description: "Object mapping completed",
      })
    } else {
      toast({
        title: "Error",
        description: "Please complete both camera and map point selections",
        variant: "destructive",
      })
    }
  }

  // Add mouse move handler for hover effect
  const handleMouseMove = (event: React.MouseEvent<HTMLImageElement>, type: "camera" | "map") => {
    if (!isMappingMode || type !== selectionSequence) return

    const img = event.currentTarget
    const rect = img.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    setHoverPoint({ x, y })
  }

  // Add mouse leave handler
  const handleMouseLeave = () => {
    setHoverPoint(null)
  }

  const startMapping = () => {
    if (!currentObject.name) {
      toast({
        title: "Error",
        description: "Please enter an object name",
        variant: "destructive",
      })
      return
    }
    setIsSelecting(true)
    setSelectionSequence("camera")
  }

  const saveMappings = async () => {
    try {
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

      const response = await fetch("http://localhost:8000/homography/save-mappings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token.trim()}`
        },
        body: JSON.stringify({
          camera_id: selectedCamera?.id,
          mappings: mappingObjects
        })
      })

      if (!response.ok) {
        throw new Error("Failed to save mappings")
      }

      toast({
        title: "Success",
        description: "Homography mappings saved successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save mappings",
        variant: "destructive",
      })
    }
  }

  // Add function to handle additional points input
  const handleAdditionalPointsSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (additionalPoints > 0) {
      setShowPointPrompt(false)
    }
  }

  // Add function to handle early completion
  const handleEarlyComplete = () => {
    if (cameraZonePoints.length >= 3) {
      setZoneMappingMode("map")
      setShowPointPrompt(false)
    } else {
      toast({
        title: "Error",
        description: "Please select at least 3 points before proceeding",
        variant: "destructive",
      })
    }
  }

  // Add function to handle mapping prompt
  const handleMappingPrompt = (action: 'continue' | 'save') => {
    setShowMappingPrompt(false)
    if (action === 'continue') {
      setCurrentStep(3) // Go back to object creation
    } else {
      setShowSavePrompt(true)
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
                <Select value={selectedCamera?.id?.toString() || ""} onValueChange={handleCameraSelect}>
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

                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={handleSaveHomography}
                  disabled={!areMappingsComplete() || isSaving}
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Mapping
                    </>
                  )}
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
                {currentStep === 1 && "Step 1: Create a new zone"}
                {currentStep === 2 && "Step 2: Map the zone points"}
                {currentStep === 3 && "Step 3: Add objects to the zone"}
                {currentStep === 4 && "Step 4: Map the object points"}
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
                        {currentStep === 2 && zoneMappingMode === "map" && (
                          <Badge variant="secondary">
                            Select point {mapZonePoints.length + 1} of {cameraZonePoints.length}
                          </Badge>
                        )}
                      </div>
                      <div className="relative w-full h-[500px] bg-muted rounded-md overflow-hidden">
                        {mallMapImage ? (
                          <div className="relative w-full h-full">
                            <img
                              src={mallMapImage}
                              alt="Mall top-view map"
                              className="w-full h-full object-contain"
                              onClick={(e) => currentStep === 2 ? handleZonePointMapping(e, "map") : handleImageClick(e, "map")}
                              onMouseMove={(e) => handleMouseMove(e, "map")}
                              onMouseLeave={handleMouseLeave}
                            />
                            {currentStep === 2 && mapZonePoints.map((point, index) => (
                              <div
                                key={index}
                                className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
                                style={{
                                  left: `${point.x}px`,
                                  top: `${point.y}px`,
                                }}
                              >
                                <div className="w-full h-full rounded-full border-2 border-white bg-primary flex items-center justify-center text-white text-xs font-bold">
                                  {index + 1}
                                </div>
                              </div>
                            ))}
                            {hoverPoint && selectionSequence === "map" && mapZonePoints.length < cameraZonePoints.length && (
                              <div
                                className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
                                style={{
                                  left: `${hoverPoint.x}px`,
                                  top: `${hoverPoint.y}px`,
                                }}
                              >
                                <div className="w-full h-full rounded-full border-2 border-dashed border-primary bg-primary/20" />
                              </div>
                            )}
                          </div>
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
                        {currentStep === 2 && zoneMappingMode === "camera" && (
                          <Badge variant="secondary">Select point {cameraZonePoints.length + 1}</Badge>
                        )}
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">
                            {selectedCamera?.name}
                          </Badge>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              if (selectedCamera) {
                                getCameraFrame(selectedCamera)
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
                          <div className="relative w-full h-full">
                            <img
                              src={cameraFrame}
                              alt="Camera view"
                              className="w-full h-full object-contain"
                              onClick={(e) => currentStep === 2 ? handleZonePointMapping(e, "camera") : handleImageClick(e, "camera")}
                              onMouseMove={(e) => handleMouseMove(e, "camera")}
                              onMouseLeave={handleMouseLeave}
                            />
                            {currentStep === 2 && cameraZonePoints.map((point, index) => (
                              <div
                                key={index}
                                className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
                                style={{
                                  left: `${point.x}px`,
                                  top: `${point.y}px`,
                                }}
                              >
                                <div className="w-full h-full rounded-full border-2 border-white bg-primary flex items-center justify-center text-white text-xs font-bold">
                                  {index + 1}
                                </div>
                              </div>
                            ))}
                            {hoverPoint && selectionSequence === "camera" && !showPointPrompt && (
                              <div
                                className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
                                style={{
                                  left: `${hoverPoint.x}px`,
                                  top: `${hoverPoint.y}px`,
                                }}
                              >
                                <div className="w-full h-full rounded-full border-2 border-dashed border-primary bg-primary/20" />
                              </div>
                            )}
                            {showPointPrompt && (
                              <div className="absolute bottom-0 left-0 right-0 bg-background/95 border-t p-4">
                                <form onSubmit={handleAdditionalPointsSubmit} className="space-y-4">
                                  <div className="flex items-center gap-4">
                                    <div className="flex-1">
                                      <Label htmlFor="additional-points">How many more points do you want to add?</Label>
                                      <Input
                                        id="additional-points"
                                        type="number"
                                        min="0"
                                        value={additionalPoints}
                                        onChange={(e) => setAdditionalPoints(parseInt(e.target.value) || 0)}
                                        className="mt-1"
                                      />
                                    </div>
                                    <div className="flex items-end gap-2">
                                      <Button type="submit" disabled={additionalPoints < 0}>
                                        Continue
                                      </Button>
                                      <Button type="button" variant="outline" onClick={handleEarlyComplete}>
                                        Done
                                      </Button>
                                    </div>
                                  </div>
                                </form>
                              </div>
                            )}
                          </div>
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
                          <Button className="w-full" onClick={handleZoneSubmit} disabled={!zoneName}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Zone
                          </Button>
                        </div>
                      </div>

                      <div className="bg-muted/50 p-4 rounded-md">
                        <p className="text-sm text-muted-foreground">
                          <strong>Instructions:</strong> Enter a name for your zone and click "Add Zone" to proceed to zone mapping.
                        </p>
                      </div>
                    </div>
                  )}

                  {currentStep === 2 && currentZone && (
                    <div className="space-y-4">
                      <div className="bg-muted/50 p-4 rounded-md">
                        <p className="text-sm text-muted-foreground">
                          <strong>Instructions:</strong>
                          <br />
                          1. First, select points on the camera view (minimum 3)
                          <br />
                          2. After 5 points, specify how many more points to add
                          <br />
                          3. Or click "Done" to proceed to map view
                          <br />
                          4. Then select corresponding points on the map view
                          <br />
                          5. Points should be selected in the same order on both views
                          <br />
                          6. You must select exactly the same number of points on both views
                          <br />
                          <br />
                          Current Zone: <strong>{currentZone.name}</strong>
                          <br />
                          Camera points: {cameraZonePoints.length}
                          <br />
                          Map points: {mapZonePoints.length} of {cameraZonePoints.length}
                        </p>
                      </div>

                      <div className="flex justify-center gap-4">
                        <Button
                          variant="outline"
                          onClick={handleSwitchMappingMode}
                          disabled={zoneMappingMode === "camera" && cameraZonePoints.length < 3}
                        >
                          Switch to {zoneMappingMode === "camera" ? "Map" : "Camera"} View
                        </Button>
                        <Button
                          variant="outline"
                          onClick={handleRemoveLastPoint}
                          disabled={zoneMappingMode === "camera" ? cameraZonePoints.length === 0 : mapZonePoints.length === 0}
                        >
                          Remove Last Point
                        </Button>
                        {zoneMappingMode === "camera" && cameraZonePoints.length >= 3 && !showPointPrompt && (
                          <Button
                            variant="outline"
                            onClick={handleEarlyComplete}
                          >
                            Done
                          </Button>
                        )}
                        <Button
                          onClick={handleCompleteZoneMapping}
                          disabled={cameraZonePoints.length < 3 || mapZonePoints.length < 3}
                        >
                          Complete Zone Mapping
                        </Button>
                      </div>
                    </div>
                  )}

                  {currentStep === 3 && currentZone && isZoneMappingComplete && (
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
                          <Button
                            className="flex-1"
                            onClick={handleObjectCreate}
                            disabled={!objectName}
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Add Object
                          </Button>

                          <Button
                            variant="outline"
                            className="flex-1"
                            onClick={() => {
                              setCurrentStep(1)
                              setCurrentZone(null)
                              setIsZoneMappingComplete(false)
                            }}
                          >
                            Back to Zones
                          </Button>
                        </div>
                      </div>

                      <div className="bg-muted/50 p-4 rounded-md">
                        <p className="text-sm text-muted-foreground">
                          <strong>Instructions:</strong> Enter a name for your object and click "Add Object" to proceed to mapping.
                          <br />
                          Current Zone: <strong>{currentZone.name}</strong>
                        </p>
                      </div>
                    </div>
                  )}

                  {currentStep === 4 && selectedObject && (
                    <div className="space-y-4">
                      <div className="bg-muted/50 p-4 rounded-md">
                        <p className="text-sm text-muted-foreground">
                          <strong>Instructions:</strong>
                          <br />
                          1. First, select 4 points on the camera view (numbered 1-4)
                          <br />
                          2. Then, select the corresponding 4 points on the map view
                          <br />
                          3. Points must be selected inside the mapped zone
                          <br />
                          4. Points should be selected in the same order on both views
                          <br />
                          <br />
                          Current Object: <strong>{selectedObject.name.split('_')[1]}</strong>
                          <br />
                          Camera points: {selectedObject.src_points.length}/4
                          <br />
                          Map points: {selectedObject.dst_points.length}/4
                          <br />
                          {selectionSequence === "camera" ? (
                            <span className="text-primary">Selecting camera points...</span>
                          ) : (
                            <span className="text-primary">Selecting map points...</span>
                          )}
                        </p>
                      </div>

                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          onClick={() => {
                            setSelectedObject(null)
                            setIsMappingMode(false)
                            setSelectionSequence("camera")
                            setCurrentStep(3)
                          }}
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={handleMappingComplete}
                          disabled={selectedObject.src_points.length !== 4 || selectedObject.dst_points.length !== 4}
                        >
                          Complete Mapping
                        </Button>
                      </div>
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
                              {mappingObjects.filter(obj => obj.name.startsWith(zone.name)).length > 0 && (
                                <div className="mt-2 space-y-2">
                                  <p className="text-sm font-medium">Mapped Objects:</p>
                                  <div className="space-y-1">
                                    {mappingObjects
                                      .filter(obj => obj.name.startsWith(zone.name))
                                      .map((obj, objIndex) => (
                                        <div
                                          key={objIndex}
                                          className={`flex items-center justify-between p-2 rounded-md cursor-pointer ${selectedObject?.name === obj.name
                                            ? 'bg-primary/10'
                                            : 'hover:bg-muted'
                                            }`}
                                          onClick={() => handleObjectSelect(obj)}
                                        >
                                          <div>
                                            <p className="text-sm font-medium">{obj.name}</p>
                                            <p className="text-xs text-muted-foreground">
                                              {obj.src_points.length}/4 points mapped
                                            </p>
                                          </div>
                                          <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={(e) => {
                                              e.stopPropagation()
                                              setMappingObjects(prev =>
                                                prev.filter((_, i) => i !== objIndex)
                                              )
                                            }}
                                          >
                                            <Trash2 className="h-4 w-4" />
                                          </Button>
                                        </div>
                                      ))}
                                  </div>
                                </div>
                              )}
                            </CardContent>
                            <CardFooter className="flex justify-end gap-2 pt-0">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setCurrentStep(4)
                                  setSelectedObject(null)
                                  setIsMappingMode(false)
                                }}
                              >
                                Edit
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive"
                                onClick={() => {
                                  setZones(zones.filter((_, i) => i !== index))
                                  // Also remove associated objects
                                  setMappingObjects(prev =>
                                    prev.filter(obj => !obj.name.startsWith(zone.name))
                                  )
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

      {/* Add mapping mode indicator */}
      {isMappingMode && selectedObject && (
        <div className="fixed bottom-4 right-4 bg-background border rounded-lg shadow-lg p-4">
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <p className="font-medium">Mapping: {selectedObject.name.split('_')[1]}</p>
              <p className="text-sm text-muted-foreground">
                Camera points: {selectedObject.src_points.length}/4
                <br />
                Map points: {selectedObject.dst_points.length}/4
                <br />
                {selectionSequence === "camera" ? (
                  <span className="text-primary">Selecting camera points...</span>
                ) : (
                  <span className="text-primary">Selecting map points...</span>
                )}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSelectedObject(null)
                setIsMappingMode(false)
                setSelectionSequence("camera")
                setCurrentStep(3)
              }}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              onClick={handleMappingComplete}
              disabled={selectedObject.src_points.length !== 4 || selectedObject.dst_points.length !== 4}
            >
              Complete
            </Button>
          </div>
        </div>
      )}

      {/* Add mapping prompt dialog */}
      {showMappingPrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background p-6 rounded-lg shadow-lg max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Object Mapping Complete</h3>
            <p className="text-muted-foreground mb-6">
              Do you want to map another object or save the current mapping?
            </p>
            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={() => handleMappingPrompt('continue')}
              >
                Map Another Object
              </Button>
              <Button
                onClick={() => handleMappingPrompt('save')}
              >
                Save Mapping
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Add save prompt dialog */}
      {showSavePrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background p-6 rounded-lg shadow-lg max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Save Mapping</h3>
            <p className="text-muted-foreground mb-6">
              {areAllObjectsInZone()
                ? "All objects are within their zones. Would you like to save the mapping?"
                : "Some objects are outside their zones. Please ensure all objects are within their zones before saving."}
            </p>
            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={() => setShowSavePrompt(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={() => {
                  if (areAllObjectsInZone()) {
                    handleSaveHomography()
                    setShowSavePrompt(false)
                  }
                }}
                disabled={!areAllObjectsInZone()}
              >
                Save Mapping
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Add save button for all cameras */}
      {mappingObjects.length > 0 && (
        <div className="fixed bottom-4 left-4">
          <Button
            onClick={() => setShowSavePrompt(true)}
            disabled={!areAllObjectsInZone() || isSaving}
            className="shadow-lg"
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Mapping
              </>
            )}
          </Button>
        </div>
      )}

      {/* Update point markers to be more prominent */}
      <style jsx global>{`
        .point-marker {
          width: 40px !important;
          height: 40px !important;
          margin-left: -20px !important;
          margin-top: -20px !important;
          border-width: 3px !important;
          font-size: 20px !important;
          font-weight: bold !important;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.3) !important;
          z-index: 10 !important;
        }
      `}</style>

      {/* Update point marker rendering for object mapping */}
      {currentStep === 4 && selectedObject && (
        <>
          {selectedObject.src_points.map((point, index) => (
            <div
              key={`src-${index}`}
              className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
              style={{
                left: `${point.x}px`,
                top: `${point.y}px`,
              }}
            >
              <div className="w-full h-full rounded-full border-2 border-white bg-primary flex items-center justify-center text-white text-xs font-bold">
                {index + 1}
              </div>
            </div>
          ))}
          {selectedObject.dst_points.map((point, index) => (
            <div
              key={`dst-${index}`}
              className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
              style={{
                left: `${point.x}px`,
                top: `${point.y}px`,
              }}
            >
              <div className="w-full h-full rounded-full border-2 border-white bg-primary flex items-center justify-center text-white text-xs font-bold">
                {index + 1}
              </div>
            </div>
          ))}
          {hoverPoint && selectionSequence === "map" && selectedObject.dst_points.length < 4 && (
            <div
              className="absolute w-6 h-6 -ml-3 -mt-3 pointer-events-none"
              style={{
                left: `${hoverPoint.x}px`,
                top: `${hoverPoint.y}px`,
              }}
            >
              <div className="w-full h-full rounded-full border-2 border-dashed border-primary bg-primary/20 flex items-center justify-center text-primary text-xs font-bold">
                {selectedObject.dst_points.length + 1}
              </div>
            </div>
          )}
        </>
      )}

      {/* Add temporary error message */}
      {tempError && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-destructive text-destructive-foreground px-4 py-2 rounded-md shadow-lg z-50 animate-fade-out">
          <p className="text-sm font-medium">{tempError}</p>
        </div>
      )}

      {/* Add point counter */}
      {currentStep === 4 && selectedObject && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-background border px-4 py-2 rounded-md shadow-lg z-50">
          <p className="text-sm font-medium">
            {selectionSequence === "camera"
              ? `Camera Point ${selectedObject.src_points.length + 1} of 4`
              : `Map Point ${selectedObject.dst_points.length + 1} of 4`}
          </p>
        </div>
      )}
    </AuthenticatedLayout>
  )
}

// Add animation styles
const styles = `
  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }
  .animate-fade-out {
    animation: fadeOut 2s ease-out;
  }
`

// Add styles to document
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement("style")
  styleSheet.textContent = styles
  document.head.appendChild(styleSheet)
}

