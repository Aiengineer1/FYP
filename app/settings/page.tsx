"use client"

import type React from "react"

import { useState } from "react"
import { Save, User, Lock, Camera, Trash2, AlertTriangle } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { validateEmail } from "@/lib/validation"
import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"
import { useRouter } from "next/navigation"

export default function SettingsPage() {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)

  // Account settings state
  const [accountSettings, setAccountSettings] = useState({
    name: "John Doe",
    email: "john.doe@example.com",
    mallName: "Central City Mall", // Display only
    mallContactEmail: "contact@centralcitymall.com",
    mallContactNumber: "123-456-7890",
  })

  // Security settings state
  const [securitySettings, setSecuritySettings] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  // Default camera credentials state
  const [cameraDefaults, setCameraDefaults] = useState({
    defaultUsername: "admin",
    defaultPassword: "camera123",
  })

  // Form errors state
  const [accountErrors, setAccountErrors] = useState<{
    name?: string
    email?: string
    mallContactEmail?: string
    mallContactNumber?: string
  }>({})

  const [securityErrors, setSecurityErrors] = useState<{
    currentPassword?: string
    newPassword?: string
    confirmPassword?: string
  }>({})

  const [isDeleteAccountDialogOpen, setIsDeleteAccountDialogOpen] = useState(false)
  const [isDeleteMallDialogOpen, setIsDeleteMallDialogOpen] = useState(false)
  const [deleteConfirmText, setDeleteConfirmText] = useState("")
  const router = useRouter()

  const handleAccountInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setAccountSettings((prev) => ({
      ...prev,
      [name]: value,
    }))

    // Clear error for this field
    if (accountErrors[name as keyof typeof accountErrors]) {
      setAccountErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }))
    }
  }

  const handleSecurityInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setSecuritySettings((prev) => ({
      ...prev,
      [name]: value,
    }))

    // Clear error for this field
    if (securityErrors[name as keyof typeof securityErrors]) {
      setSecurityErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }))
    }
  }

  const handleCameraDefaultsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCameraDefaults((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const validateAccountSettings = () => {
    const errors: {
      name?: string
      email?: string
      mallContactEmail?: string
      mallContactNumber?: string
    } = {}
    let isValid = true

    if (!accountSettings.name.trim()) {
      errors.name = "Full name is required"
      isValid = false
    }

    if (!accountSettings.email.trim()) {
      errors.email = "Email address is required"
      isValid = false
    } else if (!validateEmail(accountSettings.email)) {
      errors.email = "Please enter a valid email address"
      isValid = false
    }

    if (!accountSettings.mallContactEmail.trim()) {
      errors.mallContactEmail = "Mall contact email is required"
      isValid = false
    } else if (!validateEmail(accountSettings.mallContactEmail)) {
      errors.mallContactEmail = "Please enter a valid email address"
      isValid = false
    }

    if (!accountSettings.mallContactNumber.trim()) {
      errors.mallContactNumber = "Mall contact number is required"
      isValid = false
    } else if (!/^\d{3}-\d{3}-\d{4}$/.test(accountSettings.mallContactNumber)) {
      errors.mallContactNumber = "Please enter a valid phone number (format: 123-456-7890)"
      isValid = false
    }

    setAccountErrors(errors)
    return isValid
  }

  const validateSecuritySettings = () => {
    const errors: {
      currentPassword?: string
      newPassword?: string
      confirmPassword?: string
    } = {}
    let isValid = true

    if (!securitySettings.currentPassword) {
      errors.currentPassword = "Current password is required"
      isValid = false
    }

    if (!securitySettings.newPassword) {
      errors.newPassword = "New password is required"
      isValid = false
    } else if (securitySettings.newPassword.length < 8) {
      errors.newPassword = "Password must be at least 8 characters"
      isValid = false
    }

    if (!securitySettings.confirmPassword) {
      errors.confirmPassword = "Please confirm your new password"
      isValid = false
    } else if (securitySettings.newPassword !== securitySettings.confirmPassword) {
      errors.confirmPassword = "Passwords do not match"
      isValid = false
    }

    setSecurityErrors(errors)
    return isValid
  }

  const handleSaveAccountSettings = async () => {
    if (!validateAccountSettings()) return

    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // In a real app, you would save settings to an API
      console.log("Account settings saved:", accountSettings)

      toast({
        title: "Account settings updated",
        description: "Your account information has been successfully updated.",
      })
    } catch (error) {
      console.error("Error saving account settings:", error)
      toast({
        title: "Error",
        description: "Failed to update account settings. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdatePassword = async () => {
    if (!validateSecuritySettings()) return

    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // In a real app, you would update password via an API
      console.log("Password updated:", securitySettings)

      // Reset password fields
      setSecuritySettings({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      })

      toast({
        title: "Password updated",
        description: "Your password has been successfully updated.",
      })
    } catch (error) {
      console.error("Error updating password:", error)
      toast({
        title: "Error",
        description: "Failed to update password. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveCameraDefaults = async () => {
    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // In a real app, you would save camera defaults to an API
      console.log("Camera defaults saved:", cameraDefaults)

      toast({
        title: "Camera defaults saved",
        description: "Default camera credentials have been updated.",
      })
    } catch (error) {
      console.error("Error saving camera defaults:", error)
      toast({
        title: "Error",
        description: "Failed to save camera defaults. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteMall = async () => {
    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // In a real app, you would delete the mall via an API
      console.log("Mall deleted")

      toast({
        title: "Mall deleted",
        description: "Your mall and all associated data have been permanently deleted.",
      })

      // Redirect to auth check page
      router.push("/auth-check")
    } catch (error) {
      console.error("Error deleting mall:", error)
      toast({
        title: "Error",
        description: "Failed to delete mall. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
      setIsDeleteMallDialogOpen(false)
      setDeleteConfirmText("")
    }
  }

  const handleDeleteAccount = async () => {
    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // In a real app, you would delete the account via an API
      console.log("Account deleted")

      toast({
        title: "Account deleted",
        description: "Your account has been permanently deleted.",
      })

      // Redirect to login page
      router.push("/login")
    } catch (error) {
      console.error("Error deleting account:", error)
      toast({
        title: "Error",
        description: "Failed to delete account. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
      setIsDeleteAccountDialogOpen(false)
      setDeleteConfirmText("")
    }
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Manage your account settings and preferences</p>
        </div>

        <Tabs defaultValue="account" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="account" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span>Account</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              <Lock className="h-4 w-4" />
              <span>Security</span>
            </TabsTrigger>
            <TabsTrigger value="camera" className="flex items-center gap-2">
              <Camera className="h-4 w-4" />
              <span>Camera Defaults</span>
            </TabsTrigger>
          </TabsList>

          {/* Account Settings Tab */}
          <TabsContent value="account">
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>Update your personal information and mall contact details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      name="name"
                      value={accountSettings.name}
                      onChange={handleAccountInputChange}
                      className={accountErrors.name ? "border-destructive" : ""}
                    />
                    {accountErrors.name && <p className="text-sm text-destructive">{accountErrors.name}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={accountSettings.email}
                      onChange={handleAccountInputChange}
                      className={accountErrors.email ? "border-destructive" : ""}
                    />
                    {accountErrors.email && <p className="text-sm text-destructive">{accountErrors.email}</p>}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mallName">Mall Name</Label>
                  <Input id="mallName" value={accountSettings.mallName} disabled className="bg-muted" />
                  <p className="text-xs text-muted-foreground">
                    Mall name is set during mall setup and cannot be changed here
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="mallContactEmail">Mall Contact Email</Label>
                    <Input
                      id="mallContactEmail"
                      name="mallContactEmail"
                      type="email"
                      value={accountSettings.mallContactEmail}
                      onChange={handleAccountInputChange}
                      className={accountErrors.mallContactEmail ? "border-destructive" : ""}
                    />
                    {accountErrors.mallContactEmail && (
                      <p className="text-sm text-destructive">{accountErrors.mallContactEmail}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="mallContactNumber">Mall Contact Number</Label>
                    <Input
                      id="mallContactNumber"
                      name="mallContactNumber"
                      value={accountSettings.mallContactNumber}
                      onChange={handleAccountInputChange}
                      placeholder="123-456-7890"
                      className={accountErrors.mallContactNumber ? "border-destructive" : ""}
                    />
                    {accountErrors.mallContactNumber && (
                      <p className="text-sm text-destructive">{accountErrors.mallContactNumber}</p>
                    )}
                  </div>
                </div>
                <div className="space-y-6 pt-6">
                  <Separator />
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Danger Zone</h3>
                    <p className="text-sm text-muted-foreground">
                      These actions are destructive and cannot be reversed. Please proceed with caution.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="border-destructive/50">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-base">Delete Mall</CardTitle>
                        <CardDescription>Delete your registered mall and all associated data</CardDescription>
                      </CardHeader>
                      <CardFooter>
                        <Button variant="destructive" size="sm" onClick={() => setIsDeleteMallDialogOpen(true)}>
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete Mall
                        </Button>
                      </CardFooter>
                    </Card>

                    <Card className="border-destructive/50">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-base">Delete Account</CardTitle>
                        <CardDescription>Permanently delete your account and all associated data</CardDescription>
                      </CardHeader>
                      <CardFooter>
                        <Button variant="destructive" size="sm" onClick={() => setIsDeleteAccountDialogOpen(true)}>
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete Account
                        </Button>
                      </CardFooter>
                    </Card>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleSaveAccountSettings} disabled={isLoading}>
                  {isLoading ? (
                    "Saving..."
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Update Account
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Security Settings Tab */}
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <CardDescription>Update your password and security preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="currentPassword">Current Password</Label>
                  <Input
                    id="currentPassword"
                    name="currentPassword"
                    type="password"
                    value={securitySettings.currentPassword}
                    onChange={handleSecurityInputChange}
                    className={securityErrors.currentPassword ? "border-destructive" : ""}
                  />
                  {securityErrors.currentPassword && (
                    <p className="text-sm text-destructive">{securityErrors.currentPassword}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="newPassword">New Password</Label>
                    <Input
                      id="newPassword"
                      name="newPassword"
                      type="password"
                      value={securitySettings.newPassword}
                      onChange={handleSecurityInputChange}
                      className={securityErrors.newPassword ? "border-destructive" : ""}
                    />
                    {securityErrors.newPassword && (
                      <p className="text-sm text-destructive">{securityErrors.newPassword}</p>
                    )}
                    <p className="text-xs text-muted-foreground">Password must be at least 8 characters</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm New Password</Label>
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      value={securitySettings.confirmPassword}
                      onChange={handleSecurityInputChange}
                      className={securityErrors.confirmPassword ? "border-destructive" : ""}
                    />
                    {securityErrors.confirmPassword && (
                      <p className="text-sm text-destructive">{securityErrors.confirmPassword}</p>
                    )}
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleUpdatePassword} disabled={isLoading}>
                  {isLoading ? (
                    "Updating..."
                  ) : (
                    <>
                      <Lock className="mr-2 h-4 w-4" />
                      Update Password
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* Camera Defaults Tab */}
          <TabsContent value="camera">
            <Card>
              <CardHeader>
                <CardTitle>Default Camera Credentials</CardTitle>
                <CardDescription>Set default credentials for new camera configurations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  These default credentials will be pre-filled when adding new cameras in the camera configuration
                  section. You can still override these defaults for individual cameras.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="defaultUsername">Default RTSP Username</Label>
                    <Input
                      id="defaultUsername"
                      name="defaultUsername"
                      value={cameraDefaults.defaultUsername}
                      onChange={handleCameraDefaultsChange}
                      placeholder="admin"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="defaultPassword">Default RTSP Password</Label>
                    <Input
                      id="defaultPassword"
                      name="defaultPassword"
                      type="password"
                      value={cameraDefaults.defaultPassword}
                      onChange={handleCameraDefaultsChange}
                      placeholder="••••••••"
                    />
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button onClick={handleSaveCameraDefaults} disabled={isLoading}>
                  {isLoading ? (
                    "Saving..."
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Default Credentials
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      {/* Delete Mall Confirmation Dialog */}
      <Dialog open={isDeleteMallDialogOpen} onOpenChange={setIsDeleteMallDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-destructive flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Delete Mall
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete your mall and all data associated with it,
              including:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <ul className="list-disc pl-5 space-y-2 text-sm">
              <li>All camera configurations</li>
              <li>All homography mappings</li>
              <li>All analytics data and reports</li>
              <li>All zone and object definitions</li>
            </ul>

            <div className="space-y-2">
              <Label htmlFor="confirm-mall-delete" className="text-sm font-medium">
                Type <span className="font-bold">DELETE</span> to confirm
              </Label>
              <Input
                id="confirm-mall-delete"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="DELETE"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteMallDialogOpen(false)
                setDeleteConfirmText("")
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteMall}
              disabled={deleteConfirmText !== "DELETE" || isLoading}
            >
              {isLoading ? "Deleting..." : "Delete Mall"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Account Confirmation Dialog */}
      <Dialog open={isDeleteAccountDialogOpen} onOpenChange={setIsDeleteAccountDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-destructive flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Delete Account
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete your account and all data associated with it,
              including:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <ul className="list-disc pl-5 space-y-2 text-sm">
              <li>Your personal information</li>
              <li>All registered malls and their data</li>
              <li>All settings and preferences</li>
              <li>All access to the InsightCart platform</li>
            </ul>

            <div className="space-y-2">
              <Label htmlFor="confirm-account-delete" className="text-sm font-medium">
                Type <span className="font-bold">DELETE</span> to confirm
              </Label>
              <Input
                id="confirm-account-delete"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="DELETE"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsDeleteAccountDialogOpen(false)
                setDeleteConfirmText("")
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteAccount}
              disabled={deleteConfirmText !== "DELETE" || isLoading}
            >
              {isLoading ? "Deleting..." : "Delete Account"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AuthenticatedLayout>
  )
}

