ARG REGISTRAR=docker.io
FROM ${REGISTRAR}/postgres:15.4

# To Fix Line Endings
RUN apt-get update -y && apt-get install -y  \
    dos2unix=7.4.3-1

# Copy Startup Script
COPY initdb.sh /docker-entrypoint-initdb.d/initdb.sh

# Fix Line Endings
RUN dos2unix /docker-entrypoint-initdb.d/initdb.sh

# Ensure not running as root user
USER postgres

# Default Health Checks
# WARNING: If you update this section make sure to update the task definition template. 
# AWS does not use health checks defined in the image definition and so health checks need to be redifiened in the task definiton as well
# PAIRED FILE: 'deployments/outcome-toolkit-all-task-definition-template.json'
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --retries=5 \
    CMD pg_isready -d ${POSTGRES_DB} -U ${POSTGRES_USER}

# Intented Ports
EXPOSE 5432

# Default CMD