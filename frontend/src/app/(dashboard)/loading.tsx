import { Skeleton } from "@/components/ui/skeleton"

export default function OverviewLoading() {
    return (
        <div className="space-y-8">
            <Skeleton className="h-8 w-32" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                    <Skeleton key={i} className="h-28 w-full" />
                ))}
            </div>
            <div>
                <Skeleton className="h-6 w-48 mb-4" />
                <div className="space-y-3">
                    {Array.from({ length: 5 }).map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                    ))}
                </div>
            </div>
        </div>
    )
}
