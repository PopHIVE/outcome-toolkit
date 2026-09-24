ARG REGISTRAR=docker.io
FROM ${REGISTRAR}/python:3.11

# Args
ARG DATA_BUNDLE
ENV DATA_BUNDLE=$DATA_BUNDLE
ENV DATA_BUNDLE_DIR=/opt/dagster/app/${DATA_BUNDLE}

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p /opt/dagster/dagster_home /opt/dagster/app

# Updates
RUN apt-get update && apt-get install -y \
    dos2unix=7.5.2-1 \
    libgdal-dev=3.10.3+dfsg-1

# Copy Data Bundle
COPY ${DATA_BUNDLE} /mnt/tmp/${DATA_BUNDLE}
RUN mkdir -p ${DATA_BUNDLE_DIR} && unzip -o /mnt/tmp/${DATA_BUNDLE} -d ${DATA_BUNDLE_DIR}

# Install dependencies
COPY requirements-datastore.txt requirements.txt
RUN pip install -r requirements.txt

COPY pyproject.toml /opt/dagster/app/
COPY dagster.yaml /opt/dagster/dagster_home/
COPY datastore /opt/dagster/app/datastore
COPY db /opt/dagster/app/db/
COPY app /opt/dagster/app/app/
COPY docs /opt/dagster/app/docs/

WORKDIR /opt/dagster/app
EXPOSE 3000

# PAIRED FILE: 'deployments/outcome-toolkit-all-task-definition-template.json'
HEALTHCHECK \
    --interval=1m \
    --timeout=5m \
    --start-period=300s \
    --retries=60 \
    CMD curl --silent --fail localhost:3000 || exit 1

ENTRYPOINT ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
