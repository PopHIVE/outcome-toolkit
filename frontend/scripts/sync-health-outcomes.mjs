/**
 * Copies the Outcome Toolkit bundle from PopHIVE/health-outcomes
 * (https://github.com/PopHIVE/health-outcomes/tree/main/data/bundle_outcome_toolkit, dist/*.csv.gz) into
 * public/local-data/health-outcomes/, where the app reads it at page load (see src/stores/ingestData.ts).
 *
 * The bundle holds only what the site shows: areas as bins (rank + range), precise values for the nation only.
 * Nothing else from health-outcomes is copied.
 *
 * Usage (from frontend/):
 *   node scripts/sync-health-outcomes.mjs                          # shallow-clones the repo using your git credentials
 *   node scripts/sync-health-outcomes.mjs ../../health-outcomes   # or copy from an existing local checkout
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = path.join(ROOT, "public", "local-data", "health-outcomes");
const REPO_URL = "https://github.com/PopHIVE/health-outcomes.git";
const BUNDLE = "data/bundle_outcome_toolkit/dist";
const FILES = ["alcohol.csv.gz", "opioid.csv.gz", "maternal.csv.gz", "ascvd.csv.gz"];

const git = (cwd, ...args) => execFileSync("git", args, { cwd, encoding: "utf8" }).trim();

let src = process.argv[2];
let tmp;
if (!src) {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "health-outcomes-"));
  console.log(`Cloning ${REPO_URL}`);
  execFileSync("git", ["clone", "--depth", "1", REPO_URL, tmp], { stdio: "inherit" });
  src = tmp;
}

try {
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });
  for (const file of FILES) {
    const from = path.join(src, BUNDLE, file);
    if (!fs.existsSync(from)) throw new Error(`Missing ${from}`);
    fs.copyFileSync(from, path.join(OUT, file));
    console.log(`copied ${file} (${(fs.statSync(from).size / 1e3).toFixed(0)} KB)`);
  }
  const manifest = {
    repo: "PopHIVE/health-outcomes",
    path: BUNDLE,
    commit: git(src, "rev-parse", "HEAD"),
    commit_date: git(src, "log", "-1", "--format=%cI"),
  };
  fs.writeFileSync(path.join(OUT, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
  console.log(`health-outcomes @ ${manifest.commit.slice(0, 7)} (${manifest.commit_date})`);
} finally {
  if (tmp) fs.rmSync(tmp, { recursive: true, force: true });
}
