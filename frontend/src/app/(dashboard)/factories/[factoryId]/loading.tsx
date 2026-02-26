import { Skeleton } from "@/components/ui/skeleton"

export default function FactoryLoading() {
    return (
        <div>
            <Skeleton className="h-4 w-24 mb-2" />
            <Skeleton className="h-8 w-56 mb-1" />
            <Skeleton className="h-4 w-40 mb-6" />
            <Skeleton className="h-6 w-24 mb-4" />
            <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                ))}
            </div>
        </div>
    )
}
