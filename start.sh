#!/bin/bash
set -e

usage() {
  echo "Usage: $0 [-d <no|yes>] [-p dev|prod] [-s <string>] [-v <string>] [-t <string>] [-u] [-h]"
  echo "  -p <prod|dev> Deployment mode, setting to dev enables backend hot reloading. (default prod)"
  echo "  -d <yes|no> Rebuild the db. (default no)"
  echo "  -n          Run automated testing."
  echo "  -s <string> Deploy a specific service. (defaults to all services) "
  echo "  -t <string> Add a tag for nginx metadata. (defaults to git commit)"
  echo "  -v <string> Add a version for upper right corner. (defaults to contents of version.txt)"
  echo "  -h help"
  exit 1
}

# Defaults
REBUILD_DB="no"
DEPLOYMENT_MODE="prod"
RUN_TESTS="no"
TAG=$(git rev-parse --short HEAD)
VERSION=$(cat version.txt)
ENV=".env"
ENV_SECRETS=".env.secrets"
TARGET_BUILD_PLATFORM="linux/amd64"

while getopts d:n:p:s:t:v:h flag; do
  case "${flag}" in
  p) DEPLOYMENT_MODE=${OPTARG} ;;
  d) REBUILD_DB=${OPTARG} ;;
  n) RUN_TESTS=${OPTARG} ;;
  s) SERVICE=${OPTARG} ;;
  t) TAG=${OPTARG} ;;
  v) VERSION=${OPTARG} ;;
  h) usage ;;
  esac
done

# Backend hot reloading - reset nginx cache 
if [ "$DEPLOYMENT_MODE" == "dev" ]
then
  ( CACHE_SOURCE="cache_updater"
  printf "%-18s | Booting cache updater, deployment mode is dev\n" "$CACHE_SOURCE" 
  until docker inspect -f '{{.State.Running}}' backend_container 2>/dev/null | grep "true" >/dev/null && \
        docker inspect -f '{{.State.Running}}' nginx_container 2>/dev/null | grep "true" >/dev/null; do
        sleep 5
  done
  printf "%-18s | Both backend_container and nginx_container are up and running, cache updater is live\n" "$CACHE_SOURCE" 

  last_found=""

  # Infinite loop to monitor logs
  docker logs -f backend_container 2>&1 | while read -r line ; do
      # Check if the current line contains the search pattern
      if echo "$line" | grep -q -F "[DEBUG] 5 workers"; then
          # If the current line is different from the last found occurrence, execute the command
          if [ "$line" != "$last_found" ]; then
              last_found="$line"
              printf "%-18s | Found backend restart, purging nginx cache\n" "$CACHE_SOURCE" 
              docker exec nginx_container bash -c 'rm -rf /tmp/cache/*'
          fi
      fi
  done) & CACHE_PID=$!
fi 

# Start application
DOCKER_DEFAULT_PLATFORM=$TARGET_BUILD_PLATFORM TAG=$TAG OUTCOME_TOOLKIT_RELEASE=$VERSION REBUILD_DB=$REBUILD_DB RUN_TESTS=$RUN_TESTS docker compose -f docker-compose.yml -p outcome-toolkit-dev --env-file $ENV --env-file $ENV_SECRETS up --build $SERVICE
