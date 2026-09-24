import type { ColorRamp, MetricBin } from "@/types";

const nToC = (n: number): number => Math.floor(128 + 127 * Math.sin(n));

/** Generate an arbitrary (but reproducible) color given a string.
 * Skips everything after the first maxLen characters, for speed reasons.
 */
export function strHashColor(inputString: string, maxLen = 32) {
  let sum = 0;

  for (let i = 0; i < Math.min(inputString.length, maxLen); i++) {
    sum += inputString.charCodeAt(i) * (i / 2);
  }

  const r = nToC(sum);
  const g = nToC(sum + 2);
  const b = nToC(sum + 3);
  return `rgb(${r}, ${g}, ${b})`;
}
/** Generate an arbitrary (but reproducible) color given a string.
 * Skips everything after the first maxLen characters, for speed reasons.
 */
export function strPastelColor(inputString: string, s = 60, l = 90, maxLen = 32) {
  let sum = 0;

  for (let i = 0; i < Math.min(inputString.length, maxLen); i++) {
    sum += inputString.charCodeAt(i) * (i / 2);
  }

  const h = nToC(sum);
  return `hsl(${h}, ${s}%, ${l}%)`;
}

// HACK: Backend returns -1 for missing data.
export const MISSING_INDEX = -1;
/** Color used for missing data. */
export const MISSING_COLOR = "#FFCC00B0";

export const MISSING_BIN: MetricBin = {
  max: NaN,
  mean: NaN,
  median: NaN,
  midpoint: NaN,
  min: NaN,
  rank_value: "No Data",
  rank: MISSING_INDEX,
  representative: NaN,
};

/** Colors used for selected area.
 * NOTE: Specified as color codes because they sometimes end up in a canvas, which doesn't understand CSS variables. */
export const SELECTED_COLOR = "#0957be"; // Brand blue-dark
export const SELECTED_COLOR_PALE = "#7090d0"; // Brand blue-dark mixed with white
export const SELECTED_COLOR_FILL = "#0957beb0"; // Brand blue-dark, but transparent
export const SELECTED_INDEX = -2;
export const SELECTED_BIN: MetricBin = {
  ...MISSING_BIN,
  rank: SELECTED_INDEX,
  rank_value: "Selected",
};

export const NATIONAL_COLOR = "#959ba3"; // cool gray 50
export const NATIONAL_COLOR_PALE = "#bac2aa"; // cool gray 40
export const NATIONAL_COLOR_FILL = "#959ba3b0"; // cool gray 50, but transparent

export const PROJECT_IGNORED_COLOR = "#d7dee8b0"; // cool gray 20, but translucent

/** Two-sided color scale used for "bad-neutral-good" data. */
export const cyanToPink10: ColorRamp = {
  [SELECTED_INDEX]: SELECTED_COLOR,
  [MISSING_INDEX]: MISSING_COLOR,
  0: "#29E1CBB0",
  1: "#29FFCBB0",
  2: "#50F1CAB0",
  3: "#78E3C9B0",
  4: "#A0D5C8B0",
  5: "#C8B8BAB0",
  6: "#BBA0ACB0",
  7: "#AE7890B0",
  8: "#A15074B0",
  9: "#942859B0",
};

/** One-sided color scale used for "neutral-good" data. */
export const grayToCyan: ColorRamp = {
  [SELECTED_INDEX]: SELECTED_COLOR,
  [MISSING_INDEX]: MISSING_COLOR,
  0: "#959BA3B0",
  1: "#89A2A7B0",
  2: "#7DAAABB0",
  3: "#71B2B0B0",
  4: "#65BAB4B0",
  5: "#59C1B9B0",
  6: "#4DC9BDB0",
  7: "#41D1C2B0",
  8: "#35D9C6B0",
  9: "#29E1CBB0",
};

/** Used for the DiD. */
export const redToBlue21: ColorRamp = {
  0: "#0957BEB0",
  1: "#145BB7B0",
  2: "#205FB1B0",
  3: "#2C63ABB0",
  4: "#3867A5B0",
  5: "#446B9FB0",
  6: "#506F98B0",
  7: "#5C7392B0",
  8: "#68778CB0",
  9: "#747B86B0",
  10: "#808080B0",
  11: "#82777CB0",
  12: "#846E78B0",
  13: "#866574B0",
  14: "#885C70B0",
  15: "#8A546CB0",
  16: "#8C4B68B0",
  17: "#8E4264B0",
  18: "#903960B0",
  19: "#92305CB0",
  20: "#942859B0",
};
