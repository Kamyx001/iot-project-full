import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, ReferenceLine, ResponsiveContainer
} from 'recharts';
import { type Range } from '../utils/comfortLevel.ts';

export type HistorySample = {
    timestamp: number;
    temperature: number;
    humidity: number;
};

export type HistoryPoint = {
    timestamp: number;
    value: number;
};

type SensorHistoryChartProps = {
    data: HistoryPoint[];
    label: string;
    unit: string;
    lineColor?: string;
    warningRange?: Range;
    criticalRange?: Range;
};

function SensorHistoryChart({
                                data, label, unit, lineColor = "#1bdfa0",
                                warningRange, criticalRange
                            }: SensorHistoryChartProps) {
    return (
        <div className="h-64 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#064e3b" vertical={false} />
                    <XAxis
                        dataKey="timestamp"
                        type="number"               // Treat the timestamps as a numeric scale
                        domain={['dataMin', 'dataMax']} // Ensures the line stretches to the edges
                        stroke="#34d399"
                        fontSize={12}
                        // This is the "Magic" function
                        tickFormatter={(timeStr) => {
                            const date = new Date(timeStr);
                            return date.toLocaleTimeString([], { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
                        }}
                        dy = {10}
                    />
                    <YAxis stroke="#34d399" fontSize={12} unit={unit} dx={-5} />
                    <Tooltip
                        labelFormatter={(label) => {
                            return new Date(label).toLocaleString([], {
                                day: "2-digit",
                                month: '2-digit',
                                weekday: 'short',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                        }}
                        contentStyle={{ backgroundColor: '#022c22', border: '1px solid #065f46', borderRadius: '8px' }}
                        itemStyle={{ color: '#ecfdf5' }}
                    />

                    {/* Optimal Range Lines (Warning Thresholds) */}
                    {warningRange && (
                        <>
                            <ReferenceLine y={warningRange.max} stroke="#fbbf24" strokeDasharray="5 5" label={{ value: 'MAX', fill: '#fbbf24', fontSize: 10 }} />
                            <ReferenceLine y={warningRange.min} stroke="#fbbf24" strokeDasharray="5 5" label={{ value: 'MIN', fill: '#fbbf24', fontSize: 10 }} />
                        </>
                    )}

                    {/* Critical Range Lines */}
                    {criticalRange && (
                        <>
                            <ReferenceLine y={criticalRange.max} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'CRIT', fill: '#ef4444', fontSize: 10 }} />
                            <ReferenceLine y={criticalRange.min} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'CRIT', fill: '#ef4444', fontSize: 10 }} />
                        </>
                    )}

                    <Line
                        type="monotone"
                        dataKey="value"
                        name={label}
                        stroke={lineColor}
                        strokeWidth={3}
                        dot={false}
                        activeDot={{ r: 6, fill: "#fff" }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

export default SensorHistoryChart;