"use client"

import ErrorMessage from "@/components/error-message"

export default function OrganizationsError({ error, reset }: { error: Error; reset: () => void }) {
    return <ErrorMessage error={error} reset={reset} />
}
