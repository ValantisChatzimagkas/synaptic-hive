"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { apiClient } from "@/app/lib/api"
import { Button } from "@/components/ui/button"
import {
    Dialog, DialogContent, DialogFooter,
    DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog"


export default function DeleteMachine({ machineId, machineName, factoryId }: { machineId: string; machineName: string; factoryId: string }) {
    const router = useRouter()
    const [open, setOpen] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function handleDelete() {
        setLoading(true)
        setError(null)
        try {
            await apiClient.deleteMachine(machineId)
            router.push(`/factories/${factoryId}`)
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "An error occurred")
            setLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="destructive" size="sm">Delete</Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Delete Machine</DialogTitle>
                </DialogHeader>
                <p className="text-sm text-muted-foreground">
                    Are you sure you want to delete <span className="font-medium text-foreground">{machineName}</span>?
                    All measurement data for this machine will also be deleted. This action cannot be undone.
                </p>
                {error && <p className="text-sm text-destructive">{error}</p>}
                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                    <Button variant="destructive" onClick={handleDelete} disabled={loading}>
                        {loading ? "Deleting..." : "Delete"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
