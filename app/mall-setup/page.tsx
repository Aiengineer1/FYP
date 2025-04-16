"use client"

import { useState } from "react"
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

      // Validate required fields
      if (!formData.name || !formData.address || !formData.map_image) {
        toast({
          title: "Error",
          description: "All fields are required",
          variant: "destructive",
        })
        return
      }

      // Create FormData for multipart/form-data
      const formDataToSend = new FormData()

      // Add the image file directly to FormData
      formDataToSend.append("map_image", formData.map_image)

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
                required
                className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Creating Mall..." : "Create Mall"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

