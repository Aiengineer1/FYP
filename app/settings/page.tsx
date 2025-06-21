"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Save, User, Lock, Camera, Trash2, AlertTriangle } from "lucide-react"

import { apiClient } from "@/lib/api-client"
import { useAuthStore } from "@/stores/auth-store"

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
    const router = useRouter()
    const { setMallId } = useAuthStore()
    const [isLoading, setIsLoading] = useState(false)
    const [userData, setUserData] = useState<any>(null)
    const [mallData, setMallData] = useState<any>(null)

    // Load user and mall data on component mount
    useEffect(() => {
        const loadData = async () => {
            try {
                const userDataStr = localStorage.getItem("user")
                if (!userDataStr) {
                    console.error("No user data found in localStorage")
                    toast({
                        title: "Error",
                        description: "User data not found. Please login again.",
                        variant: "destructive",
                    })
                    return
                }

                const user = JSON.parse(userDataStr)
                console.log("Loaded user data:", user)

                if (!user.user_id) {
                    console.error("User ID missing from user data")
                    toast({
                        title: "Error",
                        description: "Invalid user data. Please login again.",
                        variant: "destructive",
                    })
                    return
                }

                setUserData(user)

                const token = localStorage.getItem("token")
                if (!token) {
                    console.error("No auth token found in localStorage")
                    toast({
                        title: "Error",
                        description: "Authentication token not found. Please login again.",
                        variant: "destructive",
                    })
                    return
                }

                // Only fetch mall data if user has a mall_id
                if (user.mall_id) {
                    const response = await fetch(`http://localhost:8000/mall/${user.mall_id}`, {
                        headers: {
                            "Authorization": `Bearer ${token.trim()}`
                        }
                    })

                    if (!response.ok) {
                        if (response.status === 401) {
                            console.error("Token expired or invalid")
                            localStorage.removeItem("token")
                            localStorage.removeItem("user")
                            toast({
                                title: "Session Expired",
                                description: "Your session has expired. Please login again.",
                                variant: "destructive",
                            })
                            router.push("/login")
                            return
                        }
                        if (response.status === 404) {
                            // Mall was deleted - this is expected when user deletes their mall
                            console.log("Mall not found (likely deleted), continuing without mall data")
                            setMallData(null)
                            return
                        }
                        const errorData = await response.json()
                        throw new Error(errorData.detail || "Failed to fetch mall data")
                    }

                    const mallData = await response.json()
                    console.log("Loaded mall data:", mallData)
                    setMallData(mallData)
                } else {
                    console.log("User has no mall_id, skipping mall data fetch")
                    setMallData(null)
                }
            } catch (error) {
                console.error("Error loading data:", error)
                toast({
                    title: "Error",
                    description: error instanceof Error ? error.message : "Failed to load user and mall data",
                    variant: "destructive",
                })
            }
        }

        loadData()
    }, [toast, router])

    // Account settings state
    const [accountSettings, setAccountSettings] = useState({
        name: "",
        email: "",
        mallName: "",
        mallAddress: "",
    })

    // Update account settings when user/mall data changes
    useEffect(() => {
        if (userData || mallData) {
            setAccountSettings({
                name: userData?.name || "",
                email: userData?.email || "",
                mallName: mallData?.name || "",
                mallAddress: mallData?.address || "",
            })
        }
    }, [userData, mallData])

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
        mallAddress?: string
    }>({})

    const [securityErrors, setSecurityErrors] = useState<{
        currentPassword?: string
        newPassword?: string
        confirmPassword?: string
    }>({})

    const [isDeleteAccountDialogOpen, setIsDeleteAccountDialogOpen] = useState(false)
    const [isDeleteMallDialogOpen, setIsDeleteMallDialogOpen] = useState(false)
    const [deleteConfirmText, setDeleteConfirmText] = useState("")

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
            mallAddress?: string
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

        // Only validate mall address if user has a mall
        if (mallData && !accountSettings.mallAddress.trim()) {
            errors.mallAddress = "Mall address is required"
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
            const token = localStorage.getItem("token")
            if (!token) {
                throw new Error("Authentication token not found. Please login again.")
            }

            const userId = userData?.user_id
            if (!userId) {
                throw new Error("User ID not found. Please login again.")
            }

            // Prepare the update data as a complete object
            const updateData = {
                name: accountSettings.name,
                email: accountSettings.email,
            }

            // Check if user data has changed
            const userDataChanged = updateData.name !== userData?.name || updateData.email !== userData?.email

            // Check if mall data has changed (only if user has a mall)
            const mallDataChanged = mallData && accountSettings.mallAddress !== mallData.address

            // Only proceed if there are changes to update
            if (!userDataChanged && !mallDataChanged) {
                toast({
                    title: "No Changes",
                    description: "No changes were made to update.",
                });
                setIsLoading(false);
                return;
            }

            let mergedUserData = userData; // Default to current user data

            // Only update user data if it has changed
            if (userDataChanged) {
                console.log("Current user data:", userData);
                console.log("Sending update data:", updateData);

                // Update user data using the correct endpoint from backend
                const userResponse = await fetch(`http://localhost:8000/auth/user/update?user_id=${userId}`, {
                    method: "PUT",
                    headers: {
                        "Authorization": `Bearer ${token.trim()}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(updateData)
                })

                console.log("Response status:", userResponse.status);

                let responseData;
                try {
                    responseData = await userResponse.json();
                    console.log("Response data:", responseData);
                } catch (parseError) {
                    console.error("Error parsing response:", parseError);
                    responseData = null;
                }

                if (!userResponse.ok) {
                    if (userResponse.status === 401) {
                        localStorage.removeItem("token")
                        localStorage.removeItem("user")
                        router.push("/login")
                        throw new Error("Session expired. Please login again.")
                    }

                    // Handle error cases
                    console.error("Update error response:", responseData);
                    let errorMessage = "Failed to update user data";
                    if (responseData?.detail) {
                        if (typeof responseData.detail === 'object') {
                            errorMessage = responseData.detail.message || "Failed to update user data";
                        } else {
                            errorMessage = responseData.detail;
                        }
                    }

                    throw new Error(errorMessage);
                }

                if (!responseData) {
                    throw new Error("No data received from server");
                }

                // Ensure we preserve the user_id in local storage
                mergedUserData = {
                    ...responseData,
                    user_id: userId
                }
            }

            // Update mall address if it has changed
            if (mallDataChanged) {
                // Create URL with query parameters for mall update
                const mallUpdateUrl = new URL(`http://localhost:8000/mall/${mallData.id}`);
                mallUpdateUrl.searchParams.append("address", accountSettings.mallAddress);

                const mallResponse = await fetch(mallUpdateUrl.toString(), {
                    method: "PUT",
                    headers: {
                        "Authorization": `Bearer ${token.trim()}`
                    }
                })

                if (!mallResponse.ok) {
                    if (mallResponse.status === 401) {
                        localStorage.removeItem("token")
                        localStorage.removeItem("user")
                        router.push("/login")
                        throw new Error("Session expired. Please login again.")
                    }
                    const mallErrorData = await mallResponse.json()
                    throw new Error(mallErrorData.detail?.message || mallErrorData.detail || "Failed to update mall address")
                }

                const updatedMallData = await mallResponse.json()
                setMallData(updatedMallData)
            }

            // Update local storage with new user data
            localStorage.setItem("user", JSON.stringify(mergedUserData))
            setUserData(mergedUserData)

            console.log("Account settings updated successfully:", {
                user: mergedUserData,
                mall: mallData
            })

            toast({
                title: "Success",
                description: "Your account information has been successfully updated.",
            })
        } catch (error) {
            console.error("Error saving account settings:", error)
            toast({
                title: "Error",
                description: error instanceof Error ? error.message : "Failed to update account settings. Please try again.",
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
            if (!mallData?.id) {
                throw new Error("Mall ID not found")
            }

            // Call API to delete the mall using the recommended endpoint
            await apiClient.deleteMyMall()

            console.log("Mall deleted successfully")

            // Clear mall_id from user data using auth store (updates both localStorage and cookies)
            setMallId(null)

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
                description: error instanceof Error ? error.message : "Failed to delete mall. Please try again.",
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
            if (!userData?.user_id) {
                throw new Error("User ID not found")
            }

            // Call API to delete the user account using the recommended endpoint
            await apiClient.deleteMyAccount()

            console.log("Account deleted successfully")

            // Clear all user data from localStorage
            localStorage.removeItem("token")
            localStorage.removeItem("user")
            localStorage.removeItem("mallConfigured")

            // Clear any cached data
            if (typeof window !== 'undefined') {
                // Clear cookies
                document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
                document.cookie = "user=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
            }

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
                description: error instanceof Error ? error.message : "Failed to delete account. Please try again.",
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
                                    <Input
                                        id="mallName"
                                        value={accountSettings.mallName || (mallData ? "" : "No mall configured")}
                                        disabled
                                        className="bg-muted"
                                    />
                                    <p className="text-xs text-muted-foreground">
                                        {mallData
                                            ? "Mall name is set during mall setup and cannot be changed here"
                                            : "Set up a mall to configure mall-specific settings"
                                        }
                                    </p>
                                </div>

                                {mallData && (
                                    <div className="space-y-2">
                                        <Label htmlFor="mallAddress">Mall Address</Label>
                                        <Input
                                            id="mallAddress"
                                            name="mallAddress"
                                            value={accountSettings.mallAddress}
                                            onChange={handleAccountInputChange}
                                            className={accountErrors.mallAddress ? "border-destructive" : ""}
                                        />
                                        {accountErrors.mallAddress && (
                                            <p className="text-sm text-destructive">{accountErrors.mallAddress}</p>
                                        )}
                                    </div>
                                )}

                                <div className="space-y-6 pt-6">
                                    <Separator />
                                    <div className="space-y-2">
                                        <h3 className="text-lg font-medium">Danger Zone</h3>
                                        <p className="text-sm text-muted-foreground">
                                            These actions are destructive and cannot be reversed. Please proceed with caution.
                                        </p>
                                    </div>

                                    <div className={`grid grid-cols-1 ${mallData ? 'md:grid-cols-2' : ''} gap-6`}>
                                        {mallData && (
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
                                        )}

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

