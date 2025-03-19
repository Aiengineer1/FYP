"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { validateEmail } from "@/lib/validation"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({})
  const [isLoading, setIsLoading] = useState(false)

  // Forgot password states
  const [forgotEmail, setForgotEmail] = useState("")
  const [forgotEmailError, setForgotEmailError] = useState<string | undefined>()
  const [isForgotLoading, setIsForgotLoading] = useState(false)
  const [isResetSent, setIsResetSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Reset errors
    setErrors({})

    // Validate form
    let isValid = true
    const newErrors: { email?: string; password?: string } = {}

    if (!email) {
      newErrors.email = "Email is required"
      isValid = false
    } else if (!validateEmail(email)) {
      newErrors.email = "Please enter a valid email"
      isValid = false
    }

    if (!password) {
      newErrors.password = "Password is required"
      isValid = false
    }

    if (!isValid) {
      setErrors(newErrors)
      return
    }

    // Handle login
    setIsLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password
        }),
      });

      const data = await response.json();
      console.log("Login response:", data); // Print the response

      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }

      // Store user data
      console.log("Storing user data:", data); // Debug log
      localStorage.setItem('user', JSON.stringify(data));

      // Show success toast
      toast({
        title: "Login successful",
        description: "Welcome back!",
      });

      // Check mall_id and redirect accordingly
      console.log("Checking mall_id:", data.mall_id); // Debug log
      if (data.mall_id && data.mall_id !== 0) {
        console.log("User has mall, redirecting to dashboard"); // Debug log
        // Store mall_id for future use
        localStorage.setItem('mall_id', data.mall_id.toString());
        // Redirect to dashboard with mall_id
        router.push(`/dashboard?mall_id=${data.mall_id}`);
      } else {
        console.log("No mall_id or mall_id is 0, redirecting to mall setup"); // Debug log
        // No mall_id, redirect to mall setup
        router.push("/mall-setup");
      }
    } catch (error) {
      console.error("Login error:", error);
      const errorMessage = error instanceof Error ? error.message : "Invalid email or password";
      toast({
        title: "Login failed",
        description: errorMessage,
        variant: "destructive"
      });
      setErrors({ 
        email: errorMessage
      });
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    // Reset error
    setForgotEmailError(undefined)

    // Validate email
    if (!forgotEmail) {
      setForgotEmailError("Email is required")
      return
    } else if (!validateEmail(forgotEmail)) {
      setForgotEmailError("Please enter a valid email")
      return
    }

    setIsForgotLoading(true)

    try {
      const response = await fetch('http://localhost:8000/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: forgotEmail
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to send reset link');
      }

      // Show success state
      setIsResetSent(true)

      toast({
        title: "Reset link sent",
        description: "Check your email for instructions to reset your password.",
      })
    } catch (error) {
      console.error("Password reset error:", error)
      setForgotEmailError(error instanceof Error ? error.message : "Failed to send reset link. Please try again.")
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send reset link",
        variant: "destructive"
      })
    } finally {
      setIsForgotLoading(false)
    }
  }

  const resetForgotPasswordForm = () => {
    setForgotEmail("")
    setForgotEmailError(undefined)
    setIsResetSent(false)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/40 p-4">
      <Link
        href="/"
        className="absolute top-4 left-4 flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Home
      </Link>

      <div className="w-full max-w-md p-8 space-y-8 bg-background rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome Back</h1>
          <p className="text-muted-foreground mt-2">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={errors.email ? "border-destructive" : ""}
              disabled={isLoading}
            />
            {errors.email && <p className="text-sm text-destructive">{errors.email}</p>}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              <Dialog onOpenChange={resetForgotPasswordForm}>
                <DialogTrigger asChild>
                  <Button variant="link" className="p-0 h-auto text-sm">
                    Forgot password?
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>Reset Password</DialogTitle>
                    <DialogDescription>
                      Enter your email address and we'll send you a link to reset your password.
                    </DialogDescription>
                  </DialogHeader>

                  {!isResetSent ? (
                    <>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="forgot-email">Email</Label>
                          <Input
                            id="forgot-email"
                            type="email"
                            placeholder="you@example.com"
                            value={forgotEmail}
                            onChange={(e) => setForgotEmail(e.target.value)}
                            className={forgotEmailError ? "border-destructive" : ""}
                          />
                          {forgotEmailError && <p className="text-sm text-destructive">{forgotEmailError}</p>}
                        </div>
                      </div>
                      <DialogFooter>
                        <Button type="button" onClick={handleForgotPassword} disabled={isForgotLoading}>
                          {isForgotLoading ? "Sending..." : "Send Reset Link"}
                        </Button>
                      </DialogFooter>
                    </>
                  ) : (
                    <div className="space-y-4 py-4">
                      <div className="bg-green-50 text-green-800 p-4 rounded-md">
                        <p className="font-medium">Reset link sent!</p>
                        <p className="text-sm mt-1">
                          We've sent a password reset link to <strong>{forgotEmail}</strong>. Please check your email
                          and follow the instructions to reset your password.
                        </p>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Didn't receive the email? Check your spam folder or try again.
                      </p>
                    </div>
                  )}
                </DialogContent>
              </Dialog>
            </div>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={errors.password ? "border-destructive" : ""}
              disabled={isLoading}
            />
            {errors.password && <p className="text-sm text-destructive">{errors.password}</p>}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Logging in..." : "Login"}
          </Button>
        </form>

        <div className="text-center mt-4">
          <p className="text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

