import {type SensorData} from "../utils/sensorData.ts";
import {ArrowLeft, Thermometer, Droplet, PencilLine, Wifi, WifiOff, RefreshCcw, Loader} from "lucide-react";
import {combineLevels, type ComfortState, getLevel} from "../utils/comfortLevel.ts";
import {useEffect, useMemo, useState} from "react";
import EditRpiModal from "./EditRpiModal.tsx";
import {fetchRpiHistory, updateRpi} from "../api/rpiApi.ts";
import SensorHistoryChart, {type HistorySample} from "./SensorHistoryChart.tsx";

type DetailViewProps = {
    data: SensorData;
    onBack: () => void;
    onEdit: (updated: SensorData) => void;
}

function DetailView({data, onBack, onEdit}: DetailViewProps) {
    const {
        rpiName,
        currTemperature,
        currHumidity,
    } = data;
    const [history, setHistory] = useState<HistorySample[] | null>(null);
    const [loadingHistory, setLoadingHistory] = useState(false);

    async function loadHistory() {
        try {
            setLoadingHistory(true);
            const res = await fetchRpiHistory(data.id);
            setHistory(res.measurements);
        } finally {
            setLoadingHistory(false);
        }
    }

    useEffect(() => {   //load on initial render
        loadHistory();
    }, [data.id]);

    useEffect(() => {   //if no readings try fetching every 10s
        if (history?.length === 0) {
            const t = setTimeout(loadHistory, 10_000);
            return () => clearTimeout(t);
        }
    }, [history]);


    const tempHistory = useMemo(() => {
        if (!history) return [];
        return history.map(p => ({
            timestamp: p.timestamp,
            value: p.temperature
        }));
    }, [history, data.plant]);

    const humHistory = useMemo(() => {
        if (!history) return [];
        return history.map(p => ({
            timestamp: p.timestamp,
            value: p.humidity
        }));
    }, [history, data.plant]);

    const plant = data.plant;
    const hasPlant = plant !== null;

    const hasReadings =
        typeof currTemperature === "number" &&
        typeof currHumidity === "number";

    const [isEditing, setIsEditing] = useState(data.plant === null);    //show edit modal if plant isn't set yet

    let tempLvl: ComfortState | null = null;
    let humLvl: ComfortState | null = null;
    let combinedLvl: ComfortState | null = null;

    if (hasPlant && hasReadings) {
        if (plant.temperature) {
            tempLvl = getLevel(
                currTemperature,
                plant.temperature.warning,
                plant.temperature.critical
            );
        }

        if (plant.humidity) {
            humLvl = getLevel(
                currHumidity,
                plant.humidity.warning,
                plant.humidity.critical
            );
        }

        if (tempLvl && humLvl) {
            combinedLvl = combineLevels(tempLvl, humLvl);
        }
    }

    const comfortTextColor = {
        green: "text-emerald-400",
        yellow: "text-amber-400",
        red: "text-red-500"
    };
    const comfortBgColor = {
        green: "bg-emerald-500",
        yellow: "bg-amber-500",
        red: "bg-red-500"
    };


    return (
      <div className="flex flex-col gap-8">
          <div className="flex justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                  <button onClick={onBack} className="p-2 hover:bg-emerald-800 rounded-full transition-colors">
                      <ArrowLeft size={30}/>
                  </button>
                  <div>
                      <h2 className="text-4xl font-bold">{rpiName}</h2>
                      <p className="text-emerald-400 text-xl">
                          {hasPlant ? plant.commonName : "No plant assigned"}
                      </p>
                  </div>
                  <button onClick={() => setIsEditing(true)} className="p-2 hover:bg-emerald-800 rounded-full transition-colors">
                      <PencilLine size={30}/>
                  </button>

              </div>
              <div className="bg-emerald-950 p-4 rounded-2xl border-2 border-emerald-800 flex gap-4 items-center">
                  <p className="text-sm uppercase tracking-widest text-emerald-200">
                      Connection:
                  </p>

                  {data.connectionStatus === "connected" ? (
                      <Wifi size={32} className="text-emerald-400" />
                  ) : (
                      <WifiOff size={32} className="text-red-500" />
                  )}
                </div>
          </div>

          <div className="bg-emerald-950 p-6 rounded-3xl border-2 border-emerald-800">
              <h3 className="text-emerald-200 mb-4 uppercase text-sm tracking-widest">Environment Status</h3>
              <div className="flex justify-around text-center flex-wrap">
                  {hasReadings ? (
                      <>
                          <div>
                              <Thermometer size={48} className="mx-auto mb-2" />
                              <span className={
                                  `text-6xl font-light 
                                  ${tempLvl !== "green" ? comfortTextColor[tempLvl!] : ""}
                                  `}>
                              {currTemperature}°C
                              </span>
                              {hasPlant && (
                                  plant.temperature ? (
                                      <div className="flex gap-3 text-sm mt-4">
                                        <span className={`${comfortTextColor["green"]}`}>
                                            Optimal: {plant.temperature.warning.min}°C - {plant.temperature.warning.max}°C
                                        </span>
                                        <span className={`${comfortTextColor["yellow"]}`}>
                                            Warning: {plant.temperature.critical.min}°C - {plant.temperature.critical.max}°C
                                        </span>
                                      </div>
                                  ) : (
                                      <p className="text-zinc-400 text-sm mt-4 italic">No temperature data available</p>
                                  )
                              )}
                          </div>
                          <div>
                              <Droplet size={48} className="mx-auto mb-2" />
                              <span className={`text-6xl font-light 
                                ${humLvl !== "green" ? comfortTextColor[humLvl!] : ""}
                                `}>
                              {currHumidity}%
                          </span>
                              {hasPlant && (
                                  plant.humidity ? (
                                      <div className="flex gap-3 text-sm mt-4">
                                        <span className={`${comfortTextColor["green"]}`}>
                                            Optimal: {plant.humidity.warning.min} - {plant.humidity.warning.max}%
                                        </span>
                                        <span className={`${comfortTextColor["yellow"]}`}>
                                            Warning: {plant.humidity.critical.min} - {plant.humidity.critical.max}%
                                        </span>
                                      </div>
                                  ) : (
                                      <p className="text-zinc-400 text-sm mt-4 italic">No humidity data available</p>
                                  )
                              )}
                          </div>
                      </>
                  ) : (
                      <p className="text-zinc-400 italic text-center w-full">
                          Waiting for sensor data…
                      </p>
                  )}
              </div>
              {combinedLvl &&
                  <div className={`mt-4 h-2 rounded-full overflow-hidden ${comfortBgColor[combinedLvl]}`}/>
              }
          </div>

          {/* === GRAPHS* === */}
          {history === null ? (
              <div className="flex flex-col items-center gap-4 text-zinc-400 italic">
                  <p className="text-center">
                      Loading sensor reading history...
                  </p>
                  <div className={"animate-spin"}>
                      <Loader className={"text-emerald-500"}/>
                  </div>
              </div>
          ) : history.length === 0 ? (
              <div className="flex flex-col items-center gap-4 text-zinc-400 italic">
                  <p className="text-center">
                      No sensor reading history data yet. Graphs will be shown when more data is collected.
                  </p>
              </div>
          ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="bg-emerald-950 p-6 rounded-3xl border-2 border-emerald-800">
                      <div className="flex items-center justify-between mb-4">
                          <h3 className="text-emerald-200 mb-4 uppercase text-sm tracking-widest">Temperature History</h3>
                          <button
                              onClick={loadHistory}
                              disabled={loadingHistory}
                              className="p-2 rounded-full hover:bg-emerald-800 disabled:opacity-50"
                              title="Refresh history"
                          >
                              <RefreshCcw/>
                          </button>
                      </div>

                      <SensorHistoryChart
                          data={tempHistory}
                          label="Temperature"
                          unit="°C"
                          lineColor="#fb923c"
                          warningRange={data.plant?.temperature?.warning}
                          criticalRange={data.plant?.temperature?.critical}
                      />
                  </div>
                  <div className="bg-emerald-950 p-6 rounded-3xl border-2 border-emerald-800">
                      <div className="flex items-center justify-between mb-4">
                          <h3 className="text-emerald-200 mb-4 uppercase text-sm tracking-widest">Humidity History</h3>
                          <button
                              onClick={loadHistory}
                              disabled={loadingHistory}
                              className="p-2 rounded-full hover:bg-emerald-800 disabled:opacity-50"
                              title="Refresh history"
                          >
                              <RefreshCcw/>
                          </button>
                      </div>
                      <SensorHistoryChart
                          data={humHistory}
                          label="Humidity"
                          unit="%"
                          lineColor="#38bdf8"
                          warningRange={data.plant?.humidity?.warning}
                          criticalRange={data.plant?.humidity?.critical}
                      />
                  </div>
              </div>
          )}

          {hasPlant ? (
              <div className="bg-emerald-950 p-6  rounded-3xl border-2 border-emerald-800">
                  <h3 className="text-emerald-200 mb-4 uppercase text-sm tracking-widest">Plant Info</h3>
                  <div className="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-8">
                      <img src={plant.imageUrl} className="w-full aspect-square object-cover rounded-2xl mb-4"  alt={"plant image"}/>
                      <div>
                          <h3 className="text-2xl font-bold mb-2">{plant.commonName}</h3>
                          <div className="space-y-3 text-md">
                              <p><span className="text-emerald-400">Species:</span> {plant.scientificName}</p>
                              <p>
                                  <span className="text-emerald-400">Optimal Temp:</span>{' '}
                                  {plant.temperature ?
                                      `${plant.temperature.warning.min}°C - ${plant.temperature.warning.max}°C` :
                                      <span className="text-zinc-400 italic">No data</span>
                                  }
                              </p>
                              <p>
                                  <span className="text-emerald-400">Optimal Humidity:</span>{' '}
                                  {plant.humidity ?
                                      `${plant.humidity.warning.min}% - ${plant.humidity.warning.max}%` :
                                      <span className="text-zinc-400 italic">No data</span>
                                  }
                              </p>
                          </div>
                      </div>
                  </div>
              </div>
          ) : (
              <p className="text-zinc-400 italic">
                  Assign a plant to see details and comfort ranges.
              </p>
          )}
          {isEditing && (
              <EditRpiModal
                  data={data}
                  onClose={() => setIsEditing(false)}
                  onSave={async partial => {
                      try {
                          const updated = await updateRpi(data.id, partial);
                          onEdit(updated);
                          setIsEditing(false);
                      } catch (err) {
                          console.error('Failed to save RPI:', err);
                          alert(`Failed to save: ${err instanceof Error ? err.message : 'Unknown error'}`);
                      }
                  }}
              />
          )}
      </div>
    );
}

export default DetailView;