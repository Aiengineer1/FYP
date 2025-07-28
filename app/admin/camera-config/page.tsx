"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Camera, Plus, Edit, Trash2, Loader2 } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Camera interface based on API response
interface CameraData {
  id: number
  name: string
  ip_address: string
  username: string
  password: string
  location: string
  homography_map: any
  fov_zones: any
  mall_id: number
  created_at?: string
  updated_at?: string
}

// Form data interface
interface CameraFormData {
  name: string
  ip_address: string
  username: string
  password: string
  location: string
  homography_map: string
  fov_zones: string
  mall_id: number
}

export default function CameraConfigPage() {
  const { toast } = useToast()
  const [cameras, setCameras] = useState<CameraData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState<CameraData | null>(null)
  const [formData, setFormData] = useState<CameraFormData>({
    name: "",
    ip_address: "",
    username: "",
    password: "",
    location: "",
    homography_map: "{}",
    fov_zones: "{}",
    mall_id: 0,
  })
  const [errors, setErrors] = useState<{
    name?: string
    ip_address?: string
    username?: string
    password?: string
    location?: string
    homography_map?: string
    fov_zones?: string
  }>({})

  // Default camera credentials state
  const [defaultCredentials, setDefaultCredentials] = useState({
    defaultUsername: "admin",
    defaultPassword: "admin1234",
  })

  // Fetch cameras when component mounts
  useEffect(() => {
    fetchCameras()
    fetchDefaultCredentials()
  }, [])

  // Fetch default camera credentials from settings
  const fetchDefaultCredentials = async () => {
    try {
      const userData = localStorage.getItem("user")
      if (!userData) {
        console.log("No user data found, using default credentials")
        return
      }

      const user = JSON.parse(userData)
      const token = localStorage.getItem("token")

      if (!token) {
        console.log("No token found, using default credentials")
        return
      }

      // Try to fetch default credentials from API
      // For now, we'll use localStorage as a fallback since the API might not be implemented yet
      const savedDefaults = localStorage.getItem("cameraDefaults")
      if (savedDefaults) {
        const defaults = JSON.parse(savedDefaults)
        setDefaultCredentials(defaults)
        console.log("Loaded default credentials from localStorage:", defaults)
      }
    } catch (error) {
      console.error("Error fetching default credentials:", error)
      // Keep using the default values
    }
  }

  // Function to auto-fill form with default credentials
  const autoFillWithDefaults = () => {
    setFormData(prev => ({
      ...prev,
      username: defaultCredentials.defaultUsername,
      password: defaultCredentials.defaultPassword,
    }))
  }

  // Fetch cameras from API
  const fetchCameras = async () => {
    setIsLoading(true)
    try {
      const userData = localStorage.getItem("user")
      if (!userData) {
        toast({
          title: "Error",
          description: "User data not found. Please log in again.",
          variant: "destructive",
        })
        return
      }

      const user = JSON.parse(userData)

      // Check if user has a mall configured
      if (!user.mall_id) {
        console.warn("No mall configured for user")
        setCameras([]) // Set empty cameras array
        return
      }

      const token = localStorage.getItem("token")
      if (!token) {
        toast({
          title: "Error",
          description: "Authentication token not found. Please log in again.",
          variant: "destructive",
        })
        return
      }

      const response = await fetch(`http://localhost:8000/mall/${user.mall_id}/cameras`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      if (!response.ok) {
        if (response.status === 404) {
          // Mall doesn't exist or no cameras found
          console.warn("Mall not found or no cameras available")
          setCameras([])
          return
        }
        throw new Error("Failed to fetch cameras")
      }

      const data = await response.json()
      setCameras(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error("Error fetching cameras:", error)
      setCameras([]) // Set empty array on error
      toast({
        title: "Warning",
        description: "Could not load cameras. You can still add new cameras.",
        variant: "default",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    // Clear error for this field
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))

    // Clear error for this field
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const resetForm = () => {
    setFormData({
      name: "",
      ip_address: "",
      username: defaultCredentials.defaultUsername,
      password: defaultCredentials.defaultPassword,
      location: "",
      homography_map: "{}",
      fov_zones: "{}",
      mall_id: 0,
    })
    setErrors({})
  }

  const validateForm = () => {
    const newErrors: {
      name?: string
      ip_address?: string
      username?: string
      password?: string
      location?: string
      homography_map?: string
      fov_zones?: string
    } = {}
    let isValid = true

    if (!formData.name.trim()) {
      newErrors.name = "Camera name is required"
      isValid = false
    }

    if (!formData.ip_address.trim()) {
      newErrors.ip_address = "IP address is required"
      isValid = false
    } else if (!/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(formData.ip_address)) {
      newErrors.ip_address = "Must be a valid IP address"
      isValid = false
    }

    if (!formData.username.trim()) {
      newErrors.username = "Username is required"
      isValid = false
    }

    if (!formData.password.trim()) {
      newErrors.password = "Password is required"
      isValid = false
    }

    if (!formData.location.trim()) {
      newErrors.location = "Location is required"
      isValid = false
    }

    // Validate JSON fields
    try {
      JSON.parse(formData.homography_map)
    } catch (e) {
      newErrors.homography_map = "Homography map must be valid JSON"
      isValid = false
    }

    try {
      JSON.parse(formData.fov_zones)
    } catch (e) {
      newErrors.fov_zones = "FOV zones must be valid JSON"
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const handleAddCamera = async () => {
    if (!validateForm()) return

    try {
      const userData = localStorage.getItem("user")
      if (!userData) {
        toast({
          title: "Error",
          description: "User data not found. Please log in again.",
          variant: "destructive",
        })
        return
      }

      const user = JSON.parse(userData)
      const token = localStorage.getItem("token")
      if (!token) {
        toast({
          title: "Error",
          description: "Authentication token not found. Please log in again.",
          variant: "destructive",
        })
        return
      }

      // Prepare the camera data
      const cameraData = {
        ...formData,
        mall_id: user.mall_id,
        homography_map: JSON.parse(formData.homography_map),
        fov_zones: JSON.parse(formData.fov_zones),
      }

      const response = await fetch("http://localhost:8000/add_camera", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(cameraData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to add camera")
      }

      const newCamera = await response.json()
      setCameras([...cameras, newCamera])
      setIsAddDialogOpen(false)
      resetForm()

      toast({
        title: "Success",
        description: "Camera added successfully",
      })
    } catch (error) {
      console.error("Error adding camera:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add camera. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleEditCamera = async () => {
    if (!selectedCamera || !validateForm()) return

    try {
      const token = localStorage.getItem("token")
      if (!token) {
        toast({
          title: "Error",
          description: "Authentication token not found. Please log in again.",
          variant: "destructive",
        })
        return
      }

      // Prepare the camera data
      const cameraData = {
        ...formData,
        homography_map: JSON.parse(formData.homography_map),
        fov_zones: JSON.parse(formData.fov_zones),
      }

      const response = await fetch(`http://localhost:8000/${selectedCamera.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(cameraData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to update camera")
      }

      const updatedCamera = await response.json()

      // Update the cameras list
      const updatedCameras = cameras.map((camera) =>
        camera.id === selectedCamera.id ? updatedCamera : camera
      )

      setCameras(updatedCameras)
      setIsEditDialogOpen(false)
      setSelectedCamera(null)
      resetForm()

      toast({
        title: "Success",
        description: "Camera updated successfully",
      })
    } catch (error) {
      console.error("Error updating camera:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update camera. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteCamera = async () => {
    if (!selectedCamera) return

    try {
      const token = localStorage.getItem("token")
      if (!token) {
        toast({
          title: "Error",
          description: "Authentication token not found. Please log in again.",
          variant: "destructive",
        })
        return
      }

      const response = await fetch(`http://localhost:8000/${selectedCamera.id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to delete camera")
      }

      // Remove the camera from the list
      const updatedCameras = cameras.filter((camera) => camera.id !== selectedCamera.id)
      setCameras(updatedCameras)
      setIsDeleteDialogOpen(false)
      setSelectedCamera(null)

      toast({
        title: "Success",
        description: "Camera deleted successfully",
      })
    } catch (error) {
      console.error("Error deleting camera:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete camera. Please try again.",
        variant: "destructive",
      })
    }
  }

  const openEditDialog = (camera: CameraData) => {
    setSelectedCamera(camera)
    setFormData({
      name: camera.name,
      ip_address: camera.ip_address,
      username: camera.username,
      password: camera.password,
      location: camera.location,
      homography_map: JSON.stringify(camera.homography_map || {}),
      fov_zones: JSON.stringify(camera.fov_zones || {}),
      mall_id: camera.mall_id,
    })
    setIsEditDialogOpen(true)
  }

  const openDeleteDialog = (camera: CameraData) => {
    setSelectedCamera(camera)
    setIsDeleteDialogOpen(true)
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Camera Configuration</h1>
          <p className="text-muted-foreground">Manage your mall's camera system</p>
        </div>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <CardTitle>Cameras</CardTitle>
                <CardDescription>View and manage all cameras in your mall</CardDescription>
              </div>
              <Dialog open={isAddDialogOpen} onOpenChange={(open) => {
                setIsAddDialogOpen(open)
                if (open) {
                  resetForm() // This will auto-fill with default credentials
                }
              }}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Camera
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[600px] max-h-[90vh] flex flex-col">
                  <DialogHeader>
                    <DialogTitle>Add New Camera</DialogTitle>
                    <DialogDescription>Enter the details for the new camera</DialogDescription>
                  </DialogHeader>
                  <div className="flex-1 overflow-y-auto pr-2">
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="name">Camera Name</Label>
                          <Input
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            placeholder="Camera x"
                            className={errors.name ? "border-destructive" : ""}
                          />
                          {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="ip_address">IP Address</Label>
                          <Input
                            id="ip_address"
                            name="ip_address"
                            value={formData.ip_address}
                            onChange={handleInputChange}
                            placeholder="192.168.0.2"
                            className={errors.ip_address ? "border-destructive" : ""}
                          />
                          {errors.ip_address && <p className="text-sm text-destructive">{errors.ip_address}</p>}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="username" className="flex items-center gap-2">
                            Username
                            {formData.username === defaultCredentials.defaultUsername && (
                              <Badge variant="secondary" className="text-xs">Default</Badge>
                            )}
                          </Label>
                          <Input
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleInputChange}
                            placeholder="admin"
                            className={errors.username ? "border-destructive" : ""}
                          />
                          {errors.username && <p className="text-sm text-destructive">{errors.username}</p>}
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="password" className="flex items-center gap-2">
                            Password
                            {formData.password === defaultCredentials.defaultPassword && (
                              <Badge variant="secondary" className="text-xs">Default</Badge>
                            )}
                          </Label>
                          <Input
                            id="password"
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            placeholder="••••••••"
                            className={errors.password ? "border-destructive" : ""}
                          />
                          {errors.password && <p className="text-sm text-destructive">{errors.password}</p>}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="location">Location</Label>
                        <Input
                          id="location"
                          name="location"
                          value={formData.location}
                          onChange={handleInputChange}
                          placeholder="Enter camera location"
                          className={errors.location ? "border-destructive" : ""}
                        />
                        {errors.location && <p className="text-sm text-destructive">{errors.location}</p>}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="homography_map">Homography Map (JSON)</Label>
                        <Textarea
                          id="homography_map"
                          name="homography_map"
                          value={formData.homography_map}
                          onChange={handleInputChange}
                          placeholder="{}"
                          className={`font-mono text-sm h-32 resize-none ${errors.homography_map ? "border-destructive" : ""}`}
                        />
                        {errors.homography_map && <p className="text-sm text-destructive">{errors.homography_map}</p>}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="fov_zones">FOV Zones (JSON)</Label>
                        <Textarea
                          id="fov_zones"
                          name="fov_zones"
                          value={formData.fov_zones}
                          onChange={handleInputChange}
                          placeholder='[{"id": 1, "name": "Zone A", "coordinates": [[10, 10], [100, 10], [100, 100], [10, 100]]}]'
                          className={`font-mono text-sm h-32 resize-none ${errors.fov_zones ? "border-destructive" : ""}`}
                        />
                        {errors.fov_zones && <p className="text-sm text-destructive">{errors.fov_zones}</p>}
                      </div>
                    </div>
                  </div>
                  <DialogFooter className="flex-shrink-0">
                    <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddCamera}>Add Camera</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                <p className="text-muted-foreground">Loading cameras...</p>
              </div>
            ) : cameras.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Camera className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No cameras found. Add your first camera to get started.</p>
              </div>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>IP Address</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {cameras.map((camera) => (
                      <TableRow key={camera.id}>
                        <TableCell className="font-medium">{camera.name}</TableCell>
                        <TableCell>{camera.ip_address}</TableCell>
                        <TableCell>{camera.location}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="bg-accent/10 text-accent border-accent/20">
                            Active
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                              <DialogTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => openEditDialog(camera)}
                                >
                                  <Edit className="h-4 w-4" />
                                  <span className="sr-only">Edit</span>
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="sm:max-w-[600px] max-h-[90vh] flex flex-col">
                                <DialogHeader>
                                  <DialogTitle>Edit Camera</DialogTitle>
                                  <DialogDescription>Update the camera details</DialogDescription>
                                </DialogHeader>
                                <div className="flex-1 overflow-y-auto pr-2">
                                  <div className="grid gap-4 py-4">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                      <div className="space-y-2">
                                        <Label htmlFor="edit-name">Camera Name</Label>
                                        <Input
                                          id="edit-name"
                                          name="name"
                                          value={formData.name}
                                          onChange={handleInputChange}
                                          className={errors.name ? "border-destructive" : ""}
                                        />
                                        {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
                                      </div>

                                      <div className="space-y-2">
                                        <Label htmlFor="edit-ip_address">IP Address</Label>
                                        <Input
                                          id="edit-ip_address"
                                          name="ip_address"
                                          value={formData.ip_address}
                                          onChange={handleInputChange}
                                          className={errors.ip_address ? "border-destructive" : ""}
                                        />
                                        {errors.ip_address && <p className="text-sm text-destructive">{errors.ip_address}</p>}
                                      </div>
                                    </div>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                      <div className="space-y-2">
                                        <Label htmlFor="edit-username">Username</Label>
                                        <Input
                                          id="edit-username"
                                          name="username"
                                          value={formData.username}
                                          onChange={handleInputChange}
                                          className={errors.username ? "border-destructive" : ""}
                                        />
                                        {errors.username && <p className="text-sm text-destructive">{errors.username}</p>}
                                      </div>

                                      <div className="space-y-2">
                                        <Label htmlFor="edit-password">Password</Label>
                                        <Input
                                          id="edit-password"
                                          name="password"
                                          type="password"
                                          value={formData.password}
                                          onChange={handleInputChange}
                                          className={errors.password ? "border-destructive" : ""}
                                        />
                                        {errors.password && <p className="text-sm text-destructive">{errors.password}</p>}
                                      </div>
                                    </div>

                                    <div className="space-y-2">
                                      <Label htmlFor="edit-location">Location</Label>
                                      <Input
                                        id="edit-location"
                                        name="location"
                                        value={formData.location}
                                        onChange={handleInputChange}
                                        placeholder="Enter camera location"
                                        className={errors.location ? "border-destructive" : ""}
                                      />
                                      {errors.location && <p className="text-sm text-destructive">{errors.location}</p>}
                                    </div>

                                    <div className="space-y-2">
                                      <Label htmlFor="edit-homography_map">Homography Map (JSON)</Label>
                                      <Textarea
                                        id="edit-homography_map"
                                        name="homography_map"
                                        value={formData.homography_map}
                                        onChange={handleInputChange}
                                        className={`font-mono text-sm h-32 resize-none ${errors.homography_map ? "border-destructive" : ""}`}
                                      />
                                      {errors.homography_map && <p className="text-sm text-destructive">{errors.homography_map}</p>}
                                    </div>

                                    <div className="space-y-2">
                                      <Label htmlFor="edit-fov_zones">FOV Zones (JSON)</Label>
                                      <Textarea
                                        id="edit-fov_zones"
                                        name="fov_zones"
                                        value={formData.fov_zones}
                                        onChange={handleInputChange}
                                        className={`font-mono text-sm h-32 resize-none ${errors.fov_zones ? "border-destructive" : ""}`}
                                      />
                                      {errors.fov_zones && <p className="text-sm text-destructive">{errors.fov_zones}</p>}
                                    </div>
                                  </div>
                                </div>
                                <DialogFooter className="flex-shrink-0">
                                  <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                                    Cancel
                                  </Button>
                                  <Button onClick={handleEditCamera}>Save Changes</Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>

                            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                              <DialogTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => openDeleteDialog(camera)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                  <span className="sr-only">Delete</span>
                                </Button>
                              </DialogTrigger>
                              <DialogContent>
                                <DialogHeader>
                                  <DialogTitle>Delete Camera</DialogTitle>
                                  <DialogDescription>
                                    Are you sure you want to delete this camera? This action cannot be undone.
                                  </DialogDescription>
                                </DialogHeader>
                                <DialogFooter>
                                  <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
                                    Cancel
                                  </Button>
                                  <Button variant="destructive" onClick={handleDeleteCamera}>
                                    Delete
                                  </Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AuthenticatedLayout>
  )
}

