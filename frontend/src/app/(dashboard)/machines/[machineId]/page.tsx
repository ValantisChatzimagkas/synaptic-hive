import { apiClient } from "@/app/lib/api"
import Breadcrumbs from "@/components/breadcrumbs"
import MachineCharts from "../MachineCharts"
import MachineStatisticsCard from "../MachineStatisticsCard"
import TimeRangeFilter from "../TimeRangeFilter"


export default async function MachinePage({
    params,
    searchParams,
}: {
    params: Promise<{ machineId: string }>
    searchParams: Promise<{ start_time?: string; end_time?: string }>
}) {
    const { machineId } = await params
    const { start_time, end_time } = await searchParams

    const machine = await apiClient.getMachine(machineId)
    const [factory, stats, measurements] = await Promise.all([
        apiClient.getFactoryById(machine.factory_id),
        apiClient.getMeasurementStatistics(machineId, { start_time, end_time }),
        apiClient.getMeasurements({ machine_id: machineId, limit: 50, start_time, end_time })
    ])

    return (
        <div className="space-y-6">
            <Breadcrumbs items={[
                { label: "Organizations", href: "/organizations" },
                { label: factory.name, href: `/factories/${machine.factory_id}` },
                { label: machine.name },
            ]} />
            <div>
                <h1 className="text-2xl font-bold">{machine.name}</h1>
                <p className="text-sm text-muted-foreground mt-1 capitalize">
                    {machine.machine_type.replace("_", " ")}
                    {machine.manufacturer ? ` · ${machine.manufacturer}` : ""}
                    {machine.model ? ` / ${machine.model}` : ""}
                </p>
            </div>

            <TimeRangeFilter />
            <MachineStatisticsCard stats={stats} />
            <MachineCharts measurements={measurements} />
        </div>
    )
}
