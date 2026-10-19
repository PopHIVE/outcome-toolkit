/**
 * Builds the static geography files that replace the backend's census-derived routes
 * (/api/{STATE,COUNTY,ZCTA3}/geometries, /api/state/tree, /api/v2/demographics).
 *
 * Outcome data itself is NOT built here -- it is read live from the PopHIVE Ingest parquet files
 * at page load (see src/stores/ingestData.ts). This only needs re-running if geography changes.
 *
 * Usage (from frontend/):  node scripts/build-geography.mjs
 *
 * Sources (downloaded to .geo-cache/, then reused):
 *   - States + counties: us-atlas 3.0.1 (Census cartographic boundaries, 1:10m)
 *   - ZCTA3 shapes: chris-prener/zcta3 (2020 ZCTA5s dissolved to 3 digits)
 *   - ZCTA5 -> county relationship: Census 2020 relationship file
 *   - Population: the denominators in the Ingest parquet files (county: NEMSIS alcohol/opioid,
 *     ZCTA3: HealthVerity maternal); state = sum of its counties
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import mapshaper from "mapshaper";
import * as topojson from "topojson-client";
import { parquetReadObjects } from "hyparquet";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CACHE = path.join(ROOT, ".geo-cache");
const OUT = path.join(ROOT, "public", "local-data");

const SOURCES = {
  usAtlas: "https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/counties-10m.json",
  zcta3: "https://raw.githubusercontent.com/chris-prener/zcta3/main/data/zcta3_2020.geojson",
  zctaCounty:
    "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt",
  ingest: "https://raw.githubusercontent.com/PopHIVE/Ingest/main/data/bundle_health_outcomes/dist",
};

const STATE_ABBR = {
  "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
  "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
  "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
  "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
  "54": "WV", "55": "WI", "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR", "78": "VI",
};

async function cached(name, url) {
  const file = path.join(CACHE, name);
  if (!fs.existsSync(file)) {
    console.log(`Downloading ${url}`);
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} fetching ${url}`);
    fs.writeFileSync(file, Buffer.from(await res.arrayBuffer()));
  }
  return fs.readFileSync(file, "utf8");
}

/** Read { geography: population } from an Ingest parquet file. */
async function ingestPop(file, popCol, geoType) {
  const res = await fetch(`${SOURCES.ingest}/${file}`);
  if (!res.ok) throw new Error(`${res.status} fetching ${file}`);
  const rows = await parquetReadObjects({ file: await res.arrayBuffer(), columns: ["geography", "geography_type", popCol] });
  const out = {};
  for (const r of rows) if (r.geography_type === geoType && r[popCol] != null) out[r.geography] = Number(r[popCol]);
  return out;
}

