"use client"

import { useState } from "react"
import { BarChart, LineChart, Activity, Users, Camera, Filter } from "lucide-react"

import AuthenticatedLayout from "@/components/authenticated-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { BarChart as ReBarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

// Mock data for charts
const stayTimeData = [
  { rack: "Rack 1", male: 45, female: 65 },
  { rack: "Rack 2", male: 55, female: 40 },
  { rack: "Rack 3", male: 35, female: 70 },
  { rack: "Rack 4", male: 60, female: 50 },
  { rack: "Rack 5", male: 25, female: 30 },
  { rack: "Rack 6", male: 40, female: 60 },
]

// Mock cameras data
const cameras = [
  { id: 1, name: "Entrance North", location: "North Entrance", status: "Active" },
  { id: 2, name: "Food Court", location: "Level 2", status: "Active" },
  { id: 3, name: "Main Hallway", location: "Level 1", status: "Active" },
  { id: 4, name: "Parking A", location: "Basement", status: "Active" },
  { id: 5, name: "Electronics Section", location: "Level 3", status: "Active" },
  { id: 6, name: "Kids Zone", location: "Level 2", status: "Active" },
  { id: 7, name: "Clothing Department", location: "Level 1", status: "Active" },
  { id: 8, name: "Entrance South", location: "South Entrance", status: "Inactive" },
]

// Mock rack data
const racks = [
  { id: 1, name: "Rack 1", section: "Electronics" },
  { id: 2, name: "Rack 2", section: "Clothing" },
  { id: 3, name: "Rack 3", section: "Food" },
  { id: 4, name: "Rack 4", section: "Toys" },
  { id: 5, name: "Rack 5", section: "Home Goods" },
  { id: 6, name: "Rack 6", section: "Beauty" },
]

