"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  ShoppingBag,
  LayoutDashboard,
  Settings,
  LogOut,
  Camera,
  Map,
  ChevronDown,
  BarChart2,
  Menu,
  X,
} from "lucide-react"

import { Button } from "@/components/ui/button"

export default function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [isAdminOpen, setIsAdminOpen] = useState(false)

  // Auto-expand admin panel when on admin pages
  useEffect(() => {
    if (pathname.startsWith("/admin")) {
      setIsAdminOpen(true)
    }
  }, [pathname])

  // Mock mall data - in a real app, this would come from an API or context
  const mall = {
    name: "Central City Mall",
    status: "Active",
  }

  return (
    <div className="flex min-h-screen">
      {/* Mobile sidebar toggle */}
      <div className="fixed top-4 left-4 z-50 md:hidden">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="bg-background"
        >
          {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 transform transition-transform duration-300 ease-in-out ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } md:relative md:translate-x-0`}
      >
        <div className="flex flex-col h-full border-r bg-background">
          <div className="border-b px-6 py-3 flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-2">
              <ShoppingBag className="h-6 w-6" />
              <span className="font-bold text-xl">RetailIQ</span>
            </Link>
            <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setIsSidebarOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto py-4">
            <div className="px-6 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">Mall</span>
              </div>
              <div className="mt-1">
                <p className="font-medium">{mall.name}</p>
                <div className="flex items-center mt-1">
                  <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded-full">{mall.status}</span>
                </div>
              </div>
            </div>

            <div className="space-y-1 px-3">
              <Link href="/dashboard">
                <Button variant={pathname === "/dashboard" ? "secondary" : "ghost"} className="w-full justify-start">
                  <LayoutDashboard className="mr-2 h-5 w-5" />
                  <span>Dashboard</span>
                </Button>
              </Link>

              {/* Admin Panel Button */}
              <div className="space-y-1">
                <Button variant="ghost" className="w-full justify-between" onClick={() => setIsAdminOpen(!isAdminOpen)}>
                  <div className="flex items-center">
                    <Settings className="mr-2 h-5 w-5" />
                    <span>Admin Panel</span>
                  </div>
                  <ChevronDown
                    className={`h-4 w-4 transition-transform duration-200 ${isAdminOpen ? "rotate-180" : ""}`}
                  />
                </Button>

                {/* Admin Panel Submenu */}
                <div
                  className={`pl-8 space-y-1 overflow-hidden transition-all duration-200 ${isAdminOpen ? "max-h-20" : "max-h-0"}`}
                >
                  <Link href="/admin/camera-config">
                    <Button
                      variant={pathname === "/admin/camera-config" ? "secondary" : "ghost"}
                      className="w-full justify-start"
                      size="sm"
                    >
                      <Camera className="mr-2 h-4 w-4" />
                      <span>Camera Configuration</span>
                    </Button>
                  </Link>
                  <Link href="/admin/homography-mapping">
                    <Button
                      variant={pathname === "/admin/homography-mapping" ? "secondary" : "ghost"}
                      className="w-full justify-start"
                      size="sm"
                    >
                      <Map className="mr-2 h-4 w-4" />
                      <span>Homography Mapping</span>
                    </Button>
                  </Link>
                </div>
              </div>

              <Link href="/analytics">
                <Button variant={pathname === "/analytics" ? "secondary" : "ghost"} className="w-full justify-start">
                  <BarChart2 className="mr-2 h-5 w-5" />
                  <span>Analytical Dashboard</span>
                </Button>
              </Link>
            </div>
          </div>

          <div className="border-t p-6">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
                <span className="text-sm font-medium">JD</span>
              </div>
              <div>
                <p className="text-sm font-medium">John Doe</p>
                <p className="text-xs text-muted-foreground">john.doe@example.com</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6">
          <div className="hidden md:block">
            <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
              <Menu className="h-5 w-5" />
            </Button>
          </div>
          <div className="flex-1" />
          <nav className="flex items-center gap-4">
            <Link href="/settings">
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
                <span className="sr-only">Settings</span>
              </Button>
            </Link>
            <Link href="/logout">
              <Button variant="ghost" size="icon">
                <LogOut className="h-5 w-5" />
                <span className="sr-only">Logout</span>
              </Button>
            </Link>
          </nav>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}

