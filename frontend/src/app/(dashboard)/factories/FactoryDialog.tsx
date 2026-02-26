"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { apiClient } from "@/app/lib/api"
import { Factory, IndustryType } from "@/types"
import { Button } from "@/components/ui/button"
import {
    Dialog, DialogContent, DialogFooter,
    DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"


const INDUSTRIES: IndustryType[] = ["automotive", "metalworking", "textile", "electronics", "food_processing"]

interface Props {
    orgId: string
    factory?: Factory
}

export default function FactoryDialog({ orgId, factory }: Props) {
    const router = useRouter()
    const [open, setOpen] = useState(false)
    const [name, setName] = useState(factory?.name ?? "")
    const [industry, setIndustry] = useState<IndustryType>(factory?.industry ?? "automotive")
    const [city, setCity] = useState(factory?.city ?? "")
    const [countryCode, setCountryCode] = useState(factory?.country_code ?? "")
    const [postalCode, setPostalCode] = useState(factory?.postal_code ?? "")
    const [isActive, setIsActive] = useState(factory?.is_active ?? true)
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const isEdit = !!factory

    async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
        e.preventDefault()
        setLoading(true)
        setError(null)
        try {
            if (isEdit) {
                await apiClient.updateFactory(factory.id, { name, industry, city, country_code: countryCode, postal_code: postalCode, is_active: isActive })
            } else {
                await apiClient.createFactory(orgId, { name, industry, city, country_code: countryCode, postal_code: postalCode, is_active: isActive })
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
            setName(factory?.name ?? "")
            setIndustry(factory?.industry ?? "automotive")
            setCity(factory?.city ?? "")
            setCountryCode(factory?.country_code ?? "")
            setPostalCode(factory?.postal_code ?? "")
            setIsActive(factory?.is_active ?? true)
            setError(null)
        }
    }

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <Button variant={isEdit ? "outline" : "default"} size={isEdit ? "sm" : "default"}>
                    {isEdit ? "Edit" : "New Factory"}
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{isEdit ? "Edit Factory" : "New Factory"}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label htmlFor="name">Name</Label>
                            <Input id="name" value={name} onChange={e => setName(e.target.value)} required />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="industry">Industry</Label>
                            <Select value={industry} onValueChange={v => setIndustry(v as IndustryType)}>
                                <SelectTrigger id="industry">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {INDUSTRIES.map(ind => (
                                        <SelectItem key={ind} value={ind} className="capitalize">
                                            {ind.replace("_", " ")}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="city">City</Label>
                                <Input id="city" value={city} onChange={e => setCity(e.target.value)} required />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="country_code">Country Code</Label>
                                <Input id="country_code" value={countryCode} onChange={e => setCountryCode(e.target.value)} required maxLength={2} placeholder="e.g. DE" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="postal_code">Postal Code</Label>
                            <Input id="postal_code" value={postalCode} onChange={e => setPostalCode(e.target.value)} required />
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
