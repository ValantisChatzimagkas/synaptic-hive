
export type IndustryType = "automotive" | "metalworking" | "textile" | "electronics" | "food_processing"
export type MachineType = "welding" | "press" | "lathe" | "assembly" | "conveyor"

export interface Organization {
    id: string
    name: string
    created_at: string
    is_active: boolean
}

export interface OrganizationCreate {
    name: string
    is_active?: boolean
}

export interface OrganizationUpdate {
    name?: string
    is_active?: boolean
}


export interface Factory {
    id: string
    organization_id: string
    name: string
    industry: IndustryType
    country_code: string
    city: string
    postal_code: string
    latitude?: number
    longitude?: number
    is_active: boolean
    registered_at: string
}

export interface FactoryCreate {
    name: string
    industry: IndustryType
    country_code: string
    city: string
    postal_code: string
    latitude?: number
    longitude?: number
    is_active?: boolean
}

export interface FactoryUpdate {
    name?: string
    industry?: IndustryType
    country_code?: string
    city?: string
    postal_code?: string
    latitude?: number
    longitude?: number
    is_active?: boolean
}


export interface Machine {
    id: string
    factory_id: string
    organization_id: string
    name: string
    machine_type: MachineType
    manufacturer?: string
    model?: string
    serial_number?: string
    meta: object
    installed_at: string
    last_seen_at?: string | null
}

export interface MachineCreate {
    name: string
    machine_type: MachineType
    manufacturer?: string
    model?: string
    serial_number?: string
    meta?: object
}

export interface MachineUpdate {
    name?: string
    machine_type?: MachineType
    manufacturer?: string
    model?: string
    serial_number?: string
    meta?: object
}


export interface MeasurementEvent {
    machine_id: string
    organization_id: string
    timestamp: string
    voltage?: number
    current?: number
    rpm?: number
    torque?: number
    additional_metrics?: object
    machine_name: string
    machine_type: MachineType
    factory_id: string
    factory_name: string
}

export interface MeasurementEventCreate {
    machine_id: string
    timestamp?: string
    voltage?: number
    current?: number
    rpm?: number
    torque?: number
    additional_metrics?: object
}

export interface PlatformStats {
    organizations: number
    factories: number
    machines: number
    measurements_24h: number
}

export interface MeasurementStatistics {
    machine_id: string
    machine_name: string
    time_range_start: string
    time_range_end: string
    total_measurements: number

    voltage_avg?: number
    voltage_min?: number
    voltage_max?: number
    
    current_avg?: number
    current_min?: number
    current_max?: number

    rpm_avg?: number
    rpm_min?: number
    rpm_max?: number

    torque_avg?: number
    torque_min?: number
    torque_max?: number
}


export interface AnomalyEvent {
    machine_id: string
    timestamp: string
    metric: string
    value: number
    score: number
    detector: string
}

export interface ActivityStats {
    hourly_measurements: { hour: string; count: number }[]
    top_anomalous_machines: { machine_id: string; machine_name: string; factory_name: string; organization_name: string; count: number }[]
}