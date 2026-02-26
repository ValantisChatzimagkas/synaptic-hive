"use client"

import { Button } from "@/components/ui/button"

interface ErrorMessageProps {
    error: Error
    reset: () => void
}

export default function ErrorMessage({ error, reset }: ErrorMessageProps) {
    return (
        <div className="flex flex-col items-start gap-4 py-8">
            <div>
                <h2 className="text-lg font-semibold mb-1">Something went wrong</h2>
                <p className="text-sm text-muted-foreground">{error.message}</p>
            </div>
            <Button variant="outline" onClick={reset}>Try again</Button>
        </div>
    )
}
