# Outcome Toolkit - Backend

### Table of Contents
 1. [Getting Started](#getting-started)
 2. [Dev Notes](#development-notes) 
 3. [Data Dictionary](#data-dictionary) 
 4. [Testing](#load-testing)
 5. [Resources](#general-links--resource) 
    
## Getting Started

### Starting the Backend

To start the services for the first time, OR if there were changes to the DB or Data Bundle
you need to run:

```{bash}
REBUILD_DB=yes docker compose -p outcome-toolkit -f docker-compose-dev.yml up --build
```

Subsequent starts to the backend service do not need the `REBUILD_DB` flag

```bash
docker compose -p outcome-toolkit -f docker-compose-dev.yml up --build
```

You can also run tests on startup but this could cause timeout errors if your docker is resource constrained.

```bash
RUN_TESTS=yes docker compose -p outcome-toolkit -f docker-compose-dev.yml up --build
```

To run tests after the service has started:

```bash
docker exec backend_container python3 -m pytest tests/ -vv
```

### Constructing Data Bundle

To build a new data bundle:

```bash
# For Backend Dev
cd backend

# Build Docker Container 
docker build -f Dockerfile.make . -t outcome-toolkit-etl

# Run Make Commands (puts data in backend/build directory)
docker run -v $(PWD):/data outcome-toolkit-etl all

# Zip into a bundle
docker run -v .:/data outcome-toolkit-etl zip
```

You should now see a bunch of files in the `backend/build/` directory.

```bash
ls -l build/*.csv
```

To have the API use this new Data Bundle you have to change update: `.env` file.

## Development Notes

There are several key directories and files when developing.

```bash
├── configs/ <- Configurations and Static Definitions
│   └── datasources.yml <- Defines the parameters ETL functions are called with.
├── db
│   ├── data_dictionary.py
│   ├── database.py <- Generates db_session for each request.
│   ├── datasets
│   │   ├── alcohol/  <- These direories contain Table Definitions
│   │   ├── ascvd/
│   │   ├── core.py  <- Contains Main Association Table that crosses datasets
│   │   ├── demographics
│   │   ├── geoms/
│   │   ├── mixins.py <- Contains some of the Common Core Fields and attributes.
│   │   ├── opioid/
│   │   ├── registry.py <- ETL Functions are regiestered here.
│   │   └── soc/
├── routes <- Any endpoint that a user hits should go in here
│   ├── api
│   │   ├── v1_refactor/ <- where the current routes are
│   │   │   ├── geometries_routes.py
│   │   │   ├── misc.py
│   │   │   └── properties_routes.py
│   │   └── v2/ <- placeholder for future routes!
│   │       └── __init__.py
│   └── docs.py
├── ext
│   ├── cache.py
│   ├── exceptions/ <- Custom Errors and Error Handling
│   └── middleware.py
├── models
│   ├── common.py <- Common Models go here
│   └── responses.py <- Responsee Formats and Validation go in here
└── utilities/ <- Misc Helper Functions
```

### SQLAlchemy Syntax

In this refactor all datasets are made avalaiable through a single object: the `Area`.

```python
>>> from app.db.database import db_session
>>> from app.db.datasets.core import Area

# Using Helper Functions
>>> areas = Area.query(geography, mids, state_usps)

# Using SQLAlchemy Syntax
>>> area = db_session.query(Area).filter(Area.mid=='ZCTA3 012')

# Access Demographic Data (area.<data_kind>.<column>)
>>> area.demographics.total_population
>>> area.income.between_10k_15k

# Access Geometries
>>> area.geoms.geometry
>>> area.adjacencies <- List of Edges
>>> area.intersections <- List of cross geography intersections 

# Access Metric Data
>>> area.alcohol.alcohol_rate_rank_value

# Note that if its a geography that doesn't have values then it will be None
```

### Parameter Validation

```python
>>> from app.models.common import MorpheusID
>>> MorpheusID(mid='ZCTA3 012') <- Validates MID
>>> MorpheusID(mid='Bad MID') <- Raises an Exception and immediately returns a standard JSON response with the message.
```

## Load Testing

To help with load testing there is a `tests/locust.py` file. See https://locust.io/ for more 
details on how to use the Locust UI.

```{bash}
# Locust Testing
$ pip3 install locust
$ bash run_load_test.sh <num_sim_users>
```

## General Links + Resource

Resources: 
 - https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html
 - https://www.census.gov/programs-surveys/geography/technical-documentation/records-layout/2020-zcta-record-layout.html
 - https://api.census.gov/data/2020/dec/dp/variables.html
 - https://api.census.gov/data/2020/dec/dp.html