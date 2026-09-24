ARG REGISTRAR=docker.io
FROM ${REGISTRAR}/python:3.11

# Add Non Root User
RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser

# Install Requirements
RUN apt-get update && apt-get install -y \
    libgdal-dev=3.10.3+dfsg-1 \
    gdal-bin=3.6.2+dfsg-1+b2 \
    python3-gdal=3.10.3+dfsg-1 \
    zip=3.0-13

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /data

# Make sure non-root user has permissions
RUN chown -R appuser:appuser /mnt && \
    chown -R appuser:appuser /data

USER appuser

ENTRYPOINT ["make"]