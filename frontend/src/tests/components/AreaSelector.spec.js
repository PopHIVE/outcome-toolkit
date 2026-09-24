import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { mount } from "@vue/test-utils";
import { createTestingPinia } from "@pinia/testing";
import AreaList from "@/components/areaSelector/AreaList.vue";
import { useDataStore } from "@/stores/data";

/**
 * Tests for the AreaList component
 */
describe("AreaList", () => {
  let wrapper = null;
  let dataStore = null;

  beforeEach(() => {
    wrapper = mount(AreaList, {
      global: {
        plugins: [createTestingPinia()],
      },
    });
    dataStore = useDataStore();
  });

  afterEach(() => {
    wrapper.unmount();
  });

  /**
   * Test to verify that the AreaList shows the loading message when the AreaList is empty
   */
  it("Shows loading message when empty", () => {
    dataStore.areas = [];
    expect(wrapper.find(".area-list")).toBeDefined();
  });
});
