import { AnomalyEvent, MeasurementStatistics } from "@/types"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { format } from "date-fns"

const METRIC_BASELINES: Partial<Record<string, keyof MeasurementStatistics>> = {
    voltage: "voltage_avg",
    current: "current_avg",
    rpm: "rpm_avg",
    torque: "torque_avg",
}

export default function AnomalyList({
    anomalies,
    stats,
}: {
    anomalies: AnomalyEvent[]
    stats: MeasurementStatistics
}) {
    if (anomalies.length === 0) {
        return (
            <Card>
                <CardHeader><CardTitle>Anomalies</CardTitle></CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">No anomalies detected in this time range.</p>
                </CardContent>
            </Card>
        )
    }

    const grouped = anomalies.reduce<Record<string, AnomalyEvent[]>>((acc, a) => {
        if (!acc[a.metric]) acc[a.metric] = []
        acc[a.metric].push(a)
        return acc
    }, {})

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    Anomalies <Badge variant="destructive">{anomalies.length}</Badge>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {Object.entries(grouped).map(([metric, events]) => {
                    const avgKey = METRIC_BASELINES[metric]
                    const avg = avgKey ? (stats[avgKey] as number | undefined) : undefined

                    return (
                        <div key={metric}>
                            <div className="flex items-center gap-2 mb-2">
                                <h3 className="font-semibold capitalize">{metric}</h3>
                                <Badge variant="outline">{events.length} event{events.length !== 1 ? "s" : ""}</Badge>
                                {avg != null && (
                                    <span className="text-xs text-muted-foreground">avg {avg.toFixed(2)}</span>
                                )}
                            </div>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Time</TableHead>
                                        <TableHead>Value</TableHead>
                                        {avg != null && <TableHead>Deviation</TableHead>}
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {events.map((a, i) => {
                                        const dev = avg != null ? ((a.value - avg) / avg) * 100 : null
                                        return (
                                            <TableRow key={i}>
                                                <TableCell className="text-sm text-muted-foreground">
                                                    {format(new Date(a.timestamp), "MMM d, HH:mm:ss")}
                                                </TableCell>
                                                <TableCell className="font-mono">{a.value.toFixed(2)}</TableCell>
                                                {dev != null && (
                                                    <TableCell className={dev > 0 ? "text-destructive font-medium" : "text-blue-500 font-medium"}>
                                                        {dev > 0 ? "+" : ""}{dev.toFixed(1)}%
                                                    </TableCell>
                                                )}
                                            </TableRow>
                                        )
                                    })}
                                </TableBody>
                            </Table>
                        </div>
                    )
                })}
            </CardContent>
        </Card>
    )
}
