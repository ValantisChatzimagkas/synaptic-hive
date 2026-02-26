"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { apiClient } from "@/app/lib/api"
import { Machine, MachineType } from "@/types"
import { Button } from "@/components/ui/button"
import {
    Dialog, DialogContent, DialogFooter,
    DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"


const MACHINE_TYPES: MachineType[] = ["welding", "press", "lathe", "assembly", "conveyor"]

interface Props {
    factoryId: string
    machine?: Machine
}

export default function MachineDialog({ factoryId, machine }: Props) {
    const router = useRouter()
    const [open, setOpen] = useState(false)
    const [name, setName] = useState(machine?.name ?? "")
    const [machineType, setMachineType] = useState<MachineType>(machine?.machine_type ?? "welding")
    const [manufacturer, setManufacturer] = useState(machine?.manufacturer ?? "")
    const [model, setModel] = useState(machine?.model ?? "")
    const [serialNumber, setSerialNumber] = useState(machine?.serial_number ?? "")
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const isEdit = !!machine

    async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
        e.preventDefault()
        setLoading(true)
        setError(null)
        try {
            if (isEdit) {
                await apiClient.updateMachine(machine.id, {
                    name,
                    machine_type: machineType,
                    manufacturer: manufacturer || undefined,
                    model: model || undefined,
                    serial_number: serialNumber || undefined,
                })
            } else {
                await apiClient.createMachine(factoryId, {
                    name,
                    machine_type: machineType,
                    manufacturer: manufacturer || undefined,
                    model: model || undefined,
                    serial_number: serialNumber || undefined,
                })
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
            setName(machine?.name ?? "")
            setMachineType(machine?.machine_type ?? "welding")
            setManufacturer(machine?.manufacturer ?? "")
            setModel(machine?.model ?? "")
            setSerialNumber(machine?.serial_number ?? "")
            setError(null)
        }
    }

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <Button variant={isEdit ? "outline" : "default"} size={isEdit ? "sm" : "default"}>
                    {isEdit ? "Edit" : "New Machine"}
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{isEdit ? "Edit Machine" : "New Machine"}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Name</Label>
                            <Input id="name" value={name} onChange={e => setName(e.target.value)} required />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="machine_type">Type</Label>
                            <Select value={machineType} onValueChange={v => setMachineType(v as MachineType)}>
                                <SelectTrigger id="machine_type">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {MACHINE_TYPES.map(type => (
                                        <SelectItem key={type} value={type} className="capitalize">
                                            {type}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="manufacturer">Manufacturer</Label>
                                <Input id="manufacturer" value={manufacturer} onChange={e => setManufacturer(e.target.value)} placeholder="Optional" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="model">Model</Label>
                                <Input id="model" value={model} onChange={e => setModel(e.target.value)} placeholder="Optional" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="serial_number">Serial Number</Label>
                            <Input id="serial_number" value={serialNumber} onChange={e => setSerialNumber(e.target.value)} placeholder="Optional" />
                        </div>
                        {error && <p className="text-sm text-destructive">{error}</p>}
                    </div>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? "Saving..." : isEdit ? "Save" : "Create"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    )
}
