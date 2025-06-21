/**
 * Performance Monitoring Utilities
 * Track component render times, API call performance, and memory usage
 */

import { config } from './config'

interface PerformanceMetric {
    name: string
    startTime: number
    endTime?: number
    duration?: number
    type: 'render' | 'api' | 'navigation' | 'custom'
    metadata?: Record<string, any>
}

class PerformanceMonitor {
    private metrics: PerformanceMetric[] = []
    private maxMetrics = 1000
    private isEnabled = config.dev.showPerformanceMetrics

    /**
     * Start tracking a performance metric
     */
    start(name: string, type: PerformanceMetric['type'] = 'custom', metadata?: Record<string, any>): void {
        if (!this.isEnabled) return

        const metric: PerformanceMetric = {
            name,
            startTime: performance.now(),
            type,
            metadata,
        }

        this.metrics.push(metric)

        // Keep only the latest metrics
        if (this.metrics.length > this.maxMetrics) {
            this.metrics = this.metrics.slice(-this.maxMetrics)
        }
    }

    /**
     * End tracking a performance metric
     */
    end(name: string): number | null {
        if (!this.isEnabled) return null

        const metric = this.metrics.find(m => m.name === name && !m.endTime)
        if (!metric) {
            console.warn(`Performance metric '${name}' not found or already ended`)
            return null
        }

        metric.endTime = performance.now()
        metric.duration = metric.endTime - metric.startTime

        // Log slow operations
        if (metric.duration > 1000) { // 1 second threshold
            console.warn(`Slow operation detected: ${name} took ${metric.duration.toFixed(2)}ms`, metric)
        }

        return metric.duration
    }

    /**
     * Measure a function execution time
     */
    async measure<T>(
        name: string,
        fn: () => T | Promise<T>,
        type: PerformanceMetric['type'] = 'custom',
        metadata?: Record<string, any>
    ): Promise<T> {
        if (!this.isEnabled) {
            return await fn()
        }

        this.start(name, type, metadata)
        try {
            const result = await fn()
            return result
        } finally {
            this.end(name)
        }
    }

    /**
     * Get performance metrics
     */
    getMetrics(type?: PerformanceMetric['type']): PerformanceMetric[] {
        if (!this.isEnabled) return []

        const completedMetrics = this.metrics.filter(m => m.duration !== undefined)
        return type ? completedMetrics.filter(m => m.type === type) : completedMetrics
    }

    /**
     * Get performance statistics
     */
    getStats(type?: PerformanceMetric['type']): {
        count: number
        average: number
        min: number
        max: number
        total: number
    } {
        const metrics = this.getMetrics(type)
        const durations = metrics.map(m => m.duration!).filter(d => d !== undefined)

        if (durations.length === 0) {
            return { count: 0, average: 0, min: 0, max: 0, total: 0 }
        }

        return {
            count: durations.length,
            average: durations.reduce((a, b) => a + b, 0) / durations.length,
            min: Math.min(...durations),
            max: Math.max(...durations),
            total: durations.reduce((a, b) => a + b, 0),
        }
    }

    /**
     * Clear all metrics
     */
    clear(): void {
        this.metrics = []
    }

    /**
     * Export metrics as JSON
     */
    export(): string {
        return JSON.stringify(this.getMetrics(), null, 2)
    }

