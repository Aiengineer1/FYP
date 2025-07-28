"use client"

import { useState, useEffect } from "react"
import { BarChart, LineChart, Activity, Users, Camera, Filter, Wifi, WifiOff, Map, TrendingUp, AlertTriangle, Clock, ArrowLeft } from "lucide-react"
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
import { useAnalytics, useCameras, useRealTimeMetrics, useHeatmapData, useSectionAnalytics, useCustomerInsights, useAlerts, useTimeSeriesData, useCameraAnalytics } from "@/hooks/use-analytics"
import { useSocket } from "@/lib/socket-client"
import { useRouter } from "next/navigation"

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
  const router = useRouter()

  // Local state - declare first
  const [shelfInsightTab, setShelfInsightTab] = useState<string>("overall")
  const [customerInsightTab, setCustomerInsightTab] = useState<string>("route")
  const [cameraTab, setCameraTab] = useState<string>("all")
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>("today")

  // Filters - declare first
  const [rackFilter, setRackFilter] = useState<string>("all")
  const [genderFilter, setGenderFilter] = useState<string>("all")
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all")
  const [cameraFilter, setCameraFilter] = useState<string>("all")

  // Fetch data using SWR hooks with real backend APIs
  const { analytics, isLoading: analyticsLoading, isError: analyticsError, refresh: refreshAnalytics } = useAnalytics(user?.mall_id || null, selectedTimeRange, {
    gender: genderFilter !== 'all' ? genderFilter : undefined,
    ageGroup: ageGroupFilter !== 'all' ? ageGroupFilter : undefined,
    zone: rackFilter !== 'all' ? rackFilter : undefined,
    cameraId: cameraFilter !== 'all' ? parseInt(cameraFilter) : undefined,
  })

  const { cameras, isLoading: camerasLoading, isError: camerasError } = useCameras(user?.mall_id || null)
  const { realTimeMetrics, isLoading: metricsLoading } = useRealTimeMetrics(user?.mall_id || null)

  // New hooks for enhanced analytics
  const { heatmapData, refresh: refreshHeatmap } = useHeatmapData(user?.mall_id || null, {
    range: selectedTimeRange,
    gender: genderFilter !== 'all' ? genderFilter : undefined,
    ageGroup: ageGroupFilter !== 'all' ? ageGroupFilter : undefined,
    zone: rackFilter !== 'all' ? rackFilter : undefined,
  })

  const { sectionData, refresh: refreshSections } = useSectionAnalytics(user?.mall_id || null, {
    range: selectedTimeRange,
    gender: genderFilter !== 'all' ? genderFilter : undefined,
    ageGroup: ageGroupFilter !== 'all' ? ageGroupFilter : undefined,
    section: rackFilter !== 'all' ? rackFilter : undefined,
  })

  const { customerData, refresh: refreshCustomers } = useCustomerInsights(user?.mall_id || null, {
    range: selectedTimeRange,
    gender: genderFilter !== 'all' ? genderFilter : undefined,
    ageGroup: ageGroupFilter !== 'all' ? ageGroupFilter : undefined,
  })

  const { alerts, refresh: refreshAlerts } = useAlerts(user?.mall_id || null, {
    since: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // Last 24 hours
  })

  const { timeSeriesData, refresh: refreshTimeSeries } = useTimeSeriesData(user?.mall_id || null, {
    metric: 'visitors',
    range: selectedTimeRange,
    zone: rackFilter !== 'all' ? rackFilter : undefined,
  })

  const { cameraAnalytics, refresh: refreshCameraAnalytics } = useCameraAnalytics(user?.mall_id || null)

  // Ensure cameras is always an array with proper typing
  const camerasArray: any[] = Array.isArray(cameras) ? cameras : []

  // Real-time socket updates
  useEffect(() => {
    if (socket.isSocketConnected() && user?.mall_id) {
      socket.joinMallRoom(user.mall_id)

      // Subscribe to real-time updates
      socket.onAnalyticsUpdate((data: any) => {
        console.log('Analytics update received:', data)
        refreshAnalytics()
      })

      return () => {
        socket.leaveMallRoom(user.mall_id!)
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
            <Button onClick={() => refreshAnalytics()} className="w-full">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const camerasWithStatus = camerasArray.map((camera: any) => ({
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
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push('/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Analytical Dashboard</h1>
              <p className="text-muted-foreground">Real-time insights and analytics for your mall</p>
            </div>
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
              {sectionData?.[0]?.name || "N/A"}
            </motion.div>
            <p className="text-xs text-muted-foreground">
              {sectionData?.[0]?.visitorCount || 0} visitors
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
              {camerasArray.length}
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
          <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
          <TabsTrigger value="realtime">Real-time Monitoring</TabsTrigger>
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
                  data={(sectionData || []).map(section => ({
                    name: section.name,
                    value: section.visitorCount || (section.male + section.female)
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
                  data={sectionData || stayTimeData}
                  stackKeys={['male', 'female']}
                  height={300}
                  colors={['hsl(var(--chart-1))', 'hsl(var(--chart-2))']}
                />
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Heatmap Tab */}
        <TabsContent value="heatmap" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Map className="h-5 w-5" />
                  Zone Activity Heatmap
                </CardTitle>
                <CardDescription>Real-time visitor density across mall zones</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative w-full h-96 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg border-2 border-dashed border-muted">
                  {/* Mall Layout Background */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-muted-foreground text-sm">Mall Layout Map</div>
                  </div>

                  {/* Heatmap Points */}
                  {heatmapData.zones?.map((zone: any, index: number) => (
                    <motion.div
                      key={zone.name}
                      className="absolute w-8 h-8 rounded-full cursor-pointer"
                      style={{
                        left: `${zone.coordinates?.[0]?.[0] || 50}%`,
                        top: `${zone.coordinates?.[0]?.[1] || 50}%`,
                        backgroundColor: `hsl(var(--primary) / ${zone.density * 0.8})`,
                        border: '2px solid hsl(var(--primary) / 0.3)',
                        transform: 'translate(-50%, -50%)',
                      }}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: index * 0.1 }}
                      title={`${zone.name}: ${zone.visitorCount} visitors`}
                    >
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-foreground text-background text-xs px-2 py-1 rounded opacity-0 hover:opacity-100 transition-opacity whitespace-nowrap">
                        {zone.name}: {zone.visitorCount}
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Heatmap Legend */}
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-muted-foreground">Low Activity</span>
                    <div className="flex gap-1">
                      {[0.2, 0.4, 0.6, 0.8, 1.0].map((intensity) => (
                        <div
                          key={intensity}
                          className="w-4 h-4 rounded-full"
                          style={{
                            backgroundColor: `hsl(var(--primary) / ${intensity * 0.8})`,
                          }}
                        />
                      ))}
                    </div>
                    <span className="text-sm text-muted-foreground">High Activity</span>
                  </div>
                  <Badge variant="outline" className="flex items-center gap-1">
                    <Activity className="w-3 h-3" />
                    Live Data
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Zone Details */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Zone Activity Details</CardTitle>
                <CardDescription>Current visitor count and activity level by zone</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {heatmapData.zones?.map((zone: any, index: number) => (
                    <motion.div
                      key={zone.zone}
                      className="p-4 rounded-lg border bg-card"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{zone.name}</h4>
                        <Badge
                          variant={zone.density > 0.8 ? "destructive" : zone.density > 0.6 ? "default" : "secondary"}
                        >
                          {Math.round(zone.density * 100)}% Active
                        </Badge>
                      </div>
                      <div className="text-2xl font-bold">{zone.visitorCount}</div>
                      <div className="text-sm text-muted-foreground">Current Visitors</div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Real-time Monitoring Tab */}
        <TabsContent value="realtime" className="space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Real-time Activity Timeline
                </CardTitle>
                <CardDescription>Live visitor count and interaction trends</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Time Series Chart Placeholder */}
                  <div className="h-64 bg-gradient-to-r from-primary/5 to-secondary/5 rounded-lg border-2 border-dashed border-muted flex items-center justify-center">
                    <div className="text-center">
                      <LineChart className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                      <div className="text-muted-foreground">Time Series Chart</div>
                      <div className="text-sm text-muted-foreground">Visitor count over time</div>
                    </div>
                  </div>

                  {/* Current Stats */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-primary/10 rounded-lg">
                      <div className="text-2xl font-bold text-primary">{timeSeriesData[timeSeriesData.length - 1]?.visitors || 0}</div>
                      <div className="text-sm text-primary">Current Visitors</div>
                    </div>
                    <div className="text-center p-3 bg-secondary/10 rounded-lg">
                      <div className="text-2xl font-bold text-secondary">{timeSeriesData[timeSeriesData.length - 1]?.interactions || 0}</div>
                      <div className="text-sm text-secondary">Interactions</div>
                    </div>
                    <div className="text-center p-3 bg-accent/10 rounded-lg">
                      <div className="text-2xl font-bold text-accent">12:30</div>
                      <div className="text-sm text-accent">Peak Time</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Real-time Alerts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Live Alerts & Notifications
                </CardTitle>
                <CardDescription>Real-time system alerts and important updates</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.map((alert, index) => (
                    <motion.div
                      key={alert.id}
                      className="flex items-center justify-between p-3 rounded-lg border bg-card"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${alert.severity === 'warning' ? 'bg-accent' :
                            alert.severity === 'error' ? 'bg-destructive' : 'bg-primary'
                          }`} />
                        <div>
                          <div className="font-medium">{alert.message}</div>
                          <div className="text-sm text-muted-foreground flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {alert.time}
                          </div>
                        </div>
                      </div>
                      <Badge variant={alert.severity === 'warning' ? 'secondary' : alert.severity === 'error' ? 'destructive' : 'default'}>
                        {alert.severity}
                      </Badge>
                    </motion.div>
                  ))}
                </div>
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
                <CardTitle>Customer Demographics</CardTitle>
                <CardDescription>Visitor breakdown by gender and age</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Gender Distribution</h4>
                      <div className="flex items-center gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-primary">{customerData?.male || 0}</div>
                          <div className="text-sm text-muted-foreground">Male</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-secondary">{customerData?.female || 0}</div>
                          <div className="text-sm text-muted-foreground">Female</div>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Average Age</h4>
                      <div className="text-2xl font-bold">{customerData?.averageAge || 0} years</div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Age Groups</h4>
                    <div className="space-y-2">
                      {customerData?.ageGroups && Object.entries(customerData.ageGroups).map(([age, count]) => (
                        <motion.div
                          key={age}
                          className="flex items-center justify-between p-2 rounded-lg bg-muted"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                        >
                          <span className="font-medium">{age}</span>
                          <Badge variant="secondary">{count as number}</Badge>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
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
                <CardTitle>Peak Hours</CardTitle>
                <CardDescription>Busiest times of the day</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {(analytics.peakHours || []).map((hour, index) => (
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

