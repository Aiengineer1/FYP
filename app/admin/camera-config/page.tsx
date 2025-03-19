"use client"

import type React from "react"

import { useState } from "react"
import { Camera, Plus, Edit, Trash2 } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
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

// Mock data - in a real app, this would come from an API
const existingCameras = [
  { id: 1, name: "Entrance North", location: "North Entrance", type: "Entrance", status: "Active" },
  { id: 2, name: "Food Court", location: "Level 2", type: "Tracking", status: "Active" },
  { id: 3, name: "Main Hallway", location: "Level 1", type: "Tracking", status: "Active" },
  { id: 4, name: "Parking A", location: "Basement", type: "Entrance", status: "Active" },
  { id: 5, name: "Electronics Section", location: "Level 3", type: "Shelf", status: "Active" },
  { id: 8, name: "Entrance South", location: "South Entrance", type: "Entrance", status: "Inactive" },
  { id: 9, name: "Storage Area", location: "Basement", type: "Shelf", status: "Inactive" },
]

const locationOptions = [
  "North Entrance",
  "South Entrance",
  "East Entrance",
  "West Entrance",
  "Level 1",
  "Level 2",
  "Level 3",
  "Basement",
  "Food Court",
  "Parking Area",
]

export default function CameraConfigPage() {
  const [cameras, setCameras] = useState(existingCameras)
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState<any>(null)
  const [formData, setFormData] = useState({
    name: "",
    rtspUrl: "",
    username: "",
    password: "",
    location: "",
    fovZones: "",
    type: "",
    status: "Active",
  })
  const [errors, setErrors] = useState<{
    name?: string
    rtspUrl?: string
    location?: string
    fovZones?: string
    type?: string
  }>({})

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
      rtspUrl: "",
      username: "",
      password: "",
      location: "",
      fovZones: "",
      type: "",
      status: "Active",
    })
    setErrors({})
  }

  const validateForm = () => {
    const newErrors: {
      name?: string
      rtspUrl?: string
      location?: string
      fovZones?: string
      type?: string
    } = {}
    let isValid = true

    if (!formData.name.trim()) {
      newErrors.name = "Camera name is required"
      isValid = false
    }

    if (!formData.rtspUrl.trim()) {
      newErrors.rtspUrl = "RTSP URL is required"
      isValid = false
    } else if (!formData.rtspUrl.startsWith("rtsp://")) {
      newErrors.rtspUrl = "Must be a valid RTSP URL (starts with rtsp://)"
      isValid = false
    }

    if (!formData.location) {
      newErrors.location = "Location is required"
      isValid = false
    }

    if (!formData.type) {
      newErrors.type = "Camera type is required"
      isValid = false
    }

    if (!formData.fovZones.trim()) {
      newErrors.fovZones = "FOV zones are required"
      isValid = false
    } else {
      try {
        JSON.parse(formData.fovZones)
      } catch (e) {
        newErrors.fovZones = "FOV zones must be valid JSON"
        isValid = false
      }
    }

    setErrors(newErrors)
    return isValid
  }

  const handleAddCamera = () => {
    if (!validateForm()) return

    // In a real app, this would be an API call
    const newCamera = {
      id: Math.max(...cameras.map((c) => c.id)) + 1,
      name: formData.name,
      location: formData.location,
      type: formData.type,
      status: formData.status,
    }

    setCameras([...cameras, newCamera])
    setIsAddDialogOpen(false)
    resetForm()
  }

  const handleEditCamera = () => {
    if (!selectedCamera || !validateForm()) return

    // In a real app, this would be an API call
    const updatedCameras = cameras.map((camera) =>
      camera.id === selectedCamera.id
        ? {
            ...camera,
            name: formData.name,
            location: formData.location,
            type: formData.type,
            status: formData.status,
          }
        : camera,
    )

    setCameras(updatedCameras)
    setIsEditDialogOpen(false)
    setSelectedCamera(null)
    resetForm()
  }

  const handleDeleteCamera = () => {
    if (!selectedCamera) return

    // In a real app, this would be an API call
    const updatedCameras = cameras.filter((camera) => camera.id !== selectedCamera.id)

    setCameras(updatedCameras)
    setIsDeleteDialogOpen(false)
    setSelectedCamera(null)
  }

  const openEditDialog = (camera: any) => {
    setSelectedCamera(camera)
    setFormData({
      name: camera.name,
      rtspUrl: `rtsp://192.168.1.${camera.id}:554/stream`,
      username: "admin",
      password: "password",
      location: camera.location,
      fovZones: JSON.stringify(
        [
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
        ],
        null,
        2,
      ),
      type: camera.type,
      status: camera.status,
    })
    setIsEditDialogOpen(true)
  }

  const openDeleteDialog = (camera: any) => {
    setSelectedCamera(camera)
    setIsDeleteDialogOpen(true)
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Camera Configuration</h1>
            <p className="text-muted-foreground">Manage and configure cameras in your mall</p>
          </div>

          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Camera
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Add New Camera</DialogTitle>
                <DialogDescription>
                  Enter the details for the new camera. Click save when you're done.
                </DialogDescription>
              </DialogHeader>

              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Camera Name</Label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="e.g., Entrance North"
                      className={errors.name ? "border-destructive" : ""}
                    />
                    {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="location">Physical Location</Label>
                    <Select value={formData.location} onValueChange={(value) => handleSelectChange("location", value)}>
                      <SelectTrigger className={errors.location ? "border-destructive" : ""}>
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                        {locationOptions.map((location) => (
                          <SelectItem key={location} value={location}>
                            {location}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.location && <p className="text-sm text-destructive">{errors.location}</p>}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rtspUrl">RTSP IP Address</Label>
                  <Input
                    id="rtspUrl"
                    name="rtspUrl"
                    value={formData.rtspUrl}
                    onChange={handleInputChange}
                    placeholder="rtsp://192.168.1.100:554/stream"
                    className={errors.rtspUrl ? "border-destructive" : ""}
                  />
                  {errors.rtspUrl && <p className="text-sm text-destructive">{errors.rtspUrl}</p>}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">RTSP Username (Optional)</Label>
                    <Input
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      placeholder="admin"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">RTSP Password (Optional)</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="type">Camera Type</Label>
                    <Select value={formData.type} onValueChange={(value) => handleSelectChange("type", value)}>
                      <SelectTrigger className={errors.type ? "border-destructive" : ""}>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Entrance">Entrance</SelectItem>
                        <SelectItem value="Tracking">Tracking</SelectItem>
                        <SelectItem value="Shelf">Shelf</SelectItem>
                      </SelectContent>
                    </Select>
                    {errors.type && <p className="text-sm text-destructive">{errors.type}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select value={formData.status} onValueChange={(value) => handleSelectChange("status", value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Active">Active</SelectItem>
                        <SelectItem value="Inactive">Inactive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fovZones">FOV Zones (JSON)</Label>
                  <Textarea
                    id="fovZones"
                    name="fovZones"
                    value={formData.fovZones}
                    onChange={handleInputChange}
                    placeholder='[{"id": 1, "name": "Zone A", "coordinates": [[10, 10], [100, 10], [100, 100], [10, 100]]}]'
                    className={`font-mono text-sm h-32 ${errors.fovZones ? "border-destructive" : ""}`}
                  />
                  {errors.fovZones && <p className="text-sm text-destructive">{errors.fovZones}</p>}
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddCamera}>Save Camera</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Camera List</CardTitle>
            <CardDescription>All configured cameras in your mall</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cameras.map((camera) => (
                  <TableRow key={camera.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Camera
                          className={`h-4 w-4 ${camera.status === "Active" ? "text-green-500" : "text-muted-foreground"}`}
                        />
                        {camera.name}
                      </div>
                    </TableCell>
                    <TableCell>{camera.location}</TableCell>
                    <TableCell>{camera.type}</TableCell>
                    <TableCell>
                      <Badge
                        variant={camera.status === "Active" ? "outline" : "secondary"}
                        className={
                          camera.status === "Active" ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-700"
                        }
                      >
                        {camera.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="icon" onClick={() => openEditDialog(camera)}>
                          <Edit className="h-4 w-4" />
                          <span className="sr-only">Edit</span>
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => openDeleteDialog(camera)}>
                          <Trash2 className="h-4 w-4" />
                          <span className="sr-only">Delete</span>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Edit Camera Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Edit Camera</DialogTitle>
            <DialogDescription>Update the details for this camera. Click save when you're done.</DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
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
                <Label htmlFor="edit-location">Physical Location</Label>
                <Select value={formData.location} onValueChange={(value) => handleSelectChange("location", value)}>
                  <SelectTrigger className={errors.location ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    {locationOptions.map((location) => (
                      <SelectItem key={location} value={location}>
                        {location}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.location && <p className="text-sm text-destructive">{errors.location}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-rtspUrl">RTSP IP Address</Label>
              <Input
                id="edit-rtspUrl"
                name="rtspUrl"
                value={formData.rtspUrl}
                onChange={handleInputChange}
                className={errors.rtspUrl ? "border-destructive" : ""}
              />
              {errors.rtspUrl && <p className="text-sm text-destructive">{errors.rtspUrl}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-username">RTSP Username</Label>
                <Input id="edit-username" name="username" value={formData.username} onChange={handleInputChange} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-password">RTSP Password</Label>
                <Input
                  id="edit-password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-type">Camera Type</Label>
                <Select value={formData.type} onValueChange={(value) => handleSelectChange("type", value)}>
                  <SelectTrigger className={errors.type ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Entrance">Entrance</SelectItem>
                    <SelectItem value="Tracking">Tracking</SelectItem>
                    <SelectItem value="Shelf">Shelf</SelectItem>
                  </SelectContent>
                </Select>
                {errors.type && <p className="text-sm text-destructive">{errors.type}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-status">Status</Label>
                <Select value={formData.status} onValueChange={(value) => handleSelectChange("status", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Active">Active</SelectItem>
                    <SelectItem value="Inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-fovZones">FOV Zones (JSON)</Label>
              <Textarea
                id="edit-fovZones"
                name="fovZones"
                value={formData.fovZones}
                onChange={handleInputChange}
                className={`font-mono text-sm h-32 ${errors.fovZones ? "border-destructive" : ""}`}
              />
              {errors.fovZones && <p className="text-sm text-destructive">{errors.fovZones}</p>}
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditCamera}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Camera Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Camera</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this camera? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          {selectedCamera && (
            <div className="py-4">
              <p className="font-medium">{selectedCamera.name}</p>
              <p className="text-sm text-muted-foreground">{selectedCamera.location}</p>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteCamera}>
              Delete Camera
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AuthenticatedLayout>
  )
}

