import axios from "axios";
import { ActivityStats, AnomalyEvent, Factory, FactoryCreate, FactoryUpdate, Machine, MachineCreate, MachineUpdate, MachineWithContext, MeasurementEvent, MeasurementEventCreate, MeasurementStatistics, Organization, OrganizationCreate, OrganizationUpdate, PlatformStats } from "@/types";


// Server components use API_URL (internal Docker network).
// Client components use NEXT_PUBLIC_API_URL (publicly reachable from browser).
const API_URL =
    typeof window === "undefined"
        ? (process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL)
        : process.env.NEXT_PUBLIC_API_URL


const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})


api.interceptors.response.use(
    response => response,
    error => {
        if (!error.response) {
        error.message = 'Cannot connect to server. Is the backend running?'
        }
    return Promise.reject(error)
    }
)


export const apiClient = {

    // Stats
    getStats: async () => {
        const { data } = await api.get<PlatformStats>('/stats/')
        return data
    },

    getActivityStats: async () => {
        const { data } = await api.get<ActivityStats>('/stats/activity')
        return data
    },

    // Organization endpoints
    getOrganizations: async () => {
        const { data } = await api.get<Organization[]>('/organizations/')
        return data
    },

    getOrganization: async (orgId: string) => {
        const { data } = await api.get<Organization>(`/organizations/${orgId}`)
        return data
    },

    createOrganization: async (organizationData: OrganizationCreate) => {
        const { data } = await api.post<Organization>("/organizations/", organizationData)
        return data
    },

    updateOrganization: async (orgId: string, updateData: OrganizationUpdate) => {
        const { data } = await api.patch<Organization>(`/organizations/${orgId}`, updateData)
        return data
    },

    deleteOrganization: async (orgId:string) => {
        await api.delete(`/organizations/${orgId}`)
    },

    // Factory endpoints
    getFactories: async (orgId: string) => {
        const { data } = await api.get<Factory[]>(`/organizations/${orgId}/factories`)
        return data
    },

    getFactoryById: async (factoryId:string) => {
        const { data } = await api.get<Factory>(`/factories/${factoryId}`)
        return data
    },

    createFactory: async(orgId: string, createData: FactoryCreate) => {
        const { data } = await api.post<Factory>(`/organizations/${orgId}/factories`, createData)
        return data
    },

    updateFactory: async(factoryId: string, updateData: FactoryUpdate) => {
        const { data } = await api.patch<Factory>(`/factories/${factoryId}`, updateData)
        return data
    },

    deleteFactory: async(factoryId: string) => {
        await api.delete(`/factories/${factoryId}`)
    },

    // Machine endpoints
    getAllMachines: async () => {
        const { data } = await api.get<MachineWithContext[]>('/machines')
        return data
    },

    getMachines: async(factoryId: string) => {
        const { data } = await api.get<Machine[]>(`/factories/${factoryId}/machines`)
        return data
    },

    getMachine: async(machineId: string) => {
        const { data } = await api.get<Machine>(`/machines/${machineId}`)
        return data
    },

    createMachine: async (factoryId: string, createData: MachineCreate) => {
        const { data } = await api.post<Machine>(`/factories/${factoryId}/machines`, createData)
        return data
    },

    updateMachine: async (machineId: string, updateData: MachineUpdate) => {
        const { data } = await api.patch<Machine>(`/machines/${machineId}`, updateData)
        return data
    },

    deleteMachine: async (machineId: string) => {
        await api.delete(`/machines/${machineId}`)
    },

    // Measurement endpoints
    getMeasurements: async (params?: { machine_id?: string, factory_id?: string, start_time?: string, end_time?: string, limit?: number }) => {
        const { data } = await api.get<MeasurementEvent[]>('/measurements/', { params })
        return data
    },

    createMeasurement: async (measurementData: MeasurementEventCreate) => {
        const { data } = await api.post<MeasurementEvent>('/measurements/', measurementData)
        return data
    },

    getMeasurementStatistics: async (machineId: string, params?: { start_time?: string, end_time?: string }) => {
        const { data } = await api.get<MeasurementStatistics>(`/measurements/statistics/${machineId}`, { params })
        return data
    },

    getAnomalies: async (machineId: string, params?: { start_time?: string; end_time?: string; limit?: number }) => {
        const { data } = await api.get<AnomalyEvent[]>(`/machines/${machineId}/anomalies`, { params })
        return data
    },

}
