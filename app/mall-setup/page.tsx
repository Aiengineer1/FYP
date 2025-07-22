"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function MallSetupPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    map_image: null as File | null,
  })
  // Mall map preview state
  const [mallMap, setMallMap] = useState<string | null>(null)
  const [mallMapImg, setMallMapImg] = useState<string | null>(null)

  useEffect(() => {
    setMallMap(localStorage.getItem('mall_map_json'))
    setMallMapImg(localStorage.getItem('mall_map_png'))
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFormData((prev) => ({
        ...prev,
        map_image: file,
      }))
    }
  }

  // Helper to convert dataURL to File
  function dataURLtoFile(dataurl: string, filename: string) {
    const arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
      bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    for (let i = 0; i < n; i++) u8arr[i] = bstr.charCodeAt(i);
    return new File([u8arr], filename, { type: mime });
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Get user_id and token from localStorage
      const user_id = localStorage.getItem("user_id")
      const token = localStorage.getItem("token")

      if (!user_id || !token) {
        toast({
          title: "Error",
          description: "Please login first",
          variant: "destructive",
        })
        return
      }

      // Validate required fields (allow either uploaded image or drawn map)
      if (!formData.name || !formData.address || (!formData.map_image && !mallMapImg)) {
        toast({
          title: "Error",
          description: "All fields are required (draw or upload a map image)",
          variant: "destructive",
        })
        return
      }

      // Create FormData for multipart/form-data
      const formDataToSend = new FormData()

      // If user uploaded an image, use it. Otherwise, use the drawn map PNG from localStorage.
      if (formData.map_image) {
        formDataToSend.append("map_image", formData.map_image)
      } else if (mallMapImg) {
        const mapFile = dataURLtoFile(mallMapImg, 'mall_map.png');
        formDataToSend.append("map_image", mapFile);
      }

      // Add mall_map_json if present
      if (mallMap) {
        formDataToSend.append('mall_map_json', mallMap)
      }

      console.log("Sending form data with image:", formData.map_image?.name)
      console.log("User ID:", user_id)

      // Create URL with query parameters
      const url = new URL("http://localhost:8000/mall/create")
      url.searchParams.append("name", formData.name)
      url.searchParams.append("address", formData.address)
      url.searchParams.append("user_id", user_id)

      console.log("Request URL:", url.toString())

      const response = await fetch(url.toString(), {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formDataToSend,
      })

      console.log("Response status:", response.status)

      // Get the response data
      const responseData = await response.json()
      console.log("Response data:", responseData)

      if (!response.ok) {
        // Handle validation errors
        if (response.status === 422) {
          const errorMessage = Array.isArray(responseData.detail)
            ? responseData.detail.map((err: any) => `${err.loc.join('.')}: ${err.msg}`).join(", ")
            : responseData.detail || "Validation error"
          throw new Error(errorMessage)
        }
        throw new Error(responseData.detail || "Failed to create mall")
      }

      // Update user data with new mall_id
      const userData = localStorage.getItem("user")
      if (userData) {
        const user = JSON.parse(userData)
        user.mall_id = responseData.id
        localStorage.setItem("user", JSON.stringify(user))
        // Update cookie as well
        document.cookie = `user=${JSON.stringify(user)}; path=/; max-age=86400; SameSite=Lax`
      }

      toast({
        title: "Success",
        description: "Mall created successfully",
      })

      // Redirect to dashboard
      window.location.href = "/dashboard"
    } catch (error) {
      console.error("Error creating mall:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create mall. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-8">
      {/* Mall Map Preview */}
      {(mallMapImg || mallMap) && (
        <div className="mb-6 max-w-2xl mx-auto">
          <div className="font-bold mb-2">Mall Map Preview:</div>
          {mallMapImg ? (
            <img src={mallMapImg} alt="Mall Map" className="border rounded shadow max-w-full mb-2" />
          ) : (
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto mb-2">{mallMap}</pre>
          )}
          <button
            className="px-3 py-1 bg-red-500 text-white rounded"
            onClick={() => {
              localStorage.removeItem('mall_map_json')
              localStorage.removeItem('mall_map_png')
              setMallMap(null)
              setMallMapImg(null)
            }}
          >
            Clear Map
          </button>
        </div>
      )}
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Mall Setup</CardTitle>
          <CardDescription>
            Create your mall profile by filling out the information below
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Mall Name</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="Enter mall name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Mall Address</Label>
              <Textarea
                id="address"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                required
                placeholder="Enter mall address"
                className="min-h-[100px]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="map_image">Mall Map Image</Label>
              <Input
                id="map_image"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                required={!mallMapImg}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                disabled={!!mallMapImg}
              />
              {mallMapImg && (
                <div className="text-xs text-gray-500 mt-1">You have drawn a mall map. Upload is disabled.</div>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Creating Mall..." : "Create Mall"}
            </Button>
            <Button
              type="button"
              className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              onClick={() => router.push('/mall-setup/draw')}
            >
              Don't have a mall map? Draw your mall layout
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

