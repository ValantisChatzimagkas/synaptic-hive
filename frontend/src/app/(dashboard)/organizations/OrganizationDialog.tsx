"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { apiClient } from "@/app/lib/api"
import { Organization } from "@/types"
import { Button } from "@/components/ui/button"
import {
    Dialog, DialogContent, DialogFooter,
    DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"


interface Props {
    org?: Organization
}

export default function OrganizationDialog({ org }: Props) {
    const router = useRouter()
    const [open, setOpen] = useState(false)
    const [name, setName] = useState(org?.name ?? "")
    const [isActive, setIsActive] = useState(org?.is_active ?? true)
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const isEdit = !!org

    async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
        e.preventDefault()
        setLoading(true)
        setError(null)
        try {
            if (isEdit) {
                await apiClient.updateOrganization(org.id, { name, is_active: isActive })
            } else {
                await apiClient.createOrganization({ name, is_active: isActive })
            }
            router.refresh()
            setOpen(false)
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "An error occurred")
        } finally {
            setLoading(false)
        }
    }

    function handleOpenChange(value: boolean) {
        setOpen(value)
        if (!value) {
            setName(org?.name ?? "")
            setIsActive(org?.is_active ?? true)
            setError(null)
        }
    }

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <Button variant={isEdit ? "outline" : "default"} size={isEdit ? "sm" : "default"}>
                    {isEdit ? "Edit" : "New Organization"}
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{isEdit ? "Edit Organization" : "New Organization"}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Name</Label>
                            <Input
                                id="name"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                required
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="is_active"
                                checked={isActive}
                                onChange={e => setIsActive(e.target.checked)}
                                className="h-4 w-4"
                            />
                            <Label htmlFor="is_active">Active</Label>
                        </div>
                        {error && <p className="text-sm text-destructive">{error}</p>}
                    </div>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? "Saving..." : isEdit ? "Save" : "Create"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    )
}
