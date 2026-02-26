import { apiClient } from "@/app/lib/api"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import Breadcrumbs from "@/components/breadcrumbs"
import Link from "next/link"
import FactoryDialog from "../FactoryDialog"
import DeleteFactory from "../DeleteFactory"
import MachineDialog from "../../machines/MachineDialog"


export default async function FactoryPage({ params }: { params: Promise<{ factoryId: string }> }) {
    const { factoryId } = await params
    const factory = await apiClient.getFactoryById(factoryId)
    const [org, machines] = await Promise.all([
        apiClient.getOrganization(factory.organization_id),
        apiClient.getMachines(factoryId)
    ])

    return (
        <div>
            <Breadcrumbs items={[
                { label: "Organizations", href: "/organizations" },
                { label: org.name, href: `/organizations/${org.id}` },
                { label: factory.name },
            ]} />
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold">{factory.name}</h1>
                    <p className="text-sm text-muted-foreground mt-1 capitalize">
                        {factory.industry.replace("_", " ")} &middot; {factory.city}, {factory.country_code}
                    </p>
                </div>
                <div className="flex gap-2">
                    <FactoryDialog orgId={factory.organization_id} factory={factory} />
                    <DeleteFactory factoryId={factory.id} factoryName={factory.name} orgId={factory.organization_id} />
                </div>
            </div>

            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Machines</h2>
                <MachineDialog factoryId={factoryId} />
            </div>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Manufacturer / Model</TableHead>
                        <TableHead>Serial Number</TableHead>
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
                            <TableCell className="capitalize">{machine.machine_type.replace("_", " ")}</TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {machine.manufacturer ?? "—"}{machine.model ? ` / ${machine.model}` : ""}
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {machine.serial_number ?? "—"}
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {new Date(machine.installed_at).toLocaleDateString()}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>

            {machines.length === 0 && (
                <p className="text-sm text-muted-foreground mt-4">No machines registered for this factory.</p>
            )}
        </div>
    )
}