function compact(n) {
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(2)}K`;
  return String(n);
}

/** Round coordinates to keep the GeoJSON small (~10m precision is plenty for this map). */
function roundGeometry(g, digits = 3) {
  const f = 10 ** digits;
  const r = (c) => (typeof c[0] === "number" ? c.map((x) => Math.round(x * f) / f) : c.map(r));
  return { ...g, coordinates: r(g.coordinates) };
}

function featureCollection(features) {
  return {
    type: "FeatureCollection",
    features: features.map((f) => ({
      type: "Feature",
      properties: f.properties,
      geometry: roundGeometry(f.geometry),
    })),
  };
}

async function main() {
  fs.mkdirSync(CACHE, { recursive: true });
  fs.mkdirSync(OUT, { recursive: true });

  const usAtlas = JSON.parse(await cached("counties-10m.json", SOURCES.usAtlas));
  const zcta3Raw = await cached("zcta3_2020.geojson", SOURCES.zcta3);
  const zctaCountyTxt = await cached("zcta_county.txt", SOURCES.zctaCounty);
  const popCounty = {
    ...(await ingestPop("opioid.parquet", "opioid_population", "county")),
    ...(await ingestPop("alcohol.parquet", "alcohol_population", "county")),
  };
  const popState = {};
  for (const [fips, pop] of Object.entries(popCounty)) popState[fips.slice(0, 2)] = (popState[fips.slice(0, 2)] ?? 0) + pop;
  const z3Pop = await ingestPop("maternal.parquet", "maternal_population", "zcta3");

  /** @type {Record<string, any>} MID -> demographics-route record */
  const areas = {};
  const area = (mid) =>
    (areas[mid] ??= { adjacency: [], intersections: { COUNTRY: [], STATE: [], COUNTY: [], ZCTA3: [] } });

  // ---- States and counties (us-atlas) ----
  const stateNames = {};
  const stateGeoms = usAtlas.objects.states.geometries;
  const stateFeatures = topojson.feature(usAtlas, usAtlas.objects.states).features;
  stateFeatures.forEach((f) => {
    stateNames[f.id] = f.properties.name;
    f.properties = { mid: `STATE ${f.id}` };
  });

  const countyGeoms = usAtlas.objects.counties.geometries;
  const countyFeatures = topojson.feature(usAtlas, usAtlas.objects.counties).features;
  const countyNeighbors = topojson.neighbors(countyGeoms);
  countyFeatures.forEach((f, i) => {
    const fips = f.id;
    const st = fips.slice(0, 2);
    const mid = `COUNTY ${fips}`;
    const a = area(mid);
    a["census.name"] = `${f.properties.name} County, ${STATE_ABBR[st] ?? st}`;
    a["census.total_population"] = popCounty[fips] ?? 0;
    a.adjacency = countyNeighbors[i].map((j) => `COUNTY ${countyGeoms[j].id}`);
    a.intersections.STATE = [`STATE ${st}`];
    area(`STATE ${st}`).intersections.COUNTY.push(mid);
    f.properties = { mid };
  });
  const stateNeighbors = topojson.neighbors(stateGeoms);
  stateGeoms.forEach((g, i) => {
    const a = area(`STATE ${g.id}`);
    a["census.name"] = stateNames[g.id];
    a["census.total_population"] = popState[g.id] ?? 0;
    a.adjacency = stateNeighbors[i].map((j) => `STATE ${stateGeoms[j].id}`);
  });

  // ---- ZCTA3 shapes: simplify, keep shared arcs so we can compute adjacency ----
  // Source is NAD83 lon/lat, which is close enough to WGS84 for display.
  const idField = "ZCTA3";
  // The source has thousands of tiny slivers/islands that defeat simplification, so drop those first.
  const ms = await mapshaper.applyCommands(
    `-i in.json -clean -filter-slivers min-area=5km2 sliver-control=0 -simplify 2% keep-shapes ` +
      `-filter-fields ${idField} -o out.json format=topojson`,
    { "in.json": zcta3Raw }
  );
  const zTopo = JSON.parse(ms["out.json"]);
  const zObj = Object.values(zTopo.objects)[0];
  const zNeighbors = topojson.neighbors(zObj.geometries);
  const zFeatures = topojson.feature(zTopo, zObj).features;
  const zIds = zObj.geometries.map((g) => String(g.properties[idField]).padStart(3, "0"));

  // A few ZCTA3s (single buildings, PO boxes) are entirely smaller than the sliver threshold;
  // re-add them with only light simplification so they still appear on the map.
  const lost = zIds.filter((_, i) => !zFeatures[i].geometry);
  if (lost.length) {
    const small = await mapshaper.applyCommands(
      `-i in.json -filter '${JSON.stringify(lost)}.includes(${idField})' -simplify 10% keep-shapes ` +
        `-o out.json format=geojson`,
      { "in.json": zcta3Raw }
    );
    const byId = Object.fromEntries(
      JSON.parse(small["out.json"]).features.map((f) => [f.properties[idField], f.geometry])
    );
    zFeatures.forEach((f, i) => (f.geometry ??= byId[zIds[i]]));
    console.log(`Restored small ZCTA3s: ${lost.join(", ")}`);
  }

  // ZCTA5 -> county relationship, aggregated to ZCTA3 (by land area of overlap)
  const z3County = {}; // zcta3 -> county -> land area
  const lines = zctaCountyTxt.trim().split(/\r?\n/);
  const hdr = lines[0].replace(/^﻿/, "").split("|");
  const iZ = hdr.indexOf("GEOID_ZCTA5_20");
  const iC = hdr.indexOf("GEOID_COUNTY_20");
  const iA = hdr.indexOf("AREALAND_PART");
  for (const line of lines.slice(1)) {
    const c = line.split("|");
    if (!c[iZ] || !c[iC]) continue;
    const z3 = c[iZ].slice(0, 3);
    (z3County[z3] ??= {})[c[iC]] = (z3County[z3]?.[c[iC]] ?? 0) + +c[iA];
  }

  zFeatures.forEach((f, i) => {
    const z3 = zIds[i];
    const mid = `ZCTA3 ${z3}`;
    const a = area(mid);
    a["census.total_population"] = z3Pop[z3] ?? 0;
    a.adjacency = zNeighbors[i].map((j) => `ZCTA3 ${zIds[j]}`);
    const counties = Object.entries(z3County[z3] ?? {})
      .filter(([, land]) => land > 0)
      .sort((x, y) => y[1] - x[1])
      .map(([fips]) => fips);
    a.intersections.COUNTY = counties.map((fips) => `COUNTY ${fips}`);
    a.intersections.STATE = [...new Set(counties.map((fips) => `STATE ${fips.slice(0, 2)}`))];
    for (const c of a.intersections.COUNTY) area(c).intersections.ZCTA3.push(mid);
    for (const s of a.intersections.STATE) area(s).intersections.ZCTA3.push(mid);
    a["census.name"] = `ZCTA3 ${z3}xx`;
    f.properties = { mid };
  });

  // ---- Country ----
  const usa = area("COUNTRY 840");
  usa["census.name"] = "United States";
  usa["census.total_population"] = Object.values(popState).reduce((s, n) => s + n, 0);

  // ---- Area tree: STATE -> { area MID: label } ----
  const tree = {};
  const sortedStates = Object.keys(stateNames).sort((a, b) => stateNames[a].localeCompare(stateNames[b]));
  for (const st of sortedStates) tree[`STATE ${st}`] = {};
  for (const [mid, a] of Object.entries(areas)) {
    if (mid.startsWith("COUNTY")) {
      tree[a.intersections.STATE[0]] ??= {};
      tree[a.intersections.STATE[0]][mid] = `${a["census.name"]} (Pop: ${compact(a["census.total_population"])})`;
    } else if (mid.startsWith("ZCTA3")) {
      // File each ZCTA3 under the state holding most of its land, with counties grouped by state.
      const byState = {};
      for (const c of a.intersections.COUNTY) {
        const st = c.slice(7, 9);
        (byState[st] ??= []).push(areas[c]?.["census.name"]?.replace(/, \w\w$/, "") ?? c);
      }
      const desc = Object.entries(byState)
        .map(([st, names]) => {
          const shown = names.slice(0, 4).join(", ");
          const more = names.length > 4 ? `, and ${names.length - 4} more` : "";
          return `${shown}${more} (${STATE_ABBR[st] ?? st})`;
        })
        .join("; ");
      const primary = a.intersections.STATE[0];
      if (!primary) continue;
      tree[primary] ??= {};
      tree[primary][mid] =
        `${a["census.name"]}: ${desc} (Pop: ${compact(a["census.total_population"])})`;
    }
  }
  for (const k of Object.keys(tree)) if (!Object.keys(tree[k]).length) delete tree[k];

  const write = (name, obj) => {
    fs.writeFileSync(path.join(OUT, name), JSON.stringify(obj));
    console.log(`wrote ${name} (${(fs.statSync(path.join(OUT, name)).size / 1e6).toFixed(2)} MB)`);
  };
  write("geometries-STATE.json", featureCollection(stateFeatures));
  write("geometries-COUNTY.json", featureCollection(countyFeatures));
  write("geometries-ZCTA3.json", featureCollection(zFeatures));
  write("tree.json", tree);
  write("areas.json", areas);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
