"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { ChartDataPoint } from '@/types'

interface AnimatedBarChartProps {
    data: ChartDataPoint[]
    dataKey?: string
    xAxisKey?: string
    height?: number
    colors?: string[]
    showGrid?: boolean
    showTooltip?: boolean
    className?: string
}

const defaultColors = [
    'hsl(var(--chart-1))',
    'hsl(var(--chart-2))',
    'hsl(var(--chart-3))',
    'hsl(var(--chart-4))',
    'hsl(var(--chart-5))',
]

export function AnimatedBarChart({
    data,
    dataKey = 'value',
    xAxisKey = 'name',
    height = 300,
    colors = defaultColors,
    showGrid = true,
    showTooltip = true,
    className = '',
}: AnimatedBarChartProps) {
    const [animatedData, setAnimatedData] = React.useState<ChartDataPoint[]>([])

    React.useEffect(() => {
        // Animate data loading
        const timer = setTimeout(() => {
            setAnimatedData(data)
        }, 300)

        return () => clearTimeout(timer)
    }, [data])

    const containerVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                duration: 0.6,
                ease: "easeOut",
                staggerChildren: 0.1
            }
        }
    }

    const barVariants = {
        hidden: { scaleY: 0, originY: 1 },
        visible: {
            scaleY: 1,
            transition: {
                duration: 0.8,
                ease: "easeOut"
            }
        }
    }

    return (
        <motion.div
            className={className}
            variants={containerVariants}
            initial="hidden"
            animate="visible"
        >
            <ChartContainer
                config={{
                    [dataKey]: {
                        label: dataKey,
                        color: colors[0],
                    },
                }}
                className="h-full w-full"
            >
                <ResponsiveContainer width="100%" height={height}>
                    <BarChart data={animatedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        {showGrid && <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />}
                        <XAxis
                            dataKey={xAxisKey}
                            className="text-xs fill-muted-foreground"
                            tick={{ fontSize: 12 }}
                        />
                        <YAxis
                            className="text-xs fill-muted-foreground"
                            tick={{ fontSize: 12 }}
                        />
                        {showTooltip && (
                            <ChartTooltip
                                content={<ChartTooltipContent />}
                                cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }}
                            />
                        )}
                        <Bar dataKey={dataKey} radius={[4, 4, 0, 0]}>
                            {animatedData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={colors[index % colors.length]}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </ChartContainer>
        </motion.div>
    )
}

// Stacked bar chart variant
export function AnimatedStackedBarChart({
    data,
    stackKeys,
    xAxisKey = 'name',
    height = 300,
    colors = defaultColors,
    showGrid = true,
    showTooltip = true,
    className = '',
}: {
    data: any[]
    stackKeys: string[]
    xAxisKey?: string
    height?: number
    colors?: string[]
    showGrid?: boolean
    showTooltip?: boolean
    className?: string
}) {
    const [animatedData, setAnimatedData] = React.useState<any[]>([])

    React.useEffect(() => {
        const timer = setTimeout(() => {
            setAnimatedData(data)
        }, 300)

        return () => clearTimeout(timer)
    }, [data])

    return (
        <motion.div
            className={className}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
        >
            <ChartContainer
                config={stackKeys.reduce((acc, key, index) => ({
                    ...acc,
                    [key]: {
                        label: key,
                        color: colors[index % colors.length],
                    },
                }), {})}
                className="h-full w-full"
            >
                <ResponsiveContainer width="100%" height={height}>
                    <BarChart data={animatedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        {showGrid && <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />}
                        <XAxis
                            dataKey={xAxisKey}
                            className="text-xs fill-muted-foreground"
                            tick={{ fontSize: 12 }}
                        />
                        <YAxis
                            className="text-xs fill-muted-foreground"
                            tick={{ fontSize: 12 }}
                        />
                        {showTooltip && (
                            <ChartTooltip
                                content={<ChartTooltipContent />}
                                cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }}
                            />
                        )}
                        {stackKeys.map((key, index) => (
                            <Bar
                                key={key}
                                dataKey={key}
                                stackId="stack"
                                fill={colors[index % colors.length]}
                                radius={index === stackKeys.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]}
                            />
                        ))}
                    </BarChart>
                </ResponsiveContainer>
            </ChartContainer>
        </motion.div>
    )
} 