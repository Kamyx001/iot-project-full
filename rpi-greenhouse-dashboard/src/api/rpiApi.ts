import type { SensorData, Plant } from "../utils/sensorData.ts";
const BASE = "/api";

export async function fetchRpis(): Promise<SensorData[]> {
    const res = await fetch(`${BASE}/rpis`);
    if (!res.ok) {
        throw new Error("Failed to fetch RPIs");
    }

    return res.json();
}

export async function addRpi(rpi: Partial<SensorData>) {
    const res = await fetch(`${BASE}/rpis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rpi)
    });
    return res.json();
}

export async function updateRpi(id: number, data: Partial<SensorData>) {
    const res = await fetch(`${BASE}/rpis/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const json = await res.json();
        throw new Error(json.error || 'Failed to update RPI');
    }
    return res.json();
}

export async function deleteRpi(id: number) {
    const res = await fetch(`${BASE}/rpis/${id}`, {
        method: "DELETE",
    });
    if (!res.ok) {
        const json = await res.json();
        throw new Error(json.error || 'Failed to delete RPI');
    }
    return res.json();
}

export async function fetchReadings(): Promise<Pick<SensorData, "id" | "currTemperature" | "currHumidity" | "connectionStatus">[]> {
    const res = await fetch(`${BASE}/rpis/readings`);
    if (!res.ok) throw new Error("Failed to fetch readings");
    return res.json();
}

export async function fetchRpiHistory(id: number) {
    const res = await fetch(`${BASE}/rpis/${id}/history`);
    if (!res.ok) throw new Error("Failed to fetch history");
    return res.json();
}

export class ApiKeyError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ApiKeyError';
    }
}

export async function searchPlants(q: string): Promise<Plant[]> {
    const res = await fetch(`${BASE}/plants?q=${encodeURIComponent(q)}`);
    if (res.status === 401) {
        const data = await res.json();
        throw new ApiKeyError(data.error);
    }
    return res.json();
}

export async function setTrefleToken(token: string): Promise<{ status?: string; error?: string }> {
    const res = await fetch(`${BASE}/settings/trefle-token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token })
    });
    return res.json();
}

export async function checkTrefleToken(): Promise<{ configured: boolean }> {
    const res = await fetch(`${BASE}/settings/trefle-token`);
    return res.json();
}
