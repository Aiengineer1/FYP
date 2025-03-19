"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, CheckCircle, XCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"

export default function ResetPasswordPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [errors, setErrors] = useState<{ newPassword?: string; confirmPassword?: string }>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isVerifying, setIsVerifying] = useState(true)
  const [isValidToken, setIsValidToken] = useState(false)
  const [isResetComplete, setIsResetComplete] = useState(false)

  // Verify token on page load
  useEffect(() => {
    const verifyToken = async () => {
      try {
        // Simulate API call to verify token
        await new Promise((resolve) => setTimeout(resolve, 1000))

        // For demo purposes, we'll consider tokens with length > 10 as valid
        const token = params.token as string
        const isValid = token && token.length > 10

        setIsValidToken(isValid)
      } catch (error) {
        console.error("Error verifying token:", error)
        setIsValidToken(false)
      } finally {
        setIsVerifying(false)
      }
    }

    verifyToken()
  }, [params.token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Reset errors
    setErrors({})

    // Validate form
    let isValid = true
    const newErrors: { newPassword?: string; confirmPassword?: string } = {}

    if (!newPassword) {
      newErrors.newPassword = "New password is required"
      isValid = false
    } else if (newPassword.length < 8) {
      newErrors.newPassword = "Password must be at least 8 characters"
      isValid = false
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password"
      isValid = false
    } else if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match"
      isValid = false
    }

    if (!isValid) {
      setErrors(newErrors)
      return
    }

    // Handle password reset
    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // In a real app, you would reset the password via an API
      console.log("Password reset successful", { token: params.token, newPassword })

      // Show success state
      setIsResetComplete(true)

      toast({
        title: "Password reset successful",
        description: "Your password has been updated. You can now log in with your new password.",
      })
    } catch (error) {
      console.error("Password reset error:", error)
      toast({
        title: "Error",
        description: "Failed to reset password. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isVerifying) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
        <div className="w-full max-w-md p-8 space-y-8 bg-background rounded-lg shadow-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <h1 className="text-2xl font-bold mt-4">Verifying Reset Link</h1>
            <p className="text-muted-foreground mt-2">Please wait while we verify your reset link...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!isValidToken) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
        <div className="w-full max-w-md p-8 space-y-8 bg-background rounded-lg shadow-lg">
          <div className="text-center">
            <XCircle className="h-12 w-12 text-destructive mx-auto" />
            <h1 className="text-2xl font-bold mt-4">Invalid or Expired Link</h1>
            <p className="text-muted-foreground mt-2">
              This password reset link is invalid or has expired. Please request a new one.
            </p>
            <div className="mt-6">
              <Link href="/login">
                <Button>Back to Login</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isResetComplete) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
        <div className="w-full max-w-md p-8 space-y-8 bg-background rounded-lg shadow-lg">
          <div className="text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
            <h1 className="text-2xl font-bold mt-4">Password Reset Complete</h1>
            <p className="text-muted-foreground mt-2">
              Your password has been successfully reset. You can now log in with your new password.
            </p>
            <div className="mt-6">
              <Link href="/login">
                <Button>Go to Login</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
      <Link
        href="/login"
        className="absolute top-4 left-4 flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Login
      </Link>

      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Reset Your Password</CardTitle>
          <CardDescription>Create a new password for your account</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className={errors.newPassword ? "border-destructive" : ""}
                disabled={isLoading}
              />
              {errors.newPassword && <p className="text-sm text-destructive">{errors.newPassword}</p>}
              <p className="text-xs text-muted-foreground">Password must be at least 8 characters</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={errors.confirmPassword ? "border-destructive" : ""}
                disabled={isLoading}
              />
              {errors.confirmPassword && <p className="text-sm text-destructive">{errors.confirmPassword}</p>}
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Resetting Password..." : "Reset Password"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}

