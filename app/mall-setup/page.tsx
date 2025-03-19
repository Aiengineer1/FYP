"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Upload, CheckCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/hooks/use-toast"

export default function MallSetupPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    name: "",
    address: "",
  })
  const [mapFile, setMapFile] = useState<File | null>(null)
  const [mapPreview, setMapPreview] = useState<string | null>(null)
  const [errors, setErrors] = useState<{
    name?: string
    address?: string
    mapFile?: string
  }>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  // Check authentication on component mount
  useEffect(() => {
    const checkAuth = () => {
      console.log("Checking authentication in mall setup..."); // Debug log
      const userData = localStorage.getItem('user')
      console.log("User data from localStorage:", userData); // Debug log
      
      if (!userData) {
        console.log("No user data found, redirecting to login"); // Debug log
        toast({
          title: "Authentication Required",
          description: "Please login to continue.",
          variant: "destructive",
        })
        router.push('/login')
        return
      }

      try {
        const parsedUserData = JSON.parse(userData);
        console.log("Parsed user data:", parsedUserData); // Debug log
        
        if (!parsedUserData.user_id) {
          console.log("No user_id found in user data"); // Debug log
          toast({
            title: "Invalid User Data",
            description: "Please login again.",
            variant: "destructive",
          })
          router.push('/login')
          return
        }
      } catch (error) {
        console.error("Error parsing user data:", error); // Debug log
        toast({
          title: "Error",
          description: "Invalid user data. Please login again.",
          variant: "destructive",
        })
        router.push('/login')
        return
      }

      setIsCheckingAuth(false)
    }

    checkAuth()
  }, [router, toast])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]

      // Check file type
      const validTypes = ["image/png", "image/jpeg", "image/jpg"]
      if (!validTypes.includes(file.type)) {
        setErrors((prev) => ({ ...prev, mapFile: "Please upload a PNG, JPG, or JPEG file" }))
        return
      }

      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setErrors((prev) => ({ ...prev, mapFile: "File size must be less than 5MB" }))
        return
      }

      setMapFile(file)
      setErrors((prev) => ({ ...prev, mapFile: undefined }))

      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setMapPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const validateForm = () => {
    const newErrors: {
      name?: string
      address?: string
      mapFile?: string
    } = {}
    let isValid = true

    if (!formData.name.trim()) {
      newErrors.name = "Mall name is required"
      isValid = false
    }

    if (!formData.address.trim()) {
      newErrors.address = "Mall address is required"
      isValid = false
    }

    if (!mapFile) {
      newErrors.mapFile = "Please upload a top-view map of the mall"
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      // Get user data from localStorage
      const userDataStr = localStorage.getItem('user')
      console.log("User data from localStorage in submit:", userDataStr); // Debug log
      
      if (!userDataStr) {
        throw new Error('User data not found. Please login again.')
      }

      const userData = JSON.parse(userDataStr)
      console.log("Parsed user data in submit:", userData); // Debug log
      
      if (!userData.user_id) {
        throw new Error('User data not found. Please login again.')
      }

      // Create form data for the API
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('address', formData.address)
      formDataToSend.append('user_id', userData.user_id)
      formDataToSend.append('map_image', mapFile!)

      console.log("Sending form data with user_id:", userData.user_id); // Debug log

      // Send POST request to create mall
      const response = await fetch('http://127.0.0.1:8000/mall/create', {
        method: 'POST',
        body: formDataToSend,
      })

      const data = await response.json()
      console.log("Mall creation response:", data); // Debug log

      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 404) {
          throw new Error('User not found. Please login again.')
        } else if (response.status === 400) {
          if (data.detail === 'User already has a mall') {
            throw new Error('You already have a mall associated with your account.')
          } else if (data.detail === 'Map image is required') {
            throw new Error('Please upload a valid map image.')
          }
        }
        throw new Error(data.detail || 'Failed to create mall')
      }

      // Show success message
      toast({
        title: "Success!",
        description: "Mall created successfully.",
      })

      // Redirect to dashboard with mall_id from response
      router.push(`/dashboard?mall_id=${data.id}`)
    } catch (error) {
      console.error("Mall setup error:", error)
      const errorMessage = error instanceof Error ? error.message : "Failed to create mall"
      
      // Show error toast
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      })

      // Set error in form
      setErrors(prev => ({
        ...prev,
        name: errorMessage
      }))
    } finally {
      setIsLoading(false)
    }
  }

  // Show loading state while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg">Checking authentication...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
      <div className="w-full max-w-2xl p-8 space-y-8 bg-background rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Mall Setup</h1>
          <p className="text-muted-foreground mt-2">Complete this step to start using RetailIQ</p>
        </div>

        <div className="flex items-center justify-center">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
              1
            </div>
            <div className="h-0.5 w-10 bg-primary"></div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <CheckCircle className="h-5 w-5" />
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name">Mall Name</Label>
              <Input
                id="name"
                name="name"
                placeholder="Central City Mall"
                value={formData.name}
                onChange={handleInputChange}
                className={errors.name ? "border-destructive" : ""}
                disabled={isLoading}
              />
              {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Mall Address</Label>
              <Input
                id="address"
                name="address"
                placeholder="123 Main St, City, Country"
                value={formData.address}
                onChange={handleInputChange}
                className={errors.address ? "border-destructive" : ""}
                disabled={isLoading}
              />
              {errors.address && <p className="text-sm text-destructive">{errors.address}</p>}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="mapFile">Upload Top-View Map</Label>
            <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-md p-6 bg-muted/50">
              {mapPreview ? (
                <div className="space-y-4 w-full">
                  <img
                    src={mapPreview || "/placeholder.svg"}
                    alt="Mall map preview"
                    className="max-h-48 mx-auto object-contain"
                  />
                  <div className="flex justify-center">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setMapFile(null)
                        setMapPreview(null)
                      }}
                      disabled={isLoading}
                    >
                      Change File
                    </Button>
                  </div>
                </div>
              ) : (
                <label
                  htmlFor="mapFile"
                  className="flex flex-col items-center justify-center cursor-pointer w-full h-32"
                >
                  <Upload className="h-10 w-10 text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Click to upload or drag and drop</p>
                  <p className="text-xs text-muted-foreground mt-1">PNG, JPG or JPEG (max. 5MB)</p>
                  <Input
                    id="mapFile"
                    type="file"
                    accept=".png,.jpg,.jpeg"
                    onChange={handleFileChange}
                    className="hidden"
                    disabled={isLoading}
                  />
                </label>
              )}
            </div>
            {errors.mapFile && <p className="text-sm text-destructive">{errors.mapFile}</p>}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Creating Mall..." : "Create Mall"}
          </Button>
        </form>
      </div>
    </div>
  )
}

