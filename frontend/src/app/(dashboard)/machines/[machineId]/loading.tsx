import { Skeleton } from "@/components/ui/skeleton"

export default function MachineLoading() {
    return (
        <div className="space-y-6">
            <div>
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-8 w-56 mb-1" />
                <Skeleton className="h-4 w-40" />
            </div>

            {/* Time range filter */}
            <div className="flex gap-4">
                <Skeleton className="h-10 w-48" />
                <Skeleton className="h-10 w-48" />
                <Skeleton className="h-10 w-20" />
            </div>

            {/* Statistics accordion */}
            <Skeleton className="h-12 w-full" />

            {/* Charts grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Array.from({ length: 4 }).map((_, i) => (
                    <Skeleton key={i} className="h-64 w-full" />
                ))}
            </div>
        </div>
    )
}
