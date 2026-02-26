"use client"

import {
Accordion,
AccordionContent,
AccordionItem,
AccordionTrigger,
} from "@/components/ui/accordion"

import {
Card,
CardContent,
} from "@/components/ui/card"

import {
Table,
TableBody,
TableCell,
TableRow,
TableHead,
TableHeader,
} from "@/components/ui/table"
import { MeasurementStatistics } from "@/types"


export default function MachineStatisticsCard({
stats,
}: {
stats: MeasurementStatistics
}) {
const filteredStats = Object.entries(stats).filter(
([key, value]) =>
    key.includes("_") && value != null
)

return (
<Accordion type="single" collapsible defaultValue="statistics">
    <AccordionItem value="statistics">
    <AccordionTrigger className="text-lg font-semibold">
        Statistics
    </AccordionTrigger>

    <AccordionContent>
        <Card className="mt-4">
        <CardContent className="pt-6">
            <Table>
            <TableHeader>
                <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead>Value</TableHead>
                </TableRow>
            </TableHeader>

            <TableBody>
                {filteredStats.map(([key, value]) => (
                <TableRow key={key}>
                    <TableCell className="font-medium">
                    {formatLabel(key)}
                    </TableCell>
                    <TableCell>{typeof value === "number" ? value.toFixed(2) : value}</TableCell>
                </TableRow>
                ))}
            </TableBody>
            </Table>
        </CardContent>
        </Card>
    </AccordionContent>
    </AccordionItem>
</Accordion>
)
}

function formatLabel(key: string) {
return key
.replace(/_/g, " ")
.replace(/\b\w/g, (char) => char.toUpperCase())
}