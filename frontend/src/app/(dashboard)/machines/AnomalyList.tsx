import { AnomalyEvent } from "@/types"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { format } from "date-fns"

const DETECTOR_LABELS: Record<string, string> = {
    iqr: "IQR",
    persist: "Persist",
}

export default function AnomalyList({ anomalies }: { anomalies: AnomalyEvent[] }) {
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

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    Anomalies <Badge variant="destructive">{anomalies.length}</Badge>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Time</TableHead>
                            <TableHead>Metric</TableHead>
                            <TableHead>Value</TableHead>
                            <TableHead>Detector</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {anomalies.map((a, i) => (
                            <TableRow key={i}>
                                <TableCell className="text-sm">{format(new Date(a.timestamp), "MMM d, HH:mm:ss")}</TableCell>
                                <TableCell className="capitalize">{a.metric}</TableCell>
                                <TableCell>{a.value.toFixed(2)}</TableCell>
                                <TableCell>
                                    <Badge variant="outline">{DETECTOR_LABELS[a.detector] ?? a.detector}</Badge>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}