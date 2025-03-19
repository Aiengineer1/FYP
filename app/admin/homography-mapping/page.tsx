"use client"

import { useState } from "react"
import { Map, Plus, Save, Play, Square, Trash2 } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

// Mock data - in a real app, this would come from an API
const cameras = [
  { id: 1, name: "Entrance North", location: "North Entrance", status: "Active" },
  { id: 2, name: "Food Court", location: "Level 2", status: "Active" },
  { id: 3, name: "Main Hallway", location: "Level 1", status: "Active" },
  { id: 4, name: "Parking A", location: "Basement", status: "Active" },
  { id: 5, name: "Electronics Section", location: "Level 3", status: "Active" },
]

export default function HomographyMappingPage() {
  const [selectedCamera, setSelectedCamera] = useState<string>("")
  const [currentStep, setCurrentStep] = useState<number>(1)
  const [zoneName, setZoneName] = useState<string>("")
  const [objectName, setObjectName] = useState<string>("")
  const [zones, setZones] = useState<any[]>([])
  const [objects, setObjects] = useState<any[]>([])
  const [systemRunning, setSystemRunning] = useState<boolean>(false)

  const handleCameraSelect = (value: string) => {
    setSelectedCamera(value)
    setCurrentStep(1)
    setZones([])
    setObjects([])
  }

  const handleAddZone = () => {
    if (!zoneName) return

    const newZone = {
      id: zones.length + 1,
      name: zoneName,
      objects: [],
    }

    setZones([...zones, newZone])
    setZoneName("")
    setCurrentStep(3)
  }

  const handleAddObject = () => {
    if (!objectName) return

    const newObject = {
      id: objects.length + 1,
      name: objectName,
      points: 4,
    }

    setObjects([...objects, newObject])
    setObjectName("")
  }

  const handleSaveZone = () => {
    // In a real app, this would save the zone and objects to the backend
    setCurrentStep(2)
    setObjects([])
  }

  const handleFinalApply = () => {
    // In a real app, this would save all mappings to the backend
    alert("Homography mappings saved successfully!")
  }

  const handleToggleSystem = () => {
    setSystemRunning(!systemRunning)
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
                  onClick={handleToggleSystem}
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

                <Button variant="outline" className="flex-1" onClick={handleFinalApply}>
                  <Save className="h-4 w-4 mr-2" />
                  Final Apply
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
                      <div className="aspect-square bg-muted rounded-md overflow-hidden relative">
                        <img
                          src="/placeholder.svg?height=500&width=500"
                          alt="Mall top-view map"
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <p className="text-muted-foreground">Mall map with interactive zones</p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium">Camera View</h3>
                        <Badge variant="outline">{cameras.find((c) => c.id.toString() === selectedCamera)?.name}</Badge>
                      </div>
                      <div className="aspect-square bg-muted rounded-md overflow-hidden relative">
                        <img
                          src="/placeholder.svg?height=500&width=500"
                          alt="Camera view"
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <p className="text-muted-foreground">Camera view with interactive zones</p>
                        </div>
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
                          <Button className="flex-1" onClick={handleAddObject} disabled={!objectName}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Object
                          </Button>

                          <Button
                            variant="outline"
                            className="flex-1"
                            onClick={handleSaveZone}
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
                            {objects.map((object) => (
                              <div key={object.id} className="flex items-center justify-between p-2 border rounded-md">
                                <div>
                                  <p className="font-medium">{object.name}</p>
                                  <p className="text-xs text-muted-foreground">{object.points} points mapped</p>
                                </div>
                                <Button variant="ghost" size="icon">
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
                        {zones.map((zone) => (
                          <Card key={zone.id}>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-base">{zone.name}</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-sm text-muted-foreground">{zone.objects.length} objects mapped</p>
                            </CardContent>
                            <CardFooter className="flex justify-end gap-2 pt-0">
                              <Button variant="outline" size="sm" onClick={() => setCurrentStep(3)}>
                                Edit
                              </Button>
                              <Button variant="ghost" size="sm" className="text-destructive">
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

