import type {SensorData} from "./utils/sensorData.ts";
import {Info} from "lucide-react";
import {useEffect, useState} from "react";
import DetailView from "./components/DetailView.tsx";
import {fetchReadings, fetchRpis} from "./api/rpiApi.ts";
import SensorTile from "./components/SensorTile.tsx";

function App() {
    const [selectedRpiId, setSelectedRpiId] = useState<number | null>(null);
    const [sensors, setSensors] = useState<SensorData[]>([]);

    const selectedRpi =
        selectedRpiId !== null
            ? sensors.find(r => r.id === selectedRpiId) ?? null
            : null;

    useEffect(() => {
        // initial load
        fetchRpis()
            .then(setSensors)
            .catch(console.error);

        // polling
        const interval = setInterval(async () => {
            try {
                const readings = await fetchReadings();
                setSensors(prev =>
                    prev.map(rpi => {
                        const updated = readings.find(r => r.id === rpi.id);
                        if (!updated) return rpi;
                        // Only update sensor readings, preserve plant and rpiName
                        return {
                            ...rpi,
                            currTemperature: updated.currTemperature,
                            currHumidity: updated.currHumidity,
                            connectionStatus: updated.connectionStatus
                        };
                    })
                );
            } catch (err) {
                console.error("Failed to poll readings", err);
            }
        }, 5000); // every 5s

        return () => clearInterval(interval);
    }, []);


    //For updates in child views
    function updateRpi(updated: SensorData) {
        setSensors(prev =>
            prev.map(t => (t.id === updated.id ? updated : t))
        );
    }

    return (
    <>
      <div className="min-h-screen min-w-full bg-zinc-900 text-emerald-50 z-50">
          <nav className="h-20 p-8 flex flex-row items-center justify-between sticky top-0 bg-emerald-800 max-h-10">
              <h1 className="text-3xl font-bold">RPI Greenhouse</h1>
          </nav>
          <main className="p-8 mx-auto max-w-screen-lg">
              {selectedRpi ? (
                  <DetailView data={selectedRpi}
                              onBack={() => setSelectedRpiId(null)}
                              onEdit={updateRpi}
                  />
              ) : (
                  // GRID VIEW
                  <div className="grid sm:grid-cols-2 grid-cols-1 gap-6">
                      {sensors.length ? (
                          sensors.map(
                              data =>
                                  <SensorTile key={data.id}
                                              data={data}
                                              onClick={() => setSelectedRpiId(data.id)}
                                  />
                          )
                      ) : (
                          <div className={"flex flex-row gap-6 items-center"}>
                              <span><Info size={30}/></span>
                              <p className="text-2xl">
                                  No sensor RPIs connected. Use the button above to
                                  <span className={"font-bold text-emerald-400"}> add one</span>.
                              </p>
                          </div>
                      )}
                  </div>
              )}
          </main>
      </div>
    </>
  )
}

export default App
