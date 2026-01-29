import {useEffect, useState} from "react";
import type {Plant} from "../utils/sensorData.ts";
import {Search, Key} from "lucide-react";
import {searchPlants, setTrefleToken, ApiKeyError} from "../api/rpiApi.ts";

type PlantSelectProps = {
    value: Plant | null;
    onChange: (p: Plant) => void;
}

function ApiKeyPrompt({ onSuccess }: { onSuccess: () => void }) {
    const [token, setToken] = useState("");
    const [error, setError] = useState("");
    const [saving, setSaving] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token.trim()) return;

        setSaving(true);
        setError("");

        const result = await setTrefleToken(token.trim());
        setSaving(false);

        if (result.error) {
            setError(result.error);
        } else {
            onSuccess();
        }
    };

    return (
        <div className="p-3 bg-zinc-800 rounded border border-zinc-700">
            <div className="flex items-center gap-2 mb-2 text-amber-400">
                <Key size={16} />
                <span className="text-sm font-medium">Trefle API Key Required</span>
            </div>
            <p className="text-xs text-zinc-400 mb-3">
                Get a free key at <a href="https://trefle.io" target="_blank" rel="noopener" className="text-emerald-400 underline">trefle.io</a>
            </p>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={token}
                    onChange={e => setToken(e.target.value)}
                    placeholder="Enter API token..."
                    className="w-full p-2 mb-2 bg-zinc-900 rounded text-sm focus:outline-emerald-500 focus:outline"
                />
                {error && <p className="text-xs text-red-400 mb-2">{error}</p>}
                <button
                    type="submit"
                    disabled={saving || !token.trim()}
                    className="w-full p-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 rounded text-sm transition-colors"
                >
                    {saving ? "Validating..." : "Save Token"}
                </button>
            </form>
        </div>
    );
}

function PlantSelect({ value, onChange }: PlantSelectProps) {
    const [query, setQuery] = useState(value?.commonName ?? "");
    const [results, setResults] = useState<Plant[]>([]);
    const [loading, setLoading] = useState(false);
    const [needsApiKey, setNeedsApiKey] = useState(false);

    const doSearch = (q: string) => {
        if (!q.trim()) {
            setResults([]);
            return;
        }

        setLoading(true);
        searchPlants(q)
            .then(setResults)
            .catch(err => {
                if (err instanceof ApiKeyError) {
                    setNeedsApiKey(true);
                } else {
                    console.error("Plant search failed", err);
                }
            })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        const timer = setTimeout(() => doSearch(query), 300);
        return () => clearTimeout(timer);
    }, [query]);

    if (needsApiKey) {
        return <ApiKeyPrompt onSuccess={() => {
            setNeedsApiKey(false);
            doSearch(query);
        }} />;
    }

    return (
        <>
            <div className="relative w-full mb-2">
                <input
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder="Search plant..."
                    className="w-full p-2 pr-10 bg-zinc-900 rounded focus:outline-emerald-500 focus:outline transition-colors"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none">
                    <Search size={18} />
                </div>
            </div>


            <div className="max-h-40 px-1 pb-1 overflow-y-auto">
                {loading && (
                    <p className="text-sm text-zinc-400 p-2">Searching…</p>
                )}
                {(results.length === 0 && !loading) &&
                    <p className="text-sm text-zinc-400 p-2">No plants found</p>
                }
                {results.map(p => {
                    const isSelected = value && p.id === value.id;
                    return (
                        <button
                            key={p.id}
                            onClick={() => onChange(p)}
                            className={`block w-full text-left p-2 rounded
                                ${isSelected ?
                                    "bg-emerald-700 border border-emerald-400"
                                    : "hover:bg-emerald-800"
                                }
                            `}
                        >
                            <strong>{p.commonName}</strong>
                            <div className="text-sm text-emerald-400">
                                {p.scientificName}
                            </div>
                        </button>
                    )
                })}
            </div>
        </>
    );
}

export default PlantSelect;
