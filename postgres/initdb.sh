#!/bin/bash

# Create V2 DB (Datastore)
echo "Creating Datastore Database: ${DATASTORE_DB}"
psql -c "CREATE DATABASE ${DATASTORE_DB}";

echo "Creating Datastore User: ${DATASTORE_USER}"
psql -c "CREATE USER ${DATASTORE_USER} WITH PASSWORD '${DATASTORE_PASSWORD}'";

echo "Granting Datastore Permissions: ${DATASTORE_USER} -> ${DATASTORE_DB}"
psql -c "GRANT ALL ON SCHEMA public TO ${DATASTORE_USER}" -d ${DATASTORE_DB};
psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DATASTORE_DB} TO ${DATASTORE_USER}";