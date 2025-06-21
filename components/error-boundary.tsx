"use client"

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

interface ErrorBoundaryState {
    hasError: boolean
    error: Error | null
    errorInfo: React.ErrorInfo | null
}

interface ErrorBoundaryProps {
    children: React.ReactNode
    fallback?: React.ComponentType<{ error: Error; retry: () => void }>
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props)
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        }
    }

    static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
        return {
            hasError: true,
            error
        }
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Error Boundary caught an error:', error)
        console.error('Error Info:', errorInfo)

        this.setState({
            error,
            errorInfo
        })

        // Call the optional onError callback
        if (this.props.onError) {
            this.props.onError(error, errorInfo)
        }

        // In production, you might want to send this to an error reporting service
        if (process.env.NODE_ENV === 'production') {
            // Example: Sentry.captureException(error, { extra: errorInfo })
        }
    }

    handleRetry = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        })
    }

    render() {
        if (this.state.hasError) {
            // Use custom fallback component if provided
            if (this.props.fallback) {
                const FallbackComponent = this.props.fallback
                return <FallbackComponent error={this.state.error!} retry={this.handleRetry} />
            }

            // Default error UI
            return <DefaultErrorUI error={this.state.error!} onRetry={this.handleRetry} />
        }

        return this.props.children
    }
}

interface DefaultErrorUIProps {
    error: Error
    onRetry: () => void
}

function DefaultErrorUI({ error, onRetry }: DefaultErrorUIProps) {
    const isDevelopment = process.env.NODE_ENV === 'development'

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
                        <AlertTriangle className="w-6 h-6 text-red-600" />
                    </div>
                    <CardTitle className="text-xl">Something went wrong</CardTitle>
                    <CardDescription>
                        An unexpected error occurred. Please try again or contact support if the problem persists.
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                    {isDevelopment && (
                        <div className="bg-red-50 border border-red-200 rounded-md p-3">
                            <p className="text-sm font-medium text-red-800 mb-2">Error Details (Development Mode):</p>
                            <code className="text-xs text-red-700 break-all">
                                {error.name}: {error.message}
                            </code>
                        </div>
                    )}

                    <div className="flex flex-col gap-2">
                        <Button onClick={onRetry} className="w-full">
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Try Again
                        </Button>

                        <Button
                            variant="outline"
                            onClick={() => window.location.href = '/dashboard'}
                            className="w-full"
                        >
                            <Home className="w-4 h-4 mr-2" />
                            Go to Dashboard
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

// HOC for wrapping components with error boundary
export function withErrorBoundary<T extends {}>(
    Component: React.ComponentType<T>,
    errorBoundaryConfig?: Omit<ErrorBoundaryProps, 'children'>
) {
    return function WrappedComponent(props: T) {
        return (
            <ErrorBoundary {...errorBoundaryConfig}>
                <Component {...props} />
            </ErrorBoundary>
        )
    }
}

// Hook for error handling in functional components
export function useErrorHandler() {
    const [error, setError] = React.useState<Error | null>(null)

    const throwError = React.useCallback((error: Error) => {
        setError(error)
        throw error
    }, [])

    const clearError = React.useCallback(() => {
        setError(null)
    }, [])

    // Throw error in next render if one exists
    React.useEffect(() => {
        if (error) {
            throw error
        }
    }, [error])

    return {
        throwError,
        clearError,
        hasError: error !== null
    }
}

export default ErrorBoundary 