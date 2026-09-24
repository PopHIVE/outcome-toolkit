#!/bin/bash

ECS_CLUSTER=<ECS_CLUSTER_NAME>
ECS_SERVICE=<ECS_SERVICE_NAME>

# Do AWS Login Tokens
aws-mfa --profile outcome-toolkit
aws ecr get-login-password --region us-east-1 --profile outcome-toolkit | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Update Service
# aws ecs update-service \
#   --cluster $ECS_CLUSTER \
#   --service $ECS_SERVICE \
#   --task-definition outcome-toolkit-all \
#   --region us-east-1 \
#   --profile outcome-toolkit > /dev/null
