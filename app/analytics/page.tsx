"use client"

import { useState, useEffect } from "react"
import { BarChart, LineChart, Activity, Users, Camera, Filter, Wifi, WifiOff } from "lucide-react"
import { motion } from "framer-motion"

import AuthenticatedLayout from "@/components/authenticated-layout"
import ErrorBoundary from "@/components/error-boundary"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { CameraStream } from "@/components/camera-stream"
import { AnimatedBarChart, AnimatedStackedBarChart } from "@/components/charts/animated-bar-chart"

// Custom hooks
import { useAuthStore } from "@/stores/auth-store"
import { useAnalytics, useCameras, useRealTimeMetrics } from "@/hooks/use-analytics"
import { useSocket } from "@/lib/socket-client"

// Mock data for charts (fallback)
const stayTimeData = [
  { rack: "Rack 1", male: 45, female: 65, name: "Rack 1" },
  { rack: "Rack 2", male: 55, female: 40, name: "Rack 2" },
  { rack: "Rack 3", male: 35, female: 70, name: "Rack 3" },
  { rack: "Rack 4", male: 60, female: 50, name: "Rack 4" },
  { rack: "Rack 5", male: 25, female: 30, name: "Rack 5" },
  { rack: "Rack 6", male: 40, female: 60, name: "Rack 6" },
]

const racks = [
  { id: 1, name: "Rack 1", section: "Electronics" },
  { id: 2, name: "Rack 2", section: "Clothing" },
  { id: 3, name: "Rack 3", section: "Food" },
  { id: 4, name: "Rack 4", section: "Toys" },
  { id: 5, name: "Rack 5", section: "Home Goods" },
  { id: 6, name: "Rack 6", section: "Beauty" },
]

function AnalyticsContent() {
  const { user } = useAuthStore()
  const { socket, isConnected } = useSocket()

  // Fetch data using SWR hooks
  const { analytics, isLoading: analyticsLoading, isError: analyticsError, refresh: refreshAnalytics } = useAnalytics(user?.mall_id || null)
  const { cameras, isLoading: camerasLoading, isError: camerasError } = useCameras(user?.mall_id || null)
  const { realTimeMetrics, isLoading: metricsLoading } = useRealTimeMetrics(user?.mall_id || null)

  // Local state
  const [shelfInsightTab, setShelfInsightTab] = useState<string>("overall")
  const [customerInsightTab, setCustomerInsightTab] = useState<string>("route")
  const [cameraTab, setCameraTab] = useState<string>("all")
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>("today")

  // Filters
  const [rackFilter, setRackFilter] = useState<string>("all")
  const [genderFilter, setGenderFilter] = useState<string>("all")
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all")
  const [cameraFilter, setCameraFilter] = useState<string>("all")

  // Real-time socket updates
  useEffect(() => {
    if (socket.isSocketConnected() && user?.mall_id) {
      socket.joinMallRoom(user.mall_id)

      // Subscribe to real-time updates
      socket.onAnalyticsUpdate((data) => {
        console.log('Analytics update received:', data)
        refreshAnalytics()
      })

      socket.onVisitorUpdate((data) => {
        console.log('Visitor update received:', data)
        refreshAnalytics()
      })

      return () => {
        socket.leaveMallRoom(user.mall_id!)
        socket.off('analytics_update')
        socket.off('visitor_update')
      }
    }
  }, [socket, user?.mall_id, refreshAnalytics])

  // Loading state
  if (analyticsLoading || camerasLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <motion.div
          className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        />
      </div>
    )
  }

  // Error state
  if (analyticsError || camerasError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Analytics</CardTitle>
            <CardDescription>
              Failed to load analytics data. Please try again.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={refreshAnalytics} className="w-full">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const camerasWithStatus = cameras.map((camera: any) => ({
    ...camera,
    status: "Active" // Set all cameras as active by default
  }))

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analytical Dashboard</h1>
            <p className="text-muted-foreground">Real-time insights and analytics for your mall</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={isConnected ? "default" : "destructive"} className="flex items-center gap-1">
              {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
              {isConnected ? "Live" : "Offline"}
            </Badge>
            <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="today">Today</SelectItem>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </motion.div>

      {/* Real-time Metrics Cards */}
      <motion.div
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Interactions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <motion.div
              className="text-2xl font-bold"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 100, delay: 0.2 }}
            >
              {analytics.totalVisitors.toLocaleString()}
            </motion.div>
            <p className="text-xs text-muted-foreground">
              {realTimeMetrics.activeVisitors} currently active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Most Popular Section</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <motion.div
              className="text-2xl font-bold"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 100, delay: 0.3 }}
            >
              {analytics.popularSections[0]?.name || "N/A"}
            </motion.div>
            <p className="text-xs text-muted-foreground">
              {analytics.popularSections[0]?.visitorCount || 0} visitors
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Dwell Time</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <motion.div
              className="text-2xl font-bold"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 100, delay: 0.4 }}
            >
              {analytics.averageDwellTime}s
            </motion.div>
            <p className="text-xs text-muted-foreground">
              {realTimeMetrics.currentPeakHour ? "Peak hour" : "Normal period"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Cameras</CardTitle>
            <Camera className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <motion.div
              className="text-2xl font-bold"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 100, delay: 0.5 }}
            >
              {cameras.length}
            </motion.div>
            <p className="text-xs text-muted-foreground">
              All systems operational
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Charts Section */}
      <Tabs defaultValue="insights" className="space-y-4">
        <TabsList>
          <TabsTrigger value="insights">Shelf Insights</TabsTrigger>
          <TabsTrigger value="customer">Customer Insights</TabsTrigger>
          <TabsTrigger value="cameras">Camera Monitoring</TabsTrigger>
        </TabsList>

        <TabsContent value="insights" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Popular Sections</CardTitle>
                <CardDescription>Visitor count by mall sections</CardDescription>
              </CardHeader>
              <CardContent>
                <AnimatedBarChart
                  data={analytics.popularSections.map(section => ({
                    name: section.name,
                    value: section.visitorCount
                  }))}
                  height={300}
                />
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Gender Distribution by Section</CardTitle>
                <CardDescription>Male vs Female visitors by section</CardDescription>
              </CardHeader>
              <CardContent>
                <AnimatedStackedBarChart
                  data={stayTimeData}
                  stackKeys={['male', 'female']}
                  height={300}
                  colors={['hsl(var(--chart-1))', 'hsl(var(--chart-2))']}
                />
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="customer" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Peak Hours</CardTitle>
                <CardDescription>Busiest times of the day</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {analytics.peakHours.map((hour, index) => (
                    <motion.div
                      key={hour}
                      className="flex items-center justify-between p-2 rounded-lg bg-muted"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <span className="font-medium">{hour}</span>
                      <Badge variant="secondary">Peak</Badge>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        <TabsContent value="cameras" className="space-y-4">
          <motion.div
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            {camerasWithStatus.map((camera: any, index: number) => (
              <motion.div
                key={camera.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <CameraStream camera={camera} />
              </motion.div>
            ))}
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default function AnalyticsPage() {
  return (
    <AuthenticatedLayout>
      <ErrorBoundary>
        <AnalyticsContent />
      </ErrorBoundary>
    </AuthenticatedLayout>
  )
}

