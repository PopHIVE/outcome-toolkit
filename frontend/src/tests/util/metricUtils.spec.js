import { beforeEach, describe, it, expect } from "vitest";

import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import { areasSingleCounty, areasTwoCounties } from "./areas.d.js";
import { areaMetricAverage } from "@/util/metricUtils";

import { setActivePinia, createPinia } from "pinia";

/**
 * Tests for the areaMetricAverage function in the metricUtils file
 */
describe("Testing areaMetricAverage function from metricUtils", () => {
  beforeEach(() => {
    // creates a fresh pinia and makes it active
    // so it's automatically picked up by any useStore() call
    // without having to pass it to it: `useStore(pinia)`
    setActivePinia(createPinia());
  });
  /**
   * Test for the areaMetricAverage function for when returning undefined
   */
  it("Averages area metrics returns undefined", () => {
    const outcome = OUTCOME_DATA.opioid;
    const areas = [];
    expect(areaMetricAverage(outcome, areas)).bin_rank.toBeNull();
    expect(areaMetricAverage(outcome, areas)).value.toBeNull();
  });

  /**
   * Test for the areaMetricAverage function for when returning the average
   * area metrics value for a single county
   */
  it("Averages area metrics for a single county", () => {
    const outcome = OUTCOME_DATA.opioid;
    const areas = areasSingleCounty;
    expect(areaMetricAverage(outcome, areas)).bin_rank.not.toBeNull();
    expect(areaMetricAverage(outcome, areas)).value.not.toBeNull();
  });

  /**
   * Test for the areaMetricAverage function for when returning the average
   * area metrics value for multiple counties
   */
  it("Averages area metrics for multiple counties", () => {
    const outcome = OUTCOME_DATA.opioid;
    const areas = areasTwoCounties;
    expect(areaMetricAverage(outcome, areas)).bin_rank.not.toBeNull();
    expect(areaMetricAverage(outcome, areas)).value.not.toBeNull();
  });
});
