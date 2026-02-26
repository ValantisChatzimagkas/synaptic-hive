"use client"

import { Building2 } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
    Sidebar, SidebarContent, SidebarHeader,
    SidebarMenu, SidebarMenuButton, SidebarMenuItem
} from "@/components/ui/sidebar"

export function AppSidebar() {
    const pathname = usePathname()

    return (
        <Sidebar>
            <SidebarHeader>
                <span className="font-semibold text-sm px-2">Synaptic Hive</span>
            </SidebarHeader>
            <SidebarContent>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton asChild isActive={pathname.startsWith("/organizations")}>
                            <Link href="/organizations">
                                <Building2 />
                                Organizations
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarContent>
        </Sidebar>
    )
}