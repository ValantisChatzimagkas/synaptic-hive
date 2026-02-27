"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { ActivityStats } from "@/types"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { format } from "date-fns"
import { useRouter } from "next/navigation"


const measurementsConfig: ChartConfig = {
    count: { label: "Measurements", color: "hsl(var(--chart-1))" },
}

const anomaliesConfig: ChartConfig = {
    count: { label: "Anomalies", color: "hsl(var(--chart-2))" },
}


export default function DashboardCharts({ activity }: { activity: ActivityStats }) {
    const router = useRouter()

    const hourlyData = activity.hourly_measurements.map(d => ({
        hour: format(new Date(d.hour), "HH:mm"),
        count: d.count,
    }))

    const anomalyData = activity.top_anomalous_machines.map(m => ({
        ...m,
        label: `${m.machine_name} · ${m.factory_name}`,
    }))

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
                <CardHeader>
                    <CardTitle className="text-sm font-medium">Measurements — last 24h</CardTitle>
                </CardHeader>
                <CardContent>
                    {hourlyData.length === 0 ? (
                        <p className="text-sm text-muted-foreground">No measurements in the last 24 hours.</p>
                    ) : (
                        <ChartContainer config={measurementsConfig} className="h-52">
                            <BarChart data={hourlyData}>
                                <CartesianGrid vertical={false} />
                                <XAxis dataKey="hour" tickLine={false} axisLine={false} interval="preserveStartEnd" />
                                <YAxis tickLine={false} axisLine={false} width={36} />
                                <ChartTooltip content={<ChartTooltipContent />} />
                                <Bar dataKey="count" fill="var(--color-count)" radius={[3, 3, 0, 0]} />
                            </BarChart>
                        </ChartContainer>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-sm font-medium">Top anomalous machines — last 24h</CardTitle>
                </CardHeader>
                <CardContent>
                    {anomalyData.length === 0 ? (
                        <p className="text-sm text-muted-foreground">No anomalies detected in the last 24 hours.</p>
                    ) : (
                        <ChartContainer config={anomaliesConfig} className="h-52">
                            <BarChart
                                data={anomalyData}
                                layout="vertical"
                                onClick={e => {
                                    const machineId = e?.activePayload?.[0]?.payload?.machine_id
                                    if (machineId) router.push(`/machines/${machineId}`)
                                }}
                                style={{ cursor: "pointer" }}
                            >
                                <CartesianGrid horizontal={false} />
                                <XAxis type="number" tickLine={false} axisLine={false} />
                                <YAxis
                                    type="category"
                                    dataKey="label"
                                    tickLine={false}
                                    axisLine={false}
                                    width={160}
                                    tick={{ fontSize: 11 }}
                                />
                                <ChartTooltip
                                    content={<ChartTooltipContent />}
                                    formatter={(value, _name, props) => [
                                        `${value} anomalies — ${props.payload.organization_name}`,
                                        props.payload.machine_name,
                                    ]}
                                />
                                <Bar dataKey="count" fill="var(--color-count)" radius={[0, 3, 3, 0]} />
                            </BarChart>
                        </ChartContainer>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
