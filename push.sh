#!/bin/bash

set -e

SERVICES=("nginx" "backend" "frontend" "postgres")
GIT_COMMIT_SHA_SHORT=$(git rev-parse --short HEAD)
OUTCOME_TOOLKIT_RELEASE=$(cat version.txt)
TARGET_BUILD_PLATFORM="linux/amd64"
REGISTRAR=docker.io

DOCKER_ECR_REGISTRY=<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Do AWS Login Tokens
aws-mfa --profile outcome-toolkit
aws ecr get-login-password --region us-east-1 --profile outcome-toolkit | docker login --username AWS --password-stdin $DOCKER_ECR_REGISTRY

# Iterate over the services
if [ -z "$(git status --untracked-files=no --porcelain)" ]; then

  # Working directory clean
  for service in ${SERVICES[@]}; do

    source .env

    # Docker Tags
    TAG=${GIT_COMMIT_SHA_SHORT}

    # Build Service
    echo "Building Service: ${service}:${GIT_COMMIT_SHA_SHORT}"
    DOCKER_DEFAULT_PLATFORM=$TARGET_BUILD_PLATFORM docker build -t outcome-toolkit-${service}-prod:$TAG \
      --build-arg TAG=${TAG} \
      --build-arg DATA_BUNDLE=${DATA_BUNDLE} \
      --build-arg OUTCOME_TOOLKIT_RELEASE=${OUTCOME_TOOLKIT_RELEASE} \
      --build-arg REGISTRAR=${REGISTRAR} \
      ${service}

    # Tag Service
    docker tag outcome-toolkit-${service}-prod:$TAG ${DOCKER_ECR_REGISTRY}/outcome-toolkit-${service}:$TAG

    # Push Service
    echo "Pushing Service: ${service}:${GIT_COMMIT_SHA_SHORT}"
    docker push ${DOCKER_ECR_REGISTRY}/outcome-toolkit-${service}:$TAG

  done
else
  # Uncommitted changes
  echo "There uncommitted changes! You must commit all changes before proceeding!"
  exit 1
fi

# Generate a Task Defintion JSON Template
TASK_REVISION=$( aws ecs list-task-definitions --family-prefix outcome-toolkit-all --profile outcome-toolkit --region us-east-1 | python3 -c "import json, sys; print(int(json.load(sys.stdin)['taskDefinitionArns'][-1].split(':')[-1]) + 1)" )
TASK_REVISION_FILE=deployments/task-definitions/outcome-toolkit-all-task-definition-${TASK_REVISION}-${GIT_COMMIT_SHA_SHORT}.json
echo "Creating Task Definition {$TASK_REVISION} -> ${TASK_REVISION_FILE}"

echo "Task Definition Next Revision: $TASK_REVISION"
sed "s/DOCKER_IMAGE_TAG/$GIT_COMMIT_SHA_SHORT/" \
  deployments/outcome-toolkit-all-task-definition-template.json > $TASK_REVISION_FILE

# Create Task Definition Revision
aws ecs register-task-definition \
  --family outcome-toolkit-all \
  --cli-input-json file://$TASK_REVISION_FILE \
  --profile outcome-toolkit \
  --region us-east-1 > /dev/null