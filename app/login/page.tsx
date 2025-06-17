"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Mail, Lock } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/use-toast"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })
  const [errors, setErrors] = useState({
    email: "",
    password: "",
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setErrors(prev => ({
      ...prev,
      [name]: ""
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setErrors({ email: "", password: "" })

    try {
      console.log("Attempting login with:", formData.email)

      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()
      console.log("Login response data:", data)
      console.log("Response status:", response.status)
      console.log("Error detail:", data.detail)

      if (!response.ok) {
        if (data.detail === "Invalid credentials") {
          setErrors({
            email: "Invalid email or password",
            password: "Invalid email or password"
          })
          return
        } else if (data.detail === "Account not found" || response.status === 404) {
          setErrors({
            email: "Account not found",
            password: ""
          })
          return
        } else {
          setErrors({
            email: data.detail || "Login failed",
            password: data.detail || "Login failed"
          })
          return
        }
      }

      // Log the token before storing
      console.log("Access token from response:", data.access_token)

      // Store user data and token in localStorage
      localStorage.setItem("token", data.access_token)
      localStorage.setItem("user_id", data.user_id)
      localStorage.setItem("user", JSON.stringify(data))

      // Verify token was stored
      const storedToken = localStorage.getItem("token")
      console.log("Token stored in localStorage:", storedToken)

      // Set cookies with proper attributes
      document.cookie = `token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`
      document.cookie = `user=${JSON.stringify(data)}; path=/; max-age=86400; SameSite=Lax`

      toast({
        title: "Success",
        description: "Logged in successfully",
      })

      // Ensure data is saved before navigation
      await new Promise(resolve => setTimeout(resolve, 1000))

      console.log("Attempting navigation...")
      if (data.mall_id === null) {
        console.log("Redirecting to mall-setup...")
        // Use window.location for a full page reload
        window.location.href = "/mall-setup"
      } else {
        console.log("Redirecting to dashboard...")
        window.location.href = "/dashboard"
      }
    } catch (error) {
      console.error("Login error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to login",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-8">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="Enter your email"
                className={errors.email ? "border-destructive" : ""}
              />
              {errors.email && (
                <p className="text-sm text-destructive mt-1">{errors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                placeholder="Enter your password"
                className={errors.password ? "border-destructive" : ""}
              />
              {errors.password && (
                <p className="text-sm text-destructive mt-1">{errors.password}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Logging in..." : "Login"}
            </Button>

            <div className="text-center text-sm">
              Don't have an account?{" "}
              <Link href="/signup" className="text-primary hover:underline">
                Sign up
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

