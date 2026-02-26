import { Skeleton } from "@/components/ui/skeleton"

export default function OrganizationLoading() {
    return (
        <div>
            <Skeleton className="h-4 w-24 mb-2" />
            <Skeleton className="h-8 w-56 mb-6" />
            <Skeleton className="h-6 w-24 mb-4" />
            <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                ))}
            </div>
        </div>
    )
}
