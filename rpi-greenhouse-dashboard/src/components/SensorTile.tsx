import {Thermometer, Droplet, Ellipsis, Wifi, WifiOff, Trash2} from "lucide-react";
import type {ComfortState} from "../utils/comfortLevel.ts";
import {getLevel, combineLevels} from "../utils/comfortLevel.ts";
import {type SensorData} from "../utils/sensorData.ts";

type SensorTileProps = {
    data: SensorData;
    onClick: () => void;
    onDelete?: (id: string) => void;
};

function SensorTile({data, onClick, onDelete}: SensorTileProps) {
    const {
        rpiName,
        currTemperature,
        currHumidity,
        plant
    } = data;

    const hasPlant = data.plant !== null;
    const hasReadings =
        typeof currTemperature === "number" && typeof currHumidity === "number";

    let comfLevel: ComfortState | null = null;
    let tempLvl: ComfortState | null = null;
    let humLvl: ComfortState | null = null;

    if (hasPlant && hasReadings) {
        if (data.plant!.temperature) {
            tempLvl = getLevel(
                currTemperature,
                data.plant!.temperature.warning,
                data.plant!.temperature.critical
            );
        }

        if (data.plant!.humidity) {
            humLvl = getLevel(
                currHumidity,
                data.plant!.humidity.warning,
                data.plant!.humidity.critical
            );
        }

        if (tempLvl && humLvl) {
            comfLevel = combineLevels(tempLvl, humLvl);
        }
    }

    const comfortBorder = {
        green: "border-emerald-800",
        yellow: "border-amber-700",
        red: "border-red-500"
    };
    const comfortText = {
        green: "text-emerald-400",
        yellow: "text-amber-400",
        red: "text-red-500"
    };

    return (
        <div className={`flex flex-col p-5 gap-5 rounded-2xl bg-emerald-950 ${ comfLevel !== null ? comfortBorder[comfLevel] : ""} border-2`}>

            <div className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">{rpiName}</span>

                    {data.connectionStatus === "connected" && (
                        <Wifi className="text-emerald-400" size={18} />
                    )}
                    {(data.connectionStatus === "disconnected" || data.connectionStatus == null) && (
                        <WifiOff className="text-red-500" size={18} />
                    )}
                </div>

                <div className="flex gap-2">
                    {(data.connectionStatus === "disconnected" || data.connectionStatus == null) && onDelete && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                if (confirm(`Delete ${rpiName}?`)) {
                                    onDelete(data.id);
                                }
                            }}
                            className="bg-red-900 p-1.5 rounded-full transition-colors hover:bg-red-700"
                            title="Delete RPI"
                        >
                            <Trash2 size={18} />
                        </button>
                    )}
                    <button onClick={onClick}
                            className="bg-zinc-900 p-1.5 rounded-full transition-colors hover:bg-emerald-600">
                        <Ellipsis/>
                    </button>
                </div>
            </div>
            {/*The 2nd row*/}
            <div className="flex flex-row items-stretch gap-3 ">
                {/*Inner 1st COL*/}
                <div className="flex flex-col justify-around gap-2 w-3/5">
                    <span className="text-xl">{hasPlant ? plant!.commonName : "No plant assigned"}</span>
                    <div className="items-center">
                        { hasReadings ?
                            (
                                <>
                                    <div className={`flex items-center gap-2 ${comfortText[tempLvl!]}`}>
                                        <Thermometer size={25}/>
                                        <span>{currTemperature?.toFixed(2)}°C</span>
                                    </div>
                                   <div className={`flex items-center gap-2 ${comfortText[humLvl!]}`}>
                                        <Droplet size={25}/>
                                        <span>{currHumidity?.toFixed(2)} %</span>
                                    </div>
                                </>
                            ) : (
                                <p className="text-zinc-400 italic">No sensor data received</p>

                        )}
                    </div>
                    {(hasPlant && comfLevel !== null) &&
                        (<span className={`text-xl font-bold ${comfortText[comfLevel]}`}>
                            {comfLevel == "green" && "COMFORTABLE"}
                            {comfLevel == "yellow" && "WARNING"}
                            {comfLevel == "red" && "CRITICAL"}
                        </span>)
                    }
                </div>
                {/*Inner 2nd COL*/}
                { hasPlant &&
                    <div className="flex flex-col w-2/5">
                        <img src={plant!.imageUrl} alt="plant image" className="aspect-square object-cover rounded-2xl"/>
                    </div>}
            </div>
        </div>
    );
}

export default SensorTile