export default function AnalyticsPage() {
  const [shelfInsightTab, setShelfInsightTab] = useState<string>("overall")
  const [customerInsightTab, setCustomerInsightTab] = useState<string>("route")
  const [cameraTab, setCameraTab] = useState<string>("all")

  // Filters
  const [rackFilter, setRackFilter] = useState<string>("all")
  const [genderFilter, setGenderFilter] = useState<string>("all")
  const [ageGroupFilter, setAgeGroupFilter] = useState<string>("all")
  const [cameraFilter, setCameraFilter] = useState<string>("all")

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytical Dashboard</h1>
          <p className="text-muted-foreground">Real-time insights and analytics for your mall</p>
        </div>

        <Tabs defaultValue="shelf" className="space-y-6">
          <TabsList className="grid grid-cols-3 w-full max-w-md">
            <TabsTrigger value="shelf">Shelf Insights</TabsTrigger>
            <TabsTrigger value="customer">Customer Insights</TabsTrigger>
            <TabsTrigger value="camera">Camera Streaming</TabsTrigger>
          </TabsList>

          {/* Shelf Insights Tab */}
          <TabsContent value="shelf" className="space-y-6">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <CardTitle>Shelf Insights</CardTitle>
                    <CardDescription>Analyze shelf performance and customer interactions</CardDescription>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={shelfInsightTab === "overall" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setShelfInsightTab("overall")}
                    >
                      <BarChart className="h-4 w-4 mr-2" />
                      Overall Rack Insights
                    </Button>
                    <Button
                      variant={shelfInsightTab === "filter" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setShelfInsightTab("filter")}
                    >
                      <Filter className="h-4 w-4 mr-2" />
                      Filter by Rack
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {shelfInsightTab === "overall" ? (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Total Interactions</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">1,245</div>
                          <p className="text-xs text-muted-foreground">+12% from last week</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Most Popular Rack</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">Rack 3</div>
                          <p className="text-xs text-muted-foreground">Food Section</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Avg. Interaction Time</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">45s</div>
                          <p className="text-xs text-muted-foreground">-5% from last week</p>
                        </CardContent>
                      </Card>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Rack Interaction Distribution</CardTitle>
                      </CardHeader>
                      <CardContent className="h-80">
                        <ChartContainer
                          config={{
                            male: {
                              label: "Male",
                              color: "hsl(var(--chart-1))",
                            },
                            female: {
                              label: "Female",
                              color: "hsl(var(--chart-2))",
                            },
                          }}
                          className="h-full"
                        >
                          <ResponsiveContainer width="100%" height="100%">
                            <ReBarChart data={stayTimeData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="rack" />
                              <YAxis />
                              <ChartTooltip content={<ChartTooltipContent />} />
                              <Legend />
                              <Bar dataKey="male" fill="var(--color-male)" name="Male" />
                              <Bar dataKey="female" fill="var(--color-female)" name="Female" />
                            </ReBarChart>
                          </ResponsiveContainer>
                        </ChartContainer>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Rack</label>
                        <Select value={rackFilter} onValueChange={setRackFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select rack" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Racks</SelectItem>
                            {racks.map((rack) => (
                              <SelectItem key={rack.id} value={rack.id.toString()}>
                                {rack.name} ({rack.section})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Gender</label>
                        <Select value={genderFilter} onValueChange={setGenderFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select gender" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Genders</SelectItem>
                            <SelectItem value="male">Male</SelectItem>
                            <SelectItem value="female">Female</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Age Group</label>
                        <Select value={ageGroupFilter} onValueChange={setAgeGroupFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select age group" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Age Groups</SelectItem>
                            <SelectItem value="18-24">18-24</SelectItem>
                            <SelectItem value="25-34">25-34</SelectItem>
                            <SelectItem value="35-44">35-44</SelectItem>
                            <SelectItem value="45-54">45-54</SelectItem>
                            <SelectItem value="55+">55+</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">
                          {rackFilter === "all" ? "All Racks Performance" : `Rack ${rackFilter} Performance`}
                        </CardTitle>
                        <CardDescription>
                          {genderFilter !== "all" && `Filtered by ${genderFilter}`}
                          {ageGroupFilter !== "all" && genderFilter !== "all" && " and "}
                          {ageGroupFilter !== "all" && `age group ${ageGroupFilter}`}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="h-80">
                        <div className="flex items-center justify-center h-full text-muted-foreground">
                          {rackFilter === "all" ? (
                            <ChartContainer
                              config={{
                                male: {
                                  label: "Male",
                                  color: "hsl(var(--chart-1))",
                                },
                                female: {
                                  label: "Female",
                                  color: "hsl(var(--chart-2))",
                                },
                              }}
                              className="h-full"
                            >
                              <ResponsiveContainer width="100%" height="100%">
                                <ReBarChart data={stayTimeData}>
                                  <CartesianGrid strokeDasharray="3 3" />
                                  <XAxis dataKey="rack" />
                                  <YAxis />
                                  <ChartTooltip content={<ChartTooltipContent />} />
                                  <Legend />
                                  <Bar dataKey="male" fill="var(--color-male)" name="Male" />
                                  <Bar dataKey="female" fill="var(--color-female)" name="Female" />
                                </ReBarChart>
                              </ResponsiveContainer>
                            </ChartContainer>
                          ) : (
                            <div className="text-center">
                              <p>Detailed insights for Rack {rackFilter} would appear here</p>
                              <p className="text-sm">Apply filters to see specific demographic data</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Customer Insights Tab */}
          <TabsContent value="customer" className="space-y-6">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <CardTitle>Customer Insights</CardTitle>
                    <CardDescription>Analyze customer behavior and movement patterns</CardDescription>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={customerInsightTab === "route" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCustomerInsightTab("route")}
                    >
                      <Activity className="h-4 w-4 mr-2" />
                      Route Tracking
                    </Button>
                    <Button
                      variant={customerInsightTab === "interaction" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCustomerInsightTab("interaction")}
                    >
                      <Users className="h-4 w-4 mr-2" />
                      Product Interaction
                    </Button>
                    <Button
                      variant={customerInsightTab === "staytime" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCustomerInsightTab("staytime")}
                    >
                      <LineChart className="h-4 w-4 mr-2" />
                      Average Stay Time
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {customerInsightTab === "route" && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Gender</label>
                        <Select value={genderFilter} onValueChange={setGenderFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select gender" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Genders</SelectItem>
                            <SelectItem value="male">Male</SelectItem>
                            <SelectItem value="female">Female</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Age Group</label>
                        <Select value={ageGroupFilter} onValueChange={setAgeGroupFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select age group" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Age Groups</SelectItem>
                            <SelectItem value="18-24">18-24</SelectItem>
                            <SelectItem value="25-34">25-34</SelectItem>
                            <SelectItem value="35-44">35-44</SelectItem>
                            <SelectItem value="45-54">45-54</SelectItem>
                            <SelectItem value="55+">55+</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Time Period</label>
                        <Select defaultValue="today">
                          <SelectTrigger>
                            <SelectValue placeholder="Select time period" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="today">Today</SelectItem>
                            <SelectItem value="yesterday">Yesterday</SelectItem>
                            <SelectItem value="week">This Week</SelectItem>
                            <SelectItem value="month">This Month</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Customer Movement Heatmap</CardTitle>
                        <CardDescription>Visualizing customer traffic and dwell time across the mall</CardDescription>
                      </CardHeader>
                      <CardContent className="h-96">
                        <div className="relative h-full w-full bg-muted rounded-md overflow-hidden">
                          <img
                            src="/placeholder.svg?height=800&width=1200"
                            alt="Mall heatmap"
                            className="w-full h-full object-cover opacity-50"
                          />
                          <div className="absolute inset-0 flex items-center justify-center">
                            <p className="text-muted-foreground">Customer movement heatmap would appear here</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {customerInsightTab === "interaction" && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Total Interactions</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">3,721</div>
                          <p className="text-xs text-muted-foreground">+8% from last week</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Most Interactive Product</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">Electronics</div>
                          <p className="text-xs text-muted-foreground">Smartphones section</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base">Conversion Rate</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">24.5%</div>
                          <p className="text-xs text-muted-foreground">+2.3% from last week</p>
                        </CardContent>
                      </Card>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Product Interaction Analysis</CardTitle>
                        <CardDescription>Visualizing which products customers interact with most</CardDescription>
                      </CardHeader>
                      <CardContent className="h-80">
                        <div className="relative h-full w-full bg-muted rounded-md overflow-hidden">
                          <div className="absolute inset-0 flex items-center justify-center">
                            <p className="text-muted-foreground">Product interaction visualization would appear here</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {customerInsightTab === "staytime" && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Rack</label>
                        <Select value={rackFilter} onValueChange={setRackFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select rack" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Racks</SelectItem>
                            {racks.map((rack) => (
                              <SelectItem key={rack.id} value={rack.id.toString()}>
                                {rack.name} ({rack.section})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Gender</label>
                        <Select value={genderFilter} onValueChange={setGenderFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select gender" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Genders</SelectItem>
                            <SelectItem value="male">Male</SelectItem>
                            <SelectItem value="female">Female</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Age Group</label>
                        <Select value={ageGroupFilter} onValueChange={setAgeGroupFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select age group" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Age Groups</SelectItem>
                            <SelectItem value="18-24">18-24</SelectItem>
                            <SelectItem value="25-34">25-34</SelectItem>
                            <SelectItem value="35-44">35-44</SelectItem>
                            <SelectItem value="45-54">45-54</SelectItem>
                            <SelectItem value="55+">55+</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Average Stay Time by Rack</CardTitle>
                        <CardDescription>How long customers spend at each rack</CardDescription>
                      </CardHeader>
                      <CardContent className="h-80">
                        <ChartContainer
                          config={{
                            male: {
                              label: "Male",
                              color: "hsl(var(--chart-1))",
                            },
                            female: {
                              label: "Female",
                              color: "hsl(var(--chart-2))",
                            },
                          }}
                          className="h-full"
                        >
                          <ResponsiveContainer width="100%" height="100%">
                            <ReBarChart data={stayTimeData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="rack" />
                              <YAxis />
                              <ChartTooltip content={<ChartTooltipContent />} />
                              <Legend />
                              <Bar dataKey="male" fill="var(--color-male)" name="Male" />
                              <Bar dataKey="female" fill="var(--color-female)" name="Female" />
                            </ReBarChart>
                          </ResponsiveContainer>
                        </ChartContainer>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Camera Streaming Tab */}
          <TabsContent value="camera" className="space-y-6">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <CardTitle>Camera Streaming</CardTitle>
                    <CardDescription>View live camera feeds from around the mall</CardDescription>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={cameraTab === "all" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCameraTab("all")}
                    >
                      <Camera className="h-4 w-4 mr-2" />
                      All Cameras
                    </Button>
                    <Button
                      variant={cameraTab === "filter" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCameraTab("filter")}
                    >
                      <Filter className="h-4 w-4 mr-2" />
                      Filter by Camera
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {cameraTab === "all" ? (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {cameras
                        .filter((camera) => camera.status === "Active")
                        .map((camera) => (
                          <Card key={camera.id}>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-base">{camera.name}</CardTitle>
                              <CardDescription>{camera.location}</CardDescription>
                            </CardHeader>
                            <CardContent className="p-0">
                              <div className="aspect-video bg-muted relative">
                                <img
                                  src="/placeholder.svg?height=720&width=1280"
                                  alt={`${camera.name} stream`}
                                  className="w-full h-full object-cover"
                                />
                                <div className="absolute top-2 right-2">
                                  <Badge variant="outline" className="bg-green-50 text-green-700">
                                    Live
                                  </Badge>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2 md:col-span-3">
                        <label className="text-sm font-medium">Select Camera</label>
                        <Select value={cameraFilter} onValueChange={setCameraFilter}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select camera" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Cameras</SelectItem>
                            {cameras
                              .filter((camera) => camera.status === "Active")
                              .map((camera) => (
                                <SelectItem key={camera.id} value={camera.id.toString()}>
                                  {camera.name} ({camera.location})
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">
                          {cameraFilter === "all"
                            ? "Select a specific camera to view"
                            : `${cameras.find((c) => c.id.toString() === cameraFilter)?.name} Stream`}
                        </CardTitle>
                        {cameraFilter !== "all" && (
                          <CardDescription>
                            {cameras.find((c) => c.id.toString() === cameraFilter)?.location}
                          </CardDescription>
                        )}
                      </CardHeader>
                      <CardContent className="p-0">
                        {cameraFilter === "all" ? (
                          <div className="h-96 flex items-center justify-center bg-muted">
                            <p className="text-muted-foreground">Please select a specific camera to view its stream</p>
                          </div>
                        ) : (
                          <div className="aspect-video bg-muted relative">
                            <img
                              src="/placeholder.svg?height=720&width=1280"
                              alt={`Camera ${cameraFilter} stream`}
                              className="w-full h-full object-cover"
                            />
                            <div className="absolute top-4 right-4">
                              <Badge variant="outline" className="bg-green-50 text-green-700">
                                Live
                              </Badge>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AuthenticatedLayout>
  )
}

