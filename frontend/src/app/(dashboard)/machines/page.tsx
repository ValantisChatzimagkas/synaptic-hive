import { apiClient } from "@/app/lib/api"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import MachineStatusBadge from "@/components/machine-status-badge"
import Link from "next/link"

export default async function MachinesPage() {
    const machines = await apiClient.getAllMachines()

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold">Machines</h1>
                <p className="text-sm text-muted-foreground mt-1">{machines.length} machine{machines.length !== 1 ? "s" : ""} across all factories</p>
            </div>

            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Factory</TableHead>
                        <TableHead>Organization</TableHead>
                        <TableHead>Manufacturer / Model</TableHead>
                        <TableHead>Installed</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {machines.map(machine => (
                        <TableRow key={machine.id}>
                            <TableCell>
                                <Link href={`/machines/${machine.id}`} className="hover:underline font-medium">
                                    {machine.name}
                                </Link>
                            </TableCell>
                            <TableCell><MachineStatusBadge lastSeenAt={machine.last_seen_at} /></TableCell>
                            <TableCell className="capitalize">{machine.machine_type.replace("_", " ")}</TableCell>
                            <TableCell>
                                <Link href={`/factories/${machine.factory_id}`} className="hover:underline text-sm">
                                    {machine.factory_name}
                                </Link>
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">{machine.organization_name}</TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {machine.manufacturer ?? "—"}{machine.model ? ` / ${machine.model}` : ""}
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {new Date(machine.installed_at).toLocaleDateString()}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>

            {machines.length === 0 && (
                <p className="text-sm text-muted-foreground mt-4">No machines registered yet.</p>
            )}
        </div>
    )
}
