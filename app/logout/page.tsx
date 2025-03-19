"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"

export default function LogoutPage() {
  const router = useRouter()

  useEffect(() => {
    const handleLogout = async () => {
      // In a real app, you would call an API to invalidate the session

      // Clear any stored data
      localStorage.removeItem("mallConfigured")

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Redirect to login page
      router.push("/login")
    }

    handleLogout()
  }, [router])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
      <h1 className="text-2xl font-semibold">Logging out...</h1>
      <p className="text-muted-foreground">Please wait while we sign you out</p>
    </div>
  )
}

