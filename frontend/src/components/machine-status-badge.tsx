type Status = "active" | "idle" | "offline" | "no_data"

function getStatus(lastSeenAt: string | null | undefined): Status {
    if (!lastSeenAt) return "no_data"
    const diffMin = (Date.now() - new Date(lastSeenAt).getTime()) / 60_000
    if (diffMin < 5) return "active"
    if (diffMin < 60) return "idle"
    return "offline"
}

const STATUS_CONFIG: Record<Status, { label: string; color: string }> = {
    active:  { label: "Active",  color: "bg-green-500" },
    idle:    { label: "Idle",    color: "bg-yellow-400" },
    offline: { label: "Offline", color: "bg-red-500" },
    no_data: { label: "No data", color: "bg-gray-400" },
}

export default function MachineStatusBadge({ lastSeenAt }: { lastSeenAt?: string | null }) {
    const status = getStatus(lastSeenAt)
    const { label, color } = STATUS_CONFIG[status]

    return (
        <span className="inline-flex items-center gap-1.5">
            <span className={`inline-block h-2 w-2 rounded-full ${color}`} />
            <span className="text-sm text-muted-foreground">{label}</span>
        </span>
    )
}
