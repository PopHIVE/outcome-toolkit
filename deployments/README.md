# Dockerfile and Deployment Considerations Notes

**High level context:** For the purposes of local development, containers are started
on the dev's machines using docker compose (`docker-compose.yml`) for configurations.
The `docker-compose.yml` handles:
 - Build Args
 - Container runtime configurations (i.e. env variables, ports, etc.)

**AWS Deployments do not use the docker-compose.yml file** at all.   For **AWS deployments**, images are built locally on a dev's machine and pushed to AWS ECR using the `push.sh` script. Container runtime configurations are handled via the Task Definition `deployments/outcome-toolkit-all-task-definition-template.json`.

 - Build args in `push.sh`
 - Runtime configurations in `deployments/outcome-toolkit-all-task-definition-template.json`

## Specific Compose Configuration Sections Equivalents

---------------

Platform:

For AWS ECS Fargate Containers all containers **must** be `linux/amd64` or `linux/x86_64`.

---------------

Container Name:

```yml
# docker-compose.yml
...
    container_name: nginx_container
```

```json
"containerDefinitions": [
    {
        "name": "nginx",
        ...
    },
    ...
]
```

---------------

Image:

```yml
# docker-compose.yml
...
    image: ${DOCKER_REGISTRY}/outcome-toolkit-nginx:${TAG}
```

```json
"containerDefinitions": [
    {
        "image": "<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/outcome-toolkit-nginx:DOCKER_IMAGE_TAG",
        ...
    },
    ...
]
```

---------------

Environment Variables:

```yml
# docker-compose.yml
...
    environment:
        - NGINX_LISTEN_PORT=${NGINX_LISTEN_PORT}
        - BACKEND_SERVER_ADDR=${BACKEND_HOST}:${BACKEND_PORT}
        - FRONTEND_SERVER_ADDR=${FRONTEND_HOST}:${FRONTEND_PORT}
```

```json
"containerDefinitions": [
    {
        "environment": [
            {
                "name": "BACKEND_SERVER_ADDR",
                "value": "localhost:5000"
            },
            {
                "name": "FRONTEND_SERVER_ADDR",
                "value": "localhost:5001"
            },
            {
                "name": "NGINX_LISTEN_PORT",
                "value": "8080"
            }
        ],
    }
```

Note that if you want to use sensitive environment variables these should be set in AWS Secrets Manager and specified in the Task Definition like below:

```json
    {
        "name": "POSTGRES_PASSWORD",
        "value": "arn:aws:secretsmanager:us-east-1:<AWS_ACCOUNT_ID>:secret:outcome-toolkit-all/dev-78slNZ:POSTGRES_PASSWORD_DEV::"
    },
```

---------------

Ports:

Ports exposed in the AWS Task Definition will become accessible to your organization's networks and there may be firewalls that limit what ports and what protocols can be exposed.

```yml
# docker-compose.ymp
    ports:
      - "80:${NGINX_LISTEN_PORT}"
```

In the Taks Definition it would look like:

```json
    "portMappings": [
        {
            "name": "nginx-8080-http",
            "containerPort": 8080,
            "hostPort": 8080,
            "protocol": "tcp",
            "appProtocol": "http"
        }
    ]
```

---------------

Command:

```yml
# docker-compose.yml
    command: npm run dev
```

In the Task Definition the command is specified as a list like below. Note that if the command section is not present or is an empty list it will use the default `CMD` of the image. The command section (like in docker compose) **overwrites** the `CMD` instruction in the Dockerfile.

```json
    "command": [
        "/app/start.sh"
    ],
```

---------------

Volumes:

**Currently we have not utilized an equivalent in the Task Definitions**. There is a way using the `mountPoints: []` and `volumesFrom: []` sections to mount EBS storage but that is not currently utilized or needed since we do not need hot reloading in production and further do not need to persist any files between deployments.

---------------

Build Args:

```yml
# docker-compose.yml
    build:
        args:
            DATA_BUNDLE: ...
```

Build Args are not handled in the Task Definition but are instead handled in the `push.sh` script. If you add a build arg to the compose file make sure its reflected in the `push.sh` script!

```sh
# ~ Line 31
DOCKER_DEFAULT_PLATFORM=$TARGET_BUILD_PLATFORM docker build -t outcome-toolkit-${service}-prod:$TAG \
      --build-arg TAG=${TAG} \
      --build-arg DATA_BUNDLE=${DATA_BUNDLE} \
      --build-arg OUTCOME_TOOLKIT_RELEASE=${OUTCOME_TOOLKIT_RELEASE} \
      ${service}
```