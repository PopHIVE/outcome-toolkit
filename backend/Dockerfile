ARG REGISTRAR=docker.io
FROM ${REGISTRAR}/python:3.11

# Args
ARG DATA_BUNDLE
ENV DATA_BUNDLE=$DATA_BUNDLE

ARG RUN_OPTION
ENV RUN_OPTION=$RUN_OPTION

# Add Non Root User
RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser

# Setup workspace
WORKDIR /app

# Updates
RUN apt-get update && apt-get install -y \
    dos2unix=7.5.2-1 \
    libgdal-dev=3.10.3+dfsg-1

# Install python requirements
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy Data Bundle and Rest of Files
COPY $DATA_BUNDLE /mnt/data/build.zip
RUN mkdir -p /data/builds && unzip -o /mnt/data/build.zip -d /data/builds

# Be explicit with Copy to avoid copying unnecessary files to externally facing service
COPY app app/
COPY db db/
COPY docs docs/
COPY tests tests/
COPY server.py .
COPY start_backend.sh .
COPY setup_db.py .
COPY setup_test_projects.py .

# Start Flask Server
RUN dos2unix ./start_backend.sh && chmod +x ./start_backend.sh

# Make sure non-root user has permissions
RUN chown -R appuser:appuser /mnt && \
    chown -R appuser:appuser /data && \
    chown -R appuser:appuser /app

USER appuser

# Default Health Checks
# WARNING: If you update this section make sure to update the task definition template. 
# AWS does not use health checks defined in the image definition and so health checks need to be redifiened in the task definiton as well
# PAIRED FILE: 'deployments/outcome-toolkit-all-task-definition-template.json'
HEALTHCHECK \
    --interval=1m \
    --timeout=5m \
    --start-period=300s \
    --retries=60 \
    CMD curl --silent --fail localhost:${BACKEND_PORT}/api/health-check || exit 1

# Intented Ports
EXPOSE 5000

# Default CMD
CMD ./start_backend.sh $RUN_OPTION

