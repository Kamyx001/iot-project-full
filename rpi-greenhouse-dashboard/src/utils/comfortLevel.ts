export type Range = {
    min: number;
    max: number;
};

export type ComfortState = "green" | "yellow" | "red";

function isOutsideRange(value: number, range: Range) {
    return value > range.max || value < range.min;
}

export function getLevel (val: number, warn: Range, crit: Range): ComfortState {
    if (isOutsideRange(val, crit)) return "red";
    if (isOutsideRange(val, warn)) return "yellow";
    return "green";
}

export function combineLevels(a: ComfortState, b: ComfortState): ComfortState {
    if (a === "red" || b === "red") return "red";
    if (a === "yellow" || b === "yellow") return "yellow";
    return "green";
}