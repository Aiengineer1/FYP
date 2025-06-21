"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Loader2, Activity } from 'lucide-react'
import { useSocket } from '@/lib/socket-client'
import { apiClient } from '@/lib/api-client'
import { useAuthStore } from '@/stores/auth-store'
import { useToast } from '@/hooks/use-toast'

interface TestResult {
    name: string
    status: 'pending' | 'success' | 'error'
    message?: string
    duration?: number
}

export function IntegrationTest() {
    const [tests, setTests] = useState<TestResult[]>([])
    const [isRunning, setIsRunning] = useState(false)
    const { socket, isConnected, connectionStatus } = useSocket()
    const { user, token } = useAuthStore()
    const { toast } = useToast()

    const updateTest = (name: string, status: TestResult['status'], message?: string, duration?: number) => {
        setTests(prev => prev.map(test =>
            test.name === name
                ? { ...test, status, message, duration }
                : test
        ))
    }

    const runIntegrationTests = async () => {
        if (!user?.mall_id) {
            toast({
                title: 'Error',
                description: 'You must be logged in with a mall to run tests',
                variant: 'destructive'
            })
            return
        }

        setIsRunning(true)
        const startTime = Date.now()

        // Initialize tests
        const initialTests: TestResult[] = [
            { name: 'Backend Health Check', status: 'pending' },
            { name: 'Authentication Verification', status: 'pending' },
            { name: 'Mall Analytics API', status: 'pending' },
            { name: 'Real-time Metrics API', status: 'pending' },
            { name: 'System Status API', status: 'pending' },
            { name: 'WebSocket Connection', status: 'pending' },
            { name: 'Mall WebSocket Room', status: 'pending' },
            { name: 'System Notifications', status: 'pending' },
        ]

        setTests(initialTests)

        try {
            // Test 1: Backend Health Check
            const healthStart = Date.now()
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/`)
                if (response.ok) {
                    updateTest('Backend Health Check', 'success', 'Backend is reachable', Date.now() - healthStart)
                } else {
                    updateTest('Backend Health Check', 'error', `HTTP ${response.status}`)
                }
            } catch (error) {
                updateTest('Backend Health Check', 'error', 'Backend not reachable')
            }

            // Test 2: Authentication Verification
            const authStart = Date.now()
            try {
                await apiClient.verifyToken()
                updateTest('Authentication Verification', 'success', 'Token valid', Date.now() - authStart)
            } catch (error) {
                updateTest('Authentication Verification', 'error', 'Token verification failed')
            }

            // Test 3: Mall Analytics API
            const analyticsStart = Date.now()
            try {
                const analytics = await apiClient.getMallAnalytics(user.mall_id)
                updateTest('Mall Analytics API', 'success', `Received analytics data`, Date.now() - analyticsStart)
            } catch (error) {
                updateTest('Mall Analytics API', 'error', 'Analytics API failed')
            }

            // Test 4: Real-time Metrics API
            const metricsStart = Date.now()
            try {
                const metrics = await apiClient.getRealTimeMetrics(user.mall_id)
                updateTest('Real-time Metrics API', 'success', `Real-time data received`, Date.now() - metricsStart)
            } catch (error) {
                updateTest('Real-time Metrics API', 'error', 'Real-time API failed')
            }

            // Test 5: System Status API
            const statusStart = Date.now()
            try {
                const status = await apiClient.getSystemStatus()
                updateTest('System Status API', 'success', `FPS: ${status.fps}, Processing: ${status.processing_time}ms`, Date.now() - statusStart)
            } catch (error) {
                updateTest('System Status API', 'error', 'System status API failed')
            }

            // Test 6: WebSocket Connection
            const wsStart = Date.now()
            if (socket.isSocketConnected()) {
                updateTest('WebSocket Connection', 'success', `Connected: ${Object.keys(connectionStatus).join(', ')}`, Date.now() - wsStart)
            } else {
                updateTest('WebSocket Connection', 'error', 'WebSocket not connected')
            }

            // Test 7: Mall WebSocket Room
            const roomStart = Date.now()
            try {
                socket.joinMallRoom(user.mall_id)
                setTimeout(() => {
                    updateTest('Mall WebSocket Room', 'success', `Joined mall room ${user.mall_id}`, Date.now() - roomStart)
                }, 1000)
            } catch (error) {
                updateTest('Mall WebSocket Room', 'error', 'Failed to join mall room')
            }

            // Test 8: System Notifications Test
            const notifStart = Date.now()
            socket.onSystemMessage((data) => {
                updateTest('System Notifications', 'success', `Received: ${data.message}`, Date.now() - notifStart)
            })

            // Trigger a test notification after 2 seconds
            setTimeout(() => {
                const currentTest = tests.find(t => t.name === 'System Notifications')
                if (currentTest?.status === 'pending') {
                    updateTest('System Notifications', 'error', 'No notifications received in 2s')
                }
            }, 2000)

        } catch (error) {
            console.error('Integration test error:', error)
        } finally {
            setIsRunning(false)
        }
    }

    const getStatusIcon = (status: TestResult['status']) => {
        switch (status) {
            case 'success':
                return <CheckCircle className="w-4 h-4 text-green-500" />
            case 'error':
                return <XCircle className="w-4 h-4 text-red-500" />
            case 'pending':
                return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
        }
    }

    const getStatusBadge = (status: TestResult['status']) => {
        switch (status) {
            case 'success':
                return <Badge variant="outline" className="bg-green-50 text-green-700">Pass</Badge>
            case 'error':
                return <Badge variant="outline" className="bg-red-50 text-red-700">Fail</Badge>
            case 'pending':
                return <Badge variant="outline" className="bg-blue-50 text-blue-700">Running</Badge>
        }
    }

    const passedTests = tests.filter(t => t.status === 'success').length
    const failedTests = tests.filter(t => t.status === 'error').length
    const pendingTests = tests.filter(t => t.status === 'pending').length

    return (
        <Card className="w-full max-w-4xl mx-auto">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="w-5 h-5" />
                            Backend Integration Test
                        </CardTitle>
                        <CardDescription>
                            Test connectivity and functionality with your backend endpoints
                        </CardDescription>
                    </div>
                    <Button
                        onClick={runIntegrationTests}
                        disabled={isRunning || !user?.mall_id}
                        className="min-w-32"
                    >
                        {isRunning ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Testing...
                            </>
                        ) : (
                            'Run Tests'
                        )}
                    </Button>
                </div>

                {tests.length > 0 && (
                    <div className="flex gap-4 mt-4">
                        <div className="flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="text-sm">Passed: {passedTests}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <XCircle className="w-4 h-4 text-red-500" />
                            <span className="text-sm">Failed: {failedTests}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Loader2 className="w-4 h-4 text-blue-500" />
                            <span className="text-sm">Pending: {pendingTests}</span>
                        </div>
                    </div>
                )}
            </CardHeader>

            <CardContent>
                {tests.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                        Click "Run Tests" to start the integration test suite
                    </div>
                ) : (
                    <div className="space-y-3">
                        {tests.map((test, index) => (
                            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                                <div className="flex items-center gap-3">
                                    {getStatusIcon(test.status)}
                                    <div>
                                        <div className="font-medium">{test.name}</div>
                                        {test.message && (
                                            <div className="text-sm text-muted-foreground">{test.message}</div>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {test.duration && (
                                        <span className="text-xs text-muted-foreground">
                                            {test.duration}ms
                                        </span>
                                    )}
                                    {getStatusBadge(test.status)}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Connection Status */}
                <div className="mt-6 p-4 bg-muted rounded-lg">
                    <h4 className="font-medium mb-2">Current Connection Status</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span className="text-muted-foreground">User:</span> {user?.name || 'Not logged in'}
                        </div>
                        <div>
                            <span className="text-muted-foreground">Mall ID:</span> {user?.mall_id || 'None'}
                        </div>
                        <div>
                            <span className="text-muted-foreground">Backend URL:</span> {process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}
                        </div>
                        <div>
                            <span className="text-muted-foreground">WebSocket:</span> {isConnected ? 'Connected' : 'Disconnected'}
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
} 