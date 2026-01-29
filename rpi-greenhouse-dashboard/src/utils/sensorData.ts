import type {Range} from "./comfortLevel.ts";

export type ConnectionStatus = "connected" | "disconnected";

export type Plant = {
    id: string;
    commonName: string;
    scientificName: string;
    imageUrl: string;

    temperature: {
        warning: Range;
        critical: Range;
    } | null;

    humidity: {
        warning: Range;
        critical: Range;
    } | null;
};

export type SensorData = {
    id: number;
    rpiName: string;

    plant: Plant | null;
    currTemperature: number | null;
    currHumidity: number | null;
    connectionStatus: ConnectionStatus;
};