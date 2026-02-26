"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { format } from "date-fns"
import { CalendarIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"


function toLocalDatetime(iso: string): { date: Date; time: string } {
    const d = new Date(iso)
    return {
        date: d,
        time: `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`,
    }
}

function buildISO(date: Date | undefined, time: string): string | undefined {
    if (!date) return undefined
    const [hours, minutes] = time ? time.split(":").map(Number) : [0, 0]
    const d = new Date(date)
    d.setHours(hours, minutes, 0, 0)
    return d.toISOString()
}


interface DateTimePickerProps {
    label: string
    date: Date | undefined
    time: string
    onDateChange: (d: Date | undefined) => void
    onTimeChange: (t: string) => void
}

function DateTimePicker({ label, date, time, onDateChange, onTimeChange }: DateTimePickerProps) {
    return (
        <div className="flex flex-col gap-1.5">
            <Label>{label}</Label>
            <div className="flex gap-2">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="outline" className="w-40 justify-start text-left font-normal">
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {date ? format(date, "MMM d, yyyy") : <span className="text-muted-foreground">Pick date</span>}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                        <Calendar mode="single" selected={date} onSelect={onDateChange} />
                    </PopoverContent>
                </Popover>
                <Input
                    type="time"
                    value={time}
                    onChange={e => onTimeChange(e.target.value)}
                    className="w-28"
                />
            </div>
        </div>
    )
}


export default function TimeRangeFilter() {
    const router = useRouter()
    const searchParams = useSearchParams()

    const startParam = searchParams.get("start_time")
    const endParam = searchParams.get("end_time")

    const parsedStart = startParam ? toLocalDatetime(startParam) : undefined
    const parsedEnd = endParam ? toLocalDatetime(endParam) : undefined

    const [startDate, setStartDate] = useState<Date | undefined>(parsedStart?.date)
    const [startTime, setStartTime] = useState(parsedStart?.time ?? "00:00")
    const [endDate, setEndDate] = useState<Date | undefined>(parsedEnd?.date)
    const [endTime, setEndTime] = useState(parsedEnd?.time ?? "23:59")

    function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
        e.preventDefault()
        const params = new URLSearchParams()
        const start = buildISO(startDate, startTime)
        const end = buildISO(endDate, endTime)
        if (start) params.set("start_time", start)
        if (end) params.set("end_time", end)
        router.push(`?${params.toString()}`)
    }

    function handleReset() {
        setStartDate(undefined)
        setStartTime("00:00")
        setEndDate(undefined)
        setEndTime("23:59")
        router.push("?")
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
            <DateTimePicker
                label="From"
                date={startDate}
                time={startTime}
                onDateChange={setStartDate}
                onTimeChange={setStartTime}
            />
            <DateTimePicker
                label="To"
                date={endDate}
                time={endTime}
                onDateChange={setEndDate}
                onTimeChange={setEndTime}
            />
            <Button type="submit">Apply</Button>
            <Button type="button" variant="outline" onClick={handleReset}>Reset</Button>
        </form>
    )
}
