ARG REGISTRAR=docker.io
FROM ${REGISTRAR}/rocker/rstudio:latest

# Packages
RUN apt-get update -y && apt-get install -y  \
    libpq-dev

# Install R Packages
RUN R -e "install.packages('ggplot2', repos='http://repo.miserver.it.umich.edu/cran')" \
    R -e "install.packages('zoo', repos='http://repo.miserver.it.umich.edu/cran')" \
    R -e "install.packages('dplyr', repos='http://repo.miserver.it.umich.edu/cran')" \
    R -e "install.packages('gridExtra', repos='http://repo.miserver.it.umich.edu/cran')" \
    R -e "install.packages('RPostgreSQL', repos='http://repo.miserver.it.umich.edu/cran')"

COPY rstudio-prefs.json /home/rstudio/.config/rstudio/rstudio-prefs.json

HEALTHCHECK \
    --interval=10s \
    --timeout=10s \
    --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8787/ || exit 1