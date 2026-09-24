import { timeBinToDates } from "@/util/dateUtils";
import { DateTime } from "luxon";
import type { RawTimeBin } from "@/types";
import _ from "lodash";

/** Options for the formatters below. Note that not all formatters support all options.

   * - hideBelow (positive number): Numbers less than this X will be shown as "<X". Default: 0 (show all numbers).
   * - noAbbreviation (boolean): If false (default): '400.1k'; true: '400,100'.
   * - precision (positive int): Number of places after the decimal. Default: 1.
*/
type ValueFormatterOptions = {
  hideBelow?: number;
  noAbbreviation?: boolean;
  precision?: number;
};

/**
 * Format a number like "10.3m", "420k", "2,350", or "<1000" (if a hideBelow value is specified)
 */
export function compactNumber(n: number, options?: ValueFormatterOptions): string {
  const hideBelow = options?.hideBelow ?? 0;
  const precision = options?.precision ?? 1;
  const noAbbreviation = options?.noAbbreviation ?? false;

  const baseFormatter = Intl.NumberFormat("en-US", {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });

  if (n === 0) {
    return `${baseFormatter.format(n)}`;
  } else if (n < hideBelow) {
    return "<" + compactNumber(hideBelow, { hideBelow: -Infinity });
  } else if (noAbbreviation) {
    return baseFormatter.format(n);
  } else if (n >= 1e6) {
    return baseFormatter.format(n / 1e6) + "M";
  } else if (n >= 2e3) {
    return baseFormatter.format(n / 1e3) + "k";
  } else {
    return baseFormatter.format(n);
  }
}

export function compactPercent(
  n: number,
  options?: Omit<ValueFormatterOptions, "noAbbreviation">
): string {
  const hideBelow = options?.hideBelow ?? 0;
  const precision = options?.precision ?? 1;

  const percentFormatter = Intl.NumberFormat("en-US", {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });
  if (n === 0) {
    return `${percentFormatter.format(0)}`;
  } else if (n < hideBelow) {
    return `<${percentFormatter.format(100 * hideBelow)}%`;
  } else {
    return percentFormatter.format(100 * n) + "%";
  }
}

/** Return a string for use in a hover-tip, which includes full precision but also respects the 'hide below' constraint. */
export function compactTitle(
  n: number,
  options?: Pick<ValueFormatterOptions, "hideBelow">
): string {
  const hideBelow = options?.hideBelow ?? 0;
  const fullFormatter = Intl.NumberFormat("en-US");
  if (n === 0) {
    return `${fullFormatter.format(0)}`;
  } else if (n < hideBelow) {
    return `less than ${fullFormatter.format(hideBelow)}`;
  } else {
    return fullFormatter.format(n);
  }
}

/**
 * Format a number like "10.3m", "420k", "2,350", or "<1000" (if a hideBelow value is specified)
 * Remove any trailing 0s from the number (needs improvement to handle generic conversions).
 */
export function compactRatesNumber(
  n: number,
  options?: ValueFormatterOptions & { hideTrailingZeroes?: boolean }
): string {
  const { hideTrailingZeroes = false, ...rest } = options ?? {};

  const raw = compactNumber(n, rest);

  if (hideTrailingZeroes) {
    // If we're stripping zeroes and we can figure out the match,
    // strip any trailing zeroes after the decimal, possibly including the decimal.
    const matches = raw.match(/([\d,]+)(?:\.0+|(\.\d+?)0*)?/);
    if (matches?.length === 2) {
      return `${matches[1]}${matches[2]}`;
    }
  }
  // Otherwise, fall through.
  return raw;
}

export function dateFormatter(dtOrStr: DateTime | string): string {
  const dt = _.isString(dtOrStr) ? DateTime.fromHTTP(dtOrStr) : dtOrStr;
  return dt.toFormat("LLL yyyy"); // HACK: for now don't show day until we fix the UTC issue
}

/** Show a human-readable version of the end of a time bin, like `Nov 2025` */
export function timeBinToString(raw: RawTimeBin): string {
  return timeBinToDates(raw).map(dateFormatter)[1];
}

/** Formatter for "Difference in differences". Looks like `10.5%` or `-20.3%`. */
export function didFormatter(n: number) {
  return `${compactNumber(n, { hideBelow: -1000, precision: 3, noAbbreviation: true })}%`;
}

/** Format for payout numbers. See options inside the function for details. */
export function payoutFormatter(n: number, options?: ValueFormatterOptions): string {
  return `$${compactNumber(n, { hideBelow: 0, precision: 3, ...options })}`;
}

/** Format for tooltips, show to 4 precision numbers. Used */
export function tooltipFormatter(n: number) {
  return `${compactNumber(n, { hideBelow: -1000, precision: 4, noAbbreviation: true })}`;
}

/** Format for Payout Dashboard values. Looks like `13.43%` or `-10.23%` */
export function payoutPercentFormatter(n: number, options?: ValueFormatterOptions) {
  return compactPercent(n, { hideBelow: -1000, precision: 2, ...options });
}

/** Output a variable string like "inches" depending on the count of the first argument.
 * Defaults to just adding "s".
 * pl(5, "inch", "inches");  -> "inches"
 * pl(1, "inch", "inches");  -> "inch"
 * pl(0, "inch", "inches");  -> "inches"
 * pl(3, "space");  -> "spaces"
 */
export function pl(count: number, one: string, many = one + "s"): string {
  return count === 1 ? one : many;
}

/** Output a string like "3 inches" depending on the count of the first argument.
 * Defaults to just adding "s" to 'one' word.
 *
 * plw()
 * pl(5, "inch", "inches");  -> "5 inches"
 * pl(1, "inch", "inches");  -> "1 inch"
 * pl(0, "inch", "inches");  -> "0 inches"
 * pl(3, "space");  -> "3 spaces"
 */
export function pln(count: number, one: string, many = one + "s"): string {
  return `${count} ${pl(count, one, many)}`;
}

type SignType = 1 | 0 | -1;
type CompareKey =
  | "greaterOrLess"
  | "increaseOrDecrease"
  | "increasedOrDecreased"
  | "improvementOrWorsening"
  | "improvedByOrWorseBy";
type CompareType = Record<SignType, string>;

const COMPARE_WORDS: Record<CompareKey, CompareType> = {
  greaterOrLess: { 1: "greater than", 0: "equal to", [-1]: "less than" },
  increaseOrDecrease: { 1: "increase", 0: "no change", [-1]: "decrease" },
  increasedOrDecreased: { 1: "increased", 0: "had no change", [-1]: "decreased" },
  improvementOrWorsening: { 1: "improvement", 0: "no change", [-1]: "worsening" },
  improvedByOrWorseBy: { 1: "improved by", 0: "unchanged at", [-1]: "worse by" },
};

/**
 * Outputs the right words given the sign of the operand n:
 * ```
 * compareWords(50, "greaterOrLess") -> "greater than"
 * compareWords(0, "increasedOrDecreased") -> "had no change"
 * compareWords(-0.234, "worseOrBetter") -> "improvement"
 * compareWords(-0.234, "betterOrWorse") -> "worsening"
 * ```
 */
export function compareWords(n: number, key: CompareKey): string {
  if (key in COMPARE_WORDS) {
    return COMPARE_WORDS[key][Math.sign(n) as SignType];
  } else {
    console.error(`Couldn't find key ${key} in comparison words`);
    return "";
  }
}
