import {useState} from "react";
import type {SensorData} from "../utils/sensorData.ts";
import PlantSelect from "./PlantSearch.tsx";
type EditRpiModalProps = {
    data: SensorData;
    onClose: () => void;
    onSave: (updated: Partial<SensorData>) => void;
}


function EditRpiModal({ data, onClose, onSave }: EditRpiModalProps) {
    const [name, setName] = useState(data.rpiName);
    const [plant, setPlant] = useState(data.plant);

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center">
            <div className="bg-emerald-950 p-6 rounded-2xl w-96">
                <h2 className="text-xl font-bold mb-4">Edit RPI</h2>

                <label className="block mb-2">RPI Name</label>
                <input
                    value={name}
                    onChange={e => setName(e.target.value)}
                    className="w-full p-2 mb-4 bg-zinc-900 rounded focus:outline-emerald-500 focus:outline transition-colors"
                />

                <label className="block mb-2">Plant</label>
                <PlantSelect value={plant} onChange={setPlant} />

                {!plant && (
                    <p className="text-zinc-400 text-sm mt-1">
                        No plant assigned
                    </p>
                )}

                <div className="flex justify-end gap-2 mt-6">
                    <button onClick={onClose}>Cancel</button>
                    <button
                        disabled={!name}
                        onClick={() => {
                            onSave({rpiName: name, plant})
                        }}
                        className="bg-emerald-600 disabled:bg-zinc-800 disabled:text-zinc-400 px-4 py-2 rounded-full"
                    >
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
}

export default EditRpiModal;
