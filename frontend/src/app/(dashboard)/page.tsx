import { apiClient } from "@/app/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Building2, Factory, Cpu, Activity } from "lucide-react"
import Link from "next/link"


export default async function OverviewPage() {
    const [stats, recentMeasurements] = await Promise.all([
        apiClient.getStats(),
        apiClient.getMeasurements({ limit: 10 })
    ])

    const statCards = [
        { label: "Organizations", value: stats.organizations, icon: Building2, href: "/organizations" },
        { label: "Factories", value: stats.factories, icon: Factory, href: "/organizations" },
        { label: "Machines", value: stats.machines, icon: Cpu, href: "/organizations" },
        { label: "Measurements (24h)", value: stats.measurements_24h, icon: Activity, href: null },
    ]

    return (
        <div className="space-y-8">
            <h1 className="text-2xl font-bold">Overview</h1>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {statCards.map(card => (
                    <Card key={card.label}>
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">{card.label}</CardTitle>
                            <card.icon className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <p className="text-3xl font-bold">{card.value.toLocaleString()}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div>
                <h2 className="text-lg font-semibold mb-4">Recent Measurements</h2>
                {recentMeasurements.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No measurements recorded yet.</p>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Machine</TableHead>
                                <TableHead>Factory</TableHead>
                                <TableHead>Timestamp</TableHead>
                                <TableHead>Voltage</TableHead>
                                <TableHead>Current</TableHead>
                                <TableHead>RPM</TableHead>
                                <TableHead>Torque</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {recentMeasurements.map((m, i) => (
                                <TableRow key={i}>
                                    <TableCell>
                                        <Link href={`/machines/${m.machine_id}`} className="hover:underline font-medium">
                                            {m.machine_name}
                                        </Link>
                                    </TableCell>
                                    <TableCell className="text-muted-foreground text-sm">{m.factory_name}</TableCell>
                                    <TableCell className="text-muted-foreground text-sm">
                                        {new Date(m.timestamp).toLocaleString()}
                                    </TableCell>
                                    <TableCell className="text-sm">{m.voltage?.toFixed(2) ?? "—"}</TableCell>
                                    <TableCell className="text-sm">{m.current?.toFixed(2) ?? "—"}</TableCell>
                                    <TableCell className="text-sm">{m.rpm ?? "—"}</TableCell>
                                    <TableCell className="text-sm">{m.torque?.toFixed(2) ?? "—"}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </div>
        </div>
    )
}
