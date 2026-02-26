import { apiClient } from "@/app/lib/api"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import Link from "next/link"
import Breadcrumbs from "@/components/breadcrumbs"
import OrganizationDialog from "../OrganizationDialog"
import DeleteOrganization from "../DeleteOrganization"
import FactoryDialog from "../../factories/FactoryDialog"


export default async function OrganizationPage({ params }: { params: Promise<{ orgId: string }> }) {
    const { orgId } = await params
    const [org, factories] = await Promise.all([
        apiClient.getOrganization(orgId),
        apiClient.getFactories(orgId)
    ])

    return (
        <div>
            <Breadcrumbs items={[
                { label: "Organizations", href: "/organizations" },
                { label: org.name },
            ]} />
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">{org.name}</h1>
                <div className="flex gap-2">
                    <OrganizationDialog org={org} />
                    <DeleteOrganization orgId={org.id} orgName={org.name} />
                </div>
            </div>

            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Factories</h2>
                <FactoryDialog orgId={orgId} />
            </div>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Industry</TableHead>
                        <TableHead>Location</TableHead>
                        <TableHead>Status</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {factories.map(factory => (
                        <TableRow key={factory.id}>
                            <TableCell>
                                <Link href={`/factories/${factory.id}`} className="hover:underline font-medium">
                                    {factory.name}
                                </Link>
                            </TableCell>
                            <TableCell className="capitalize">{factory.industry.replace("_", " ")}</TableCell>
                            <TableCell className="text-muted-foreground text-sm">{factory.city}, {factory.country_code}</TableCell>
                            <TableCell>
                                <Badge variant={factory.is_active ? "default" : "secondary"}>
                                    {factory.is_active ? "Active" : "Inactive"}
                                </Badge>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>

            {factories.length === 0 && (
                <p className="text-sm text-muted-foreground mt-4">No factories registered for this organization.</p>
            )}
        </div>
    )
}
