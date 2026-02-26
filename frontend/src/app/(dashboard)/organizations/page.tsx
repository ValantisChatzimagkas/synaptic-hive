import { apiClient } from "@/app/lib/api"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import {
    Table, TableBody, TableCell,
    TableHead, TableHeader, TableRow
} from "@/components/ui/table"
import OrganizationDialog from "./OrganizationDialog"

export default async function OrganizationsPage() {
    const organizations = await apiClient.getOrganizations()

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold">Organizations</h1>
                <OrganizationDialog />
            </div>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {organizations.map(org => (
                        <TableRow key={org.id}>
                            <TableCell>
                                <Link href={`/organizations/${org.id}`} className="hover:underline font-medium">
                                    {org.name}
                                </Link>
                            </TableCell>
                            <TableCell>
                                <Badge variant={org.is_active ? "default" : "secondary"}>
                                    {org.is_active ? "Active" : "Inactive"}
                                </Badge>
                            </TableCell>
                            <TableCell className="text-muted-foreground text-sm">
                                {new Date(org.created_at).toLocaleDateString()}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}