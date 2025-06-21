"use client"

import { IntegrationTest } from '@/components/integration-test'
import AuthenticatedLayout from '@/components/authenticated-layout'

export default function IntegrationTestPage() {
    return (
        <AuthenticatedLayout>
            <div className="container mx-auto py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold">Backend Integration Test</h1>
                    <p className="text-muted-foreground mt-2">
                        Test your frontend connection with the backend API and WebSocket endpoints
                    </p>
                </div>

                <IntegrationTest />

                <div className="mt-8 p-6 bg-muted/50 rounded-lg">
                    <h2 className="text-xl font-semibold mb-4">How to Use This Test</h2>
                    <div className="space-y-3 text-sm">
                        <div className="flex items-start gap-3">
                            <span className="font-medium text-blue-600">1.</span>
                            <div>
                                <strong>Start your backend:</strong> Make sure your FastAPI backend is running on port 8000
                                <code className="ml-2 px-2 py-1 bg-background rounded text-xs">python run.py</code>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <span className="font-medium text-blue-600">2.</span>
                            <div>
                                <strong>Login:</strong> Ensure you're logged in with a user that has a mall assigned
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <span className="font-medium text-blue-600">3.</span>
                            <div>
                                <strong>Run Tests:</strong> Click "Run Tests" to verify all backend connections are working
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <span className="font-medium text-blue-600">4.</span>
                            <div>
                                <strong>Check Results:</strong> Green = working, Red = needs attention
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    )
} 