    /**
     * Log performance summary
     */
    logSummary(): void {
        if (!this.isEnabled) return

        console.group('Performance Summary')
        console.log('Render Performance:', this.getStats('render'))
        console.log('API Performance:', this.getStats('api'))
        console.log('Navigation Performance:', this.getStats('navigation'))
        console.log('Custom Performance:', this.getStats('custom'))
        console.groupEnd()
    }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor()

/**
 * React hook for measuring component render time
 */
import { useEffect, useRef } from 'react'

export function usePerformanceMetric(name: string, metadata?: Record<string, any>) {
    const renderCount = useRef(0)

    useEffect(() => {
        renderCount.current++
        const metricName = `${name}_render_${renderCount.current}`

        performanceMonitor.start(metricName, 'render', {
            ...metadata,
            renderCount: renderCount.current,
        })

        return () => {
            performanceMonitor.end(metricName)
        }
    })
}

/**
 * Higher-order component for measuring component performance
 */
import React from 'react'

export function withPerformanceMetric<P extends object>(
    WrappedComponent: React.ComponentType<P>,
    componentName?: string
) {
    const displayName = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component'

    const WithPerformanceMetric = (props: P) => {
        usePerformanceMetric(displayName, { componentType: 'HOC' })
        return <WrappedComponent { ...props } />
    }

    WithPerformanceMetric.displayName = `withPerformanceMetric(${displayName})`
    return WithPerformanceMetric
}

/**
 * Decorator for measuring API call performance
 */
export function measureApiCall(target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value

    descriptor.value = async function (...args: any[]) {
        const methodName = `API_${propertyName}`
        performanceMonitor.start(methodName, 'api', {
            method: propertyName,
            args: args.length,
        })

        try {
            const result = await method.apply(this, args)
            return result
        } catch (error) {
            console.error(`API call ${propertyName} failed:`, error)
            throw error
        } finally {
            performanceMonitor.end(methodName)
        }
    }

    return descriptor
}

/**
 * Monitor memory usage
 */
export function getMemoryUsage(): {
    used: number
    total: number
    percentage: number
} | null {
    if (typeof window === 'undefined' || !('memory' in performance)) {
        return null
    }

    const memory = (performance as any).memory
    return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100,
    }
}

/**
 * Monitor page load performance
 */
export function getPageLoadMetrics(): {
    navigationStart: number
    domContentLoaded: number
    loadComplete: number
    firstPaint?: number
    firstContentfulPaint?: number
} | null {
    if (typeof window === 'undefined') return null

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    if (!navigation) return null

    const paintEntries = performance.getEntriesByType('paint')
    const firstPaint = paintEntries.find(entry => entry.name === 'first-paint')
    const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint')

    return {
        navigationStart: navigation.fetchStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
        loadComplete: navigation.loadEventEnd - navigation.fetchStart,
        firstPaint: firstPaint?.startTime,
        firstContentfulPaint: firstContentfulPaint?.startTime,
    }
}

/**
 * Performance debug panel (development only)
 */
export function logPerformanceMetrics(): void {
    if (!config.dev.showPerformanceMetrics) return

    console.group('🚀 InsightCart Performance Metrics')

    // Performance summary
    performanceMonitor.logSummary()

    // Memory usage
    const memory = getMemoryUsage()
    if (memory) {
        console.log('Memory Usage:', {
            used: `${(memory.used / 1024 / 1024).toFixed(2)} MB`,
            total: `${(memory.total / 1024 / 1024).toFixed(2)} MB`,
            percentage: `${memory.percentage.toFixed(1)}%`,
        })
    }

    // Page load metrics
    const pageLoad = getPageLoadMetrics()
    if (pageLoad) {
        console.log('Page Load Metrics:', {
            domContentLoaded: `${pageLoad.domContentLoaded.toFixed(2)}ms`,
            loadComplete: `${pageLoad.loadComplete.toFixed(2)}ms`,
            firstPaint: pageLoad.firstPaint ? `${pageLoad.firstPaint.toFixed(2)}ms` : 'N/A',
            firstContentfulPaint: pageLoad.firstContentfulPaint ? `${pageLoad.firstContentfulPaint.toFixed(2)}ms` : 'N/A',
        })
    }

    console.groupEnd()
}

// Auto-log performance metrics in development
if (config.dev.showPerformanceMetrics && typeof window !== 'undefined') {
    window.addEventListener('load', () => {
        setTimeout(logPerformanceMetrics, 1000)
    })
} 