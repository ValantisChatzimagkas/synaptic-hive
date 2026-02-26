import { Skeleton } from "@/components/ui/skeleton"

export default function OrganizationsLoading() {
    return (
        <div>
            <Skeleton className="h-8 w-48 mb-6" />
            <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                ))}
            </div>
        </div>
    )
}
