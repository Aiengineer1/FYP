"use client"

import Link from "next/link"
import { Camera, CameraOff, ArrowRight } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

// Mock data - in a real app, this would come from an API
const mallData = {
  name: "Central City Mall",
  address: "123 Main St, Central City, USA",
  totalCameras: 12,
  activeCameras: [
    { id: 1, name: "Entrance North", location: "North Entrance" },
    { id: 2, name: "Food Court", location: "Level 2" },
    { id: 3, name: "Main Hallway", location: "Level 1" },
    { id: 4, name: "Parking A", location: "Basement" },
    { id: 5, name: "Electronics Section", location: "Level 3" },
    { id: 6, name: "Kids Zone", location: "Level 2" },
    { id: 7, name: "Clothing Department", location: "Level 1" },
  ],
  inactiveCameras: [
    { id: 8, name: "Entrance South", location: "South Entrance" },
    { id: 9, name: "Storage Area", location: "Basement" },
    { id: 10, name: "Parking B", location: "Basement" },
    { id: 11, name: "Staff Room", location: "Level 3" },
    { id: 12, name: "Emergency Exit", location: "Level 2" },
  ],
}

export default function DashboardPage() {
  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your mall and camera system</p>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle>Mall Information</CardTitle>
              <CardDescription>Basic details about your mall</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Mall Name</h3>
                    <p className="text-lg font-medium">{mallData.name}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Address</h3>
                    <p className="text-lg font-medium">{mallData.address}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Total Cameras</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Camera className="h-8 w-8 text-muted-foreground mr-3" />
                  <span className="text-3xl font-bold">{mallData.totalCameras}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Active Cameras</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Camera className="h-8 w-8 text-green-500 mr-3" />
                  <span className="text-3xl font-bold">{mallData.activeCameras.length}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Inactive Cameras</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <CameraOff className="h-8 w-8 text-destructive mr-3" />
                  <span className="text-3xl font-bold">{mallData.inactiveCameras.length}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Active Cameras</CardTitle>
                <CardDescription>Cameras that are currently operational</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mallData.activeCameras.map((camera) => (
                    <Link
                      key={camera.id}
                      href={`/camera-details/${camera.id}`}
                      className="flex items-center justify-between p-3 rounded-md border hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Camera className="h-5 w-5 text-green-500" />
                        <div>
                          <p className="font-medium">{camera.name}</p>
                          <p className="text-sm text-muted-foreground">{camera.location}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="bg-green-50 text-green-700 hover:bg-green-100">
                        Active
                      </Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Inactive Cameras</CardTitle>
                <CardDescription>Cameras that need attention</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mallData.inactiveCameras.map((camera) => (
                    <Link
                      key={camera.id}
                      href={`/camera-details/${camera.id}`}
                      className="flex items-center justify-between p-3 rounded-md border hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <CameraOff className="h-5 w-5 text-destructive" />
                        <div>
                          <p className="font-medium">{camera.name}</p>
                          <p className="text-sm text-muted-foreground">{camera.location}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="bg-red-50 text-red-700 hover:bg-red-100">
                        Inactive
                      </Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  )
}

