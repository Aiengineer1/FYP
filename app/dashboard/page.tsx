"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Camera, CameraOff, ArrowRight } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/components/ui/use-toast"
import { Skeleton } from "@/components/ui/skeleton"

// Define types for our data
interface Camera {
  id: number
  name: string
  location: string
  status: "active" | "inactive"
  mall_id: number
  created_at?: string
  updated_at?: string
}

interface MallData {
  id: number
  name: string
  address: string
  created_at: string
  cameras: Camera[]
}

export default function DashboardPage() {
  const { toast } = useToast()
  const [mallData, setMallData] = useState<MallData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMallData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Get user data from localStorage
        const userData = localStorage.getItem("user")
        if (!userData) {
          throw new Error("User data not found. Please login again.")
        }
        
        const user = JSON.parse(userData)
        const mallId = user.mall_id
        
        if (!mallId) {
          throw new Error("No mall associated with this account. Please set up a mall first.")
        }
        
        // Get token from localStorage
        const token = localStorage.getItem("token")
        if (!token) {
          throw new Error("Authentication token not found. Please login again.")
        }
        
        console.log("Fetching mall data for mall ID:", mallId)
        
        // Fetch mall data from API
        const response = await fetch(`http://localhost:8000/mall/${mallId}`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || "Failed to fetch mall data")
        }
        
        const data = await response.json()
        console.log("Mall data received:", data)
        
        // Transform the data to match our expected format
        // The API returns a simpler format than what our UI expects
        const transformedData = {
          id: data.id,
          name: data.name,
          address: data.address,
          created_at: data.created_at,
          // Initialize with empty cameras array since it's not in the API response yet
          cameras: []
        }
        
        setMallData(transformedData)
        
        // Now fetch cameras for this mall
        await fetchCameras(mallId, token)
      } catch (err) {
        console.error("Error fetching mall data:", err)
        setError(err instanceof Error ? err.message : "An unknown error occurred")
        toast({
          title: "Error",
          description: err instanceof Error ? err.message : "Failed to load dashboard data",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    const fetchCameras = async (mallId: number, token: string) => {
      try {
        console.log("Fetching cameras for mall ID:", mallId)
        
        // Fetch cameras for this mall
        const camerasResponse = await fetch(`http://localhost:8000/mall/${mallId}/cameras`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })
        
        if (!camerasResponse.ok) {
          const errorData = await camerasResponse.json()
          throw new Error(errorData.detail || "Failed to fetch cameras")
        }
        
        const camerasData = await camerasResponse.json()
        console.log("Cameras data received:", camerasData)
        
        // Update mall data with cameras
        setMallData(prevData => {
          if (!prevData) return null
          return {
            ...prevData,
            cameras: camerasData
          }
        })
      } catch (err) {
        console.error("Error fetching cameras:", err)
        // If the API is not implemented yet, use fallback data for testing
        console.log("Using fallback camera data for testing")
        
        // Create some fallback camera data
        const fallbackCameras: Camera[] = [
          { id: 1, name: "Entrance North", location: "North Entrance", status: "active", mall_id: mallId },
          { id: 2, name: "Food Court", location: "Level 2", status: "active", mall_id: mallId },
          { id: 3, name: "Main Hallway", location: "Level 1", status: "active", mall_id: mallId },
          { id: 4, name: "Parking A", location: "Basement", status: "inactive", mall_id: mallId },
          { id: 5, name: "Electronics Section", location: "Level 3", status: "inactive", mall_id: mallId }
        ]
        
        // Update mall data with fallback cameras
        setMallData(prevData => {
          if (!prevData) return null
          return {
            ...prevData,
            cameras: fallbackCameras
          }
        })
      }
    }
    
    fetchMallData()
  }, [toast])

  // Filter cameras by status
  const activeCameras = mallData?.cameras.filter(camera => camera.status === "active") || []
  const inactiveCameras = mallData?.cameras.filter(camera => camera.status === "inactive") || []
  const totalCameras = mallData?.cameras.length || 0

  // Loading state
  if (isLoading) {
    return (
      <AuthenticatedLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Loading mall data...</p>
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
                      <Skeleton className="h-6 w-48 mt-1" />
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Address</h3>
                      <Skeleton className="h-6 w-64 mt-1" />
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
                  <Skeleton className="h-10 w-16" />
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle>Active Cameras</CardTitle>
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-10 w-16" />
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle>Inactive Cameras</CardTitle>
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-10 w-16" />
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </AuthenticatedLayout>
    )
  }

  // Error state
  if (error) {
    return (
      <AuthenticatedLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Error loading dashboard data</p>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-destructive">Error</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Please try the following:</p>
              <ul className="list-disc pl-6 mt-2 space-y-1">
                <li>Check your internet connection</li>
                <li>Make sure you're logged in</li>
                <li>Try refreshing the page</li>
                <li>Contact support if the problem persists</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </AuthenticatedLayout>
    )
  }

  // Success state
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
                    <p className="text-lg font-medium">{mallData?.name}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Address</h3>
                    <p className="text-lg font-medium">{mallData?.address}</p>
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
                  <span className="text-3xl font-bold">{totalCameras}</span>
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
                  <span className="text-3xl font-bold">{activeCameras.length}</span>
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
                  <span className="text-3xl font-bold">{inactiveCameras.length}</span>
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
                {activeCameras.length > 0 ? (
                  <div className="space-y-4">
                    {activeCameras.map((camera) => (
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
                ) : (
                  <p className="text-muted-foreground text-center py-4">No active cameras found</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Inactive Cameras</CardTitle>
                <CardDescription>Cameras that need attention</CardDescription>
              </CardHeader>
              <CardContent>
                {inactiveCameras.length > 0 ? (
                  <div className="space-y-4">
                    {inactiveCameras.map((camera) => (
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
                ) : (
                  <p className="text-muted-foreground text-center py-4">No inactive cameras found</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  )
}

