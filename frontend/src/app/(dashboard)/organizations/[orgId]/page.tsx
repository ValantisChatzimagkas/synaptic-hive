import { apiClient } from "@/app/lib/api";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import Link from "next/link"
import Breadcrumbs from "@/components/breadcrumbs"


export default async function OrganizationPage( {params}: {params: Promise<{orgId: string}>}) {
    const { orgId } = await params
    const [ org, factories ] = await Promise.all([
        apiClient.getOrganization(orgId),
        apiClient.getFactories(orgId)
    ])

    return (
        <div>
            <Breadcrumbs items={[
                { label: "Organizations", href: "/organizations" },
                { label: org.name },
            ]} />
            <div className="mb-6">
                <h1 className="text-2xl font-bold">{org.name}</h1>
            </div>

            <h2 className="text-lg font-semibold mb-4">Factories</h2>
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
                                <Badge variant={factory.is_active ? "default": "secondary"}>
                                    {factory.is_active ? "Active": "Inactive"}
                                </Badge>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}