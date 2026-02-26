"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { MeasurementEvent } from "@/types"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"


const METRICS = [
    { key: "voltage", label: "Voltage", unit: "V" },
    { key: "current", label: "Current", unit: "A" },
    { key: "rpm",     label: "RPM",     unit: "" },
    { key: "torque",  label: "Torque",  unit: "Nm" },
]


export default function MachineCharts( {measurements}: { measurements: MeasurementEvent[] }) {
    const sorted = [...measurements].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    const activeMetrics = METRICS.filter(m =>  sorted.some(measurement => measurement[m.key as keyof MeasurementEvent] != null))
    if (activeMetrics.length === 0) {
        return <p className="text-sm text-muted-foreground">No measurement data available.</p>
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {activeMetrics.map(metric => {
        const config: ChartConfig = {
            [metric.key]: {
                label: metric.unit ? `${metric.label} (${metric.unit})` : metric.label,
                color: "hsl(var(--chart-1))"
            }
        }

    return (
        <Card key={metric.key}>
            <CardHeader>
                <CardTitle className="text-sm font-medium">{metric.label}</CardTitle>
            </CardHeader>
            <CardContent>
                <ChartContainer config={config} className="h-48">
                    <AreaChart data={sorted}>
                        <CartesianGrid vertical={false} />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={v => new Date(v).toLocaleTimeString()}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis tickLine={false} axisLine={false} width={40} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Area
                            dataKey={metric.key}
                            type="monotone"
                            fill={`var(--color-${metric.key})`}
                            stroke={`var(--color-${metric.key})`}
                            fillOpacity={0.2}
                            connectNulls
                        />
                    </AreaChart>
                </ChartContainer>
            </CardContent>
        </Card>
        )
        })}
        </div>
    )
}