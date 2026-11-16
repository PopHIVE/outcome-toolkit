# Outcome Toolkit

Outcome Toolkit is a program to guide investment into important national health outcomes. It aggregates high-level health
information on specific outcomes, coupled with demographics from US Census data.

- [Getting Started](#getting-started)
  - [Install dependencies](#install-dependencies)
  - [Get the repository](#get-the-repository)
  - [Setup your local .env.secrets file](#setup-your-local-envsecrets-file)
  - [Download the Data Bundle (one-time setup)](#download-the-data-bundle-one-time-setup)
  - [Build your Own Data Bundle (optional)](#build-your-own-data-bundle-optional)
  - [Run the system](#run-the-system)
  - [Local Automated Testing](#local-automated-testing)
  - [CI/CD](#cicd)
  - [Deployment](#deployment)
  - [Load Testing](#load-testing)
- [General Links + Resources](#general-links--resources)

## Static site (GitHub Pages)

The frontend can run without the backend. By default it loads monthly outcome data from the
[`bundle_outcome_toolkit`](https://github.com/PopHIVE/health-outcomes/tree/main/data/bundle_outcome_toolkit) in
PopHIVE/health-outcomes and geography from `frontend/public/local-data/` (built by
`node frontend/scripts/build-geography.mjs`). Pushing to `main` builds and deploys it with
`.github/workflows/deploy-pages.yml`.

The bundle holds only what the site shows: each county / ZCTA3 as its monthly and six-month-average bin (rank,
range, label), and precise values for the nation only. Bins are computed in the bundle's `build.R`. Its files are
copied into `frontend/public/local-data/health-outcomes/`, with a `manifest.json` recording the source commit. To
pick up new data, run this from `frontend/` with git access to health-outcomes, then commit and push:

```bash
node scripts/sync-health-outcomes.mjs            # or: node scripts/sync-health-outcomes.mjs <path to a local checkout>
```

To preview locally: `cd frontend && npm ci && npm run dev`. Set `VITE_DATA_SOURCE=api` to use the original backend
instead. Login-only features (projects, invites) and payout targets require the backend.

## Getting Started

### Install dependencies

- Docker
- Python 3.11

### Get the repository

```bash
git clone https://github.com/PopHIVE/health_indicator_dash_archive.git
```

### Setup your local .env.secrets file

Local secrets/credentials are not used in production, but to avoid checking any secrets/credentials into production
secrets/credentials should not be placed in the `.env` and instead in a local `.env.secrets` file. To setup your local
`.env.secrets` file:

```bash
# 1. Copy the template
$ cp .env.secrets.template .env.secrets

# 2. Generate passwords for each of the missing variables in .env.secrets file
#   Would recommend using python's secrets module.
#   Run the following command for each unassigned variable in your new .env.secrets file.
#   Use a text editor to set each unassigned variable to one of the generated strings.
$ python3 -c 'import secrets; print(secrets.token_hex()[:20])'
```

Note that if you do not do this step docker compose will not start and give an error: `.env.secrets not found`.

### Download the Data Bundle (one-time setup)

Since the data is moderately large, we don't push it to git. Instead, contact the team for the location of the latest
data bundle, and place the zip file in the `backend/bundles` directory.

For more information on each data bundle see: [Data Changelog](DATA-CHANGELOG.md).

### Build your Own Data Bundle (optional)

If you would like to build your own data bundle:

```bash
# For Backend Dev
cd backend

# Build Docker Container
docker build -f Dockerfile.make . -t outcome-toolkit-etl

# Run Make Commands (puts data in backend/build directory)
docker run -v .:/data outcome-toolkit-etl all

# Zip into a bundle
docker run -v .:/data outcome-toolkit-etl zip
```

You should now see a bunch of files in the `backend/build/` directory.

```bash
ls -l build/*.csv
```

Once you build a bundle and compress everything into a .zip file, please also copy the compiled bundle into the CI VM
with the following command, filling in the appropriate variables accordingly:

```bash
scp <path to data bundle> <username>@outcome-toolkit-test:/data/bundles/
```

The final command should look something like:

```bash
scp backend/bundles/data_bundle_v0.14.0.zip <username>@outcome-toolkit-test:/data/bundles/
```

### Run the system

The first time you run the system, you will need to rebuild the database first. This can take a minute or so. run the
`start.sh` script from the project's root directory. If you encounter build errors, it may be due to an old docker
version. It is recommended you use docker version 27.1 and above.

```bash
./start.sh -d yes
```

To start the containers without rebuilding the database, leave off the `-d` (or specify `-d no`):

```bash
./start.sh
```

To start the containers in hot-reload mode for development, specify the `dev` profile:

```bash
./start.sh -p dev
```

Other options for `start.sh` can be found by running it with `-h`.

> WINDOWS NOTE
>
> The above commands work on Mac, Linux, and gitbash (or Windows/Linux sub-system) but not Powershell. To use these
> commands, install a WSL Linux (Ubuntu 20.04 works) distribution and run the commands from within that terminal. If
> you're running Docker Desktop, you may need to manually allow WSL integration in the Docker Desktop settings.

### Local Automated Testing

To run automated testing against the database, use the `-n` flag. This can occasionally cause docker to time out. The
following example includes shows the recommended setup for running automated testing in a CI/CD pipeline:

```bash
./start.sh -n -p prod -d yes
```

To just run the tests without launching the application you can run the following script.

```bash
docker exec backend_container python3 -m pytest tests/ -vv
```

> WINDOWS NOTE
>
> The above command works on Mac, Linux, and gitbash (or Windows/Linux sub-system) but not Powershell. If
> you are using Powershell you can edit the `.env` file with entries like `RUN_TESTS=yes`, `REBUILD_DB=yes`, and
> `COMPOSE_PROFILES=dev`.

### CI/CD

CI/CD is not yet configured for this repository. Jobs must succeed to be merged into main once it is set up.

### Deployment

To push a new image to AWS ECR you must commit all changes since the Commit tag will be used as the docker image tag.

```{bash}
bash push.sh
```

The script will build the images locally, then push to ECR. It will also create a task definition under the `outcome-toolkit-all`
family and push the revision.

To then update the service run:

```{bash}
bash deploy.sh
```

Note that this will update the service but it may change the IP address of the ECS service. So you may need to manually
check to make sure the load balancer is pointing to the correct IP.

### Load Testing

TBD

## General Links + Resources

Census Resources:

- <https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html>
- <https://www.census.gov/programs-surveys/geography/technical-documentation/records-layout/2020-zcta-record-layout.html>
- <https://api.census.gov/data/2020/dec/dp/variables.html>
- <https://api.census.gov/data/2020/dec/dp.html>
