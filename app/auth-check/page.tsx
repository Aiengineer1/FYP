"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Loader2, Store, CheckCircle, XCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export default function AuthCheck() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [showOptions, setShowOptions] = useState(false)

  // In a real app, this would be an API call to check if the user has any malls
  const checkMallExists = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch('http://localhost:8000/auth/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // If token is invalid, redirect to login
        localStorage.removeItem('token');
        router.push('/login');
        return;
      }

      // For demo purposes, we'll show the options instead of auto-redirecting
      setShowOptions(true);
      setLoading(false);
    } catch (error) {
      console.error("Error checking mall status:", error);
      // On error, clear token and redirect to login
      localStorage.removeItem('token');
      router.push('/login');
    }
  }

  const handleMallSelection = (hasMall: boolean) => {
    if (hasMall) {
      // User has a mall, store this info and redirect to dashboard
      localStorage.setItem("mallConfigured", "true")
      router.push("/dashboard")
    } else {
      // User doesn't have a mall, redirect to mall setup
      localStorage.setItem("mallConfigured", "false")
      router.push("/mall-setup")
    }
  }

  // Check mall status on component mount
  useEffect(() => {
    checkMallExists()
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      {loading ? (
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <h1 className="text-2xl font-semibold">Checking your account...</h1>
          <p className="text-muted-foreground">Please wait while we set things up for you</p>
        </div>
      ) : showOptions ? (
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Mall Registration</CardTitle>
            <CardDescription>Do you already have a mall registered with RetailIQ?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Select an option below to continue. If you already have a mall registered, you'll be taken to your
              dashboard. If not, you'll be guided through the mall setup process.
            </p>
          </CardContent>
          <CardFooter className="flex flex-col sm:flex-row gap-3">
            <Button
              variant="outline"
              className="w-full sm:w-auto flex items-center gap-2"
              onClick={() => handleMallSelection(false)}
            >
              <XCircle className="h-4 w-4" />
              No, I need to register a mall
            </Button>
            <Button className="w-full sm:w-auto flex items-center gap-2" onClick={() => handleMallSelection(true)}>
              <CheckCircle className="h-4 w-4" />
              Yes, I have a registered mall
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <Store className="h-12 w-12 text-primary" />
          <h1 className="text-2xl font-semibold">Something went wrong</h1>
          <p className="text-muted-foreground">We couldn't check your mall status. Please try again.</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      )}
    </div>
  )
}

