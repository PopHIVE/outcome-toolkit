ARG REGISTRAR=docker.io
FROM ${REGISTRAR}/node:22.3

RUN useradd -r frontenduser

USER root

# Setup workspace
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . ./

RUN npm run build

RUN chown -R frontenduser /app
USER frontenduser

# WARNING: If you update this section make sure to update the task definition template. 
# AWS does not use health checks defined in the image definition and so health checks need to be redifiened in the task definiton as well
# PAIRED FILE: 'deployments/outcome-toolkit-all-task-definition-template.json'
HEALTHCHECK \
    --interval=10s \
    --timeout=10s \
    --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${FRONTEND_PORT}/ || exit 1


CMD npm run serve