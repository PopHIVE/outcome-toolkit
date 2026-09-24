import { OUTCOME_DATA } from "@/stores/OUTCOME_DATA";
import { GRANULARITIES } from "@/stores/SPATIAL_GRANULARITY_DATA";
import { useDataStore } from "@/stores/data";
import { useGeometryStore } from "@/stores/geometry";
import { useNavigationStore } from "@/stores/nav";
import { useSelectionStore } from "@/stores/selection";
import {
  APITreeSpec,
  APIV2BinsTypeSpec,
  APIV2DataDetailsSpec,
  APIV2DemographicsSpec,
  APITargetPayoutsSpec,
  APIV2DetailsSpec,
  type APIV2BinsType,
  type AreaFeatureCollection,
  api2TargetPayout,
} from "@/types";
import {
  API_GEOMETRIES,
  API_TREE_URL,
  API_V2_BINS,
  API_V2_DEMOGRAPHICS,
  API_TARGET_PAYOUTS_URL,
  API_V2_DETAILS,
  COUNTRY_USA,
  API_DATA_DETAILS,
} from "@/util/Consts";
import { makeTimeBin } from "@/util/dateUtils";
import { midGranularity } from "@/util/mapUtils";
import _ from "lodash";

/** Lightweight type-checking on response. Doesn't verify that features look right, for performance reasons. */
function isGeoJSONShapeCollection(u: unknown): u is AreaFeatureCollection {
  return (
    _.isObject(u) &&
    "type" in u &&
    u.type === "FeatureCollection" &&
    "features" in u &&
    _.isArray(u.features)
  );
}

/** Helper function to make sure failed responses from the server fail before throwing
 * misleading validation errors.
 */
export function okOrThrow(res: Response): Response {
  if (!res.ok) {
    throw res.status + " " + res.statusText;
  }
  return res;
}

// TODO: get data at app load in a better way.
export function doFetches() {
  const geoStore = useGeometryStore();
  const dataStore = useDataStore();

  fetch(API_TREE_URL)
    .then(okOrThrow)
    .then((res) => res.json())
    .then(APITreeSpec.check)
    .then((data) => {
      dataStore.areasByState = _.map(data, (areas, mid) => ({
        areas,
        mid,
      }));
      return dataStore.areasByState;
    })
    .then((areasByState) => {
      // HACK - overview route not performant / not working right, fall back to using details.
      const midGroups = _.groupBy(
        areasByState.flatMap((a) => Object.keys(a.areas)),
        midGranularity
      );
      _.forEach(OUTCOME_DATA, (outcome) => {
        const postBody = {
          mids: [COUNTRY_USA, ...midGroups[outcome.spatialGranularity]],
          outcome: outcome.key,
          metrics: [outcome.metric.key, outcome.metric.keyT6mo],
          aggregate: false,
        };
        fetch(API_V2_DETAILS, {
          method: "POST",
          body: JSON.stringify(postBody),
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then(okOrThrow)
          .then((res) => res.json())
          .then(APIV2DetailsSpec.check)
          .then((data) => {
            _.merge(dataStore._overviewData, data);
            dataStore.setDataIsReady(outcome.key, true);
          })
          .catch((err) => {
            console.error("Problem fetching outcome data for outcome ", outcome.key, err);
          });
      });
    })
    .catch(() => {
      console.error("Problem fetching area list data.");
    });

  // Get target payouts
  fetch(API_TARGET_PAYOUTS_URL)
    .then(okOrThrow)
    .then((res) => res.json())
    .then(APITargetPayoutsSpec.check)
    .then((targetData) => {
      dataStore._targetPayouts = api2TargetPayout(targetData);
    })
    .catch((err) => {
      console.error("Problem fetching target payout data. Debug for details.", err);
    });

  fetch(API_V2_DEMOGRAPHICS)
    .then(okOrThrow)
    .then((res) => res.json())
    .then(APIV2DemographicsSpec.check)
    .then((demoData) => {
      dataStore.displayNames = demoData.metadata.display_names;
      dataStore.demographicsCategories = demoData.metadata.demographic_categories;
      dataStore.demographicsSource = demoData.metadata.source;
      dataStore.areaDemographics = demoData.data;
      dataStore._dataIsReady.demographics = true;
    })
    .catch(() => {
      console.error("Problem fetching demographic data. Debug for details.");
    });

  fetch(API_DATA_DETAILS, { method: "POST" })
    .then(okOrThrow)
    .then((res) => res.json())
    .then(APIV2DataDetailsSpec.check)
    .then((data) => {
      // TODO: Should this go in a different place? or keep it here in the new field
      dataStore._dataDetails = data;
    })
    .catch(() => {
      console.error("Problem fetching data details. Debug for details.");
    });

  Promise.all(
    _.map(
      OUTCOME_DATA,
      // NOTE: We return the promise! this is crucial so we can wait for the Promise.all to complete.
      (outcome) =>
        fetch(`${API_V2_BINS}?outcome=${outcome.key}`)
          .then(okOrThrow)
          .then((res) => res.json())
          .then(APIV2BinsTypeSpec.check)
          .then((binData: APIV2BinsType) => {
            const outcomeKey = outcome.key;
            const metricKey = outcome.metric.key;

            // Grab the metric bins for this outcome
            dataStore._metricBins[outcomeKey] = binData[outcomeKey];
            // Parse out the time bins for this metric
            dataStore._timeBins[metricKey] = _.map(
              _.keys(binData[outcomeKey][metricKey]),
              makeTimeBin
            );
          })
    )
  )
    .then(() => {
      useSelectionStore().chooseBestTimeBin({ metricKey: useNavigationStore().metric().key });
    })
    .catch(() => {
      console.error("Problem importing time bins.");
    });

  // Fetch granular geometry into the geo store. Schedule this last as it takes the longest to run.
  for (const key of GRANULARITIES) {
    if (key === "COUNTRY") {
      // We don't currently ship shapes for country-level information.
      continue;
    }
    fetch(API_GEOMETRIES(key))
      .then(okOrThrow)
      .then((res) => res.json())
      .then((json) => {
        if (isGeoJSONShapeCollection(json)) {
          geoStore[key] = json;
        } else {
          throw new Error("JSON response was not a GeoJSON feature collection.");
        }
      })
      .catch(() => console.error(`Couldn't load ${key} data.`));
  }
}
