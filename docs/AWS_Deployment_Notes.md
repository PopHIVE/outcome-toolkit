# AWS ECR and ECS Deployment

This assumes you have the AWS CLI installed. If you do not have them installed look at the [AWS Docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for instructions

- [0. Deployment environment](#0-deployment-environment)
- [1. Deployment Architecture](#1-deployment-architecture)
- [2. AWS CLI Setup](#2-aws-cli-setup)
- [3. Push Docker Images to Elastic Container Registry and Create Task Revision](#3-push-docker-images-to-elastic-container-registry-and-create-task-revision)
  - [Resolving Script Errors](#resolving-script-errors)
  - [Authentication](#authentication)
  - [Building and Pushing Images](#building-and-pushing-images)
  - [Creating a Task Definition](#creating-a-task-definition)
- [4. Update/Deploy an ECS Service](#4-updatedeploy-an-ecs-service)
- [5. Create an ECS Service (Optional)](#5-create-an-ecs-service-optional)
- [6. Checking Container Logging + Status](#6-checking-container-logging--status)
- [7. Updating Load Balancer IP Address](#7-updating-load-balancer-ip-address)

## 0. Deployment Environment

The ECS clusters that host deployed versions of the application (described below) are built in docker with an AMD platform. Apple machines with m-series chips have trouble building AMD (They prefer ARM). If no developers are available with a non m-series mac, a workaround is to deploy from a Linux virtual machine:

- Give an existing user sudo privileges: `sudo usermod -aG sudo <user_to_add>` (Run as a different user that already has sudo)
- Give an existing user docker privileges: `sudo usermod -aG docker $USER` (Run as the user you want to give docker privileges to)
  - For your new docker privileges to be applied you will need to reset your terminal session. If that doesn't work then reboot the vm.

## 1. Deployment Architecture

The AWS deployment architecture will consist of 3 main parts: Elastic Container Registry (ECR), Task Definitions + Cloud Formation, and Elastic Container Service (ECS).

ECR will host the images in the AWS Environment staged for deployment. Task Definitions can be configured in the AWS Console and define which versions of images in ECR to run along
with any resource parameters (CPU and memory limits). ECS is the cluster that actually runs the containers on "Fargate" machines which auto-scale.

## 2. AWS CLI Setup

Make sure you have an IAM user account created for you. If you do not, look at [Create an IAM user in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) for instructions.

If your organization requires MFA on your credentials, we recommend using the python aws-mfa tool which helps manage token configuration.

```bash
# Create a virtual Env
$ python3 -m venv env
$ source env/bin/activate

# Install package
$ pip install aws-mfa
```

Once that is installed add a `outcome-toolkit-long-term` profile. On windows the AWS Credentials and Configuration File can be found at `C:\Users\USERNAME\.aws\credentials`

If needed, make the `.aws` directory as follows:

```bash
mkdir ~/.aws
```

Then create your credentials and config files as follows:

```bash
$ vim ~/.aws/credentials
...
[outcome-toolkit-long-term]
aws_access_key_id = <your-access-key>
aws_secret_access_key = <your-secret-access-key>
aws_mfa_device = <your-mfa-arn>
region = us-east-1
```

```bash
$ vim ~/.aws/config
...
[outcome-toolkit-long-term]
region=us-east-1
```

If your organization requires a custom CA bundle for SSL, add a `ca_bundle` entry pointing to it in the config above.

Then run the **aws-mfa** tool and input your MFA Token. You will have to refresh the MFA token every 12 hours.

```bash
$ aws-mfa --profile outcome-toolkit
INFO - Validating credentials for profile: outcome-toolkit
...
```

**Note:** If you receive the below error message you may have to rename the `[default]` profile in your aws credentials file.

```log
ERROR - An error occurred while calling assume role: An error occurred (InvalidClientTokenId) when calling the GetSessionToken operation: The security token included in the request is invalid.
```

To test that it worked run the below command which should return something like:

```bash
$ aws ecr describe-repositories --profile outcome-toolkit --region us-east-1
{
    "repositories": [
        {
            "repositoryArn": "arn:aws:ecr:us-east-1:<registry-id>:repository/outcome-toolkit-container-repo",
            "registryId": "<registry-id>",
            "repositoryName": "outcome-toolkit-container-repo",
            "repositoryUri": "<registry-id>.dkr.ecr.us-east-1.amazonaws.com/outcome-toolkit-container-repo",
            "createdAt": "2023-12-20T14:27:48-05:00",
            "imageTagMutability": "MUTABLE",
            "imageScanningConfiguration": {
                "scanOnPush": false
            },
            "encryptionConfiguration": {
                "encryptionType": "AES256"
            }
        }
        ...
    ]
}
```

There should be a ECR Repository for each image in our docker compose.

**Note**: If you get SSL errors, check whether your organization requires a custom CA bundle for outbound HTTPS.

## 3. Push Docker Images to Elastic Container Registry and Create Task Revision

If your AWS MFA token is expired it will prompt you for a new token. **Note:** That this script **requires** you to have a clean git working directory. If you have uncommitted changes in a tracked file this script will exit. This is a requirement because the git tag is used as the docker image tag.

```bash
bash push.sh
...
```

### Resolving Script Errors

First, try rerunning. Our AWS ECR is set to have tag immutability so you do not need to worry about damaging existing images when re-running this script. If an error occurs (which happens inconsistently on zscalar) feel free to simply rerun the script. If a service was pushed successfully rerunning will simply skip that service with messages that say "layer already exists".

Some Errors people have encountered are resolved just by rerunning the script. I suspect these are errors where zscalar is blocking an authentication packet.

```log
denied: User: arn:aws:iam::<iam>:user/<user> is not authorized to perform: ecr:InitiateLayerUpload on resource: ... with an explicit deny in a service control policy
```

```log
error parsing HTTP 403 response body: unexpected end of JSON input: ""
```

If you encounter the following error, make sure your CA bundle (if your organization requires one) is in place and set via `export AWS_CA_BUNDLE=<path-to-bundle>`. Then rerun the `push.sh` script:

```log
SSL validation failed for https://ecs.us-east-1.amazonaws.com/ [SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)
Traceback (most recent call last):
   ...
raise JSONDecodeError("Expecting value", s, err.value) from None
```

If you encounter, the following error, this means that this image tag already exists with the ECR system. Image tags are based on the git commit hash and so in order to push again you will have to make another commit in order to change the corresponding hash.

```log
tag invalid: The image tag ' 2723b331' already exists in the 'outcome-toolkit-nginx' repository and cannot be overwritten because the repository is immutable.
```

If you need to re-push using the same commit hash, you can delete the offending tagged containers in aws with the following command:

```bash
aws ecr --profile outcome-toolkit batch-delete-image --repository-name <INSERT_NAME> --image-ids imageTag=<INSERT_TAG>
```

This script can take several minutes to run and composes three stages:

### Authentication

The script should handle authentication, which involves a general AWS CLI authentication and AWS ECR Login.

```bash
aws-mfa --profile outcome-toolkit
aws ecr get-login-password --region us-east-1 --profile outcome-toolkit | docker login --username AWS --password-stdin $DOCKER_ECR_REGISTRY
```

### Building and Pushing Images

```bash
TAG=${GIT_COMMIT_SHA_SHORT}

# Build Service
DOCKER_DEFAULT_PLATFORM=$TARGET_BUILD_PLATFORM docker build -t outcome-toolkit-${service}-prod:$TAG ${service}

# Tag it with the ECR URI
docker tag outcome-toolkit-${service}-prod:$TAG ${DOCKER_ECR_REGISTRY}/outcome-toolkit-${service}:$TAG

# Push
docker push ${DOCKER_ECR_REGISTRY}/outcome-toolkit-${service}:$TAG
```

### Creating a Task Definition

The last portion creates an ECS Task Definition. It will substitute the necessary variables i
`deployments/outcome-toolkit-all-task-definition-template.json` and create and push the revision: `deployments/task-definitions/outcome-toolkit-all-task-definition-<revision>-<git commit>.json`

```bash
# Generate a Task Definition JSON Template
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
```

## 4. Update/Deploy an ECS Service

Once the `push.sh` script completes it should print the Task Definition Number something like:

```log
Creating Task Definition <task def number> -> <file>
```

Then go to: <https://us-east-1.console.aws.amazon.com/ecs/v2/clusters?region=us-east-1> and select the cluster you want to update/deploy your changes to:

_(AWS console screenshot removed.)_

Then select the checkbox by the service name (bottom left) and click the update button (see below). Note that Task Definition column shows the current task definition this service is running.

_(AWS console screenshot removed.)_

After hitting Update you will be prompted with Deployment configurations. The only thing that needs changing is selecting the Revision drop down and selecting your desired Task Definition Number. Then scroll to the bottom and hit Update.

_(AWS console screenshot removed.)_

The existing deployment will continue running until the containers for the new task definition start and are healthy. Logs can be seen in the UI by selecting the Service > the Task > Logs tab

The UI gives an easy way to see each container's logs. Within the cluster select the service and the Logs Tab.

_(AWS console screenshot removed.)_

Each new deployment creates a new IP Address. The IP Address for the deployment can be found by selecting the running Service, then selecting the Task and the Configuration Tab.

_(AWS console screenshot removed.)_

**Note** that in ECS the service is running on port 8080 instead of 80. This is due to an SCR requirement that our containers run as non-root users and FARGATE's limitation of accessing ports <1024 for non-privileged users.

## 5. Create an ECS Service (Optional)

Go to one of the pre-created [ECS Clusters](https://us-east-1.console.aws.amazon.com/ecs/v2/clusters?region=us-east-1) and click the create button.

_(AWS console screenshot removed.)_

In the UI select the Task Definition Family and Revision to run. You must also specify a unique name.

_(AWS console screenshot removed.)_

Most importantly, in the Networking Configuration you must specify:

**VPC:** Generic VPC
**Subnets:** Your organization's public subnets
**Security Groups** default, plus your organization's baseline/web security groups

_(AWS console screenshot removed.)_

The IP Address to check the Deployment can be found by Selecting the running Service, then selecting the Task and the Configuration Tab.

_(AWS console screenshot removed.)_

## 6. Checking Container Logging + Status

The UI gives an easy way to see each container's logs. Within the cluster select the service and the Logs Tab.

_(AWS console screenshot removed.)_

## 7. Updating Load Balancer IP Address

Once you have the IP Address of the updated cluster service go to the Web UI for our [load balancer](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#LoadBalancer:loadBalancerArn=arn:aws:elasticloadbalancing:us-east-1:<AWS_ACCOUNT_ID>:loadbalancer/app/<LOAD_BALANCER_NAME>/<LOAD_BALANCER_ID>;tab=listeners). You can also navigate to it by searching for "Load Balancers" in services and selecting "<LOAD_BALANCER_NAME>".

Once on the Load Balancer page select the Load Balancer Target Group for port 80:

_(AWS console screenshot removed.)_

Once on the Target Group page select register targets.

_(AWS console screenshot removed.)_

Enter the IP Address from the deployed service and set port to 8080 and select "Include as pending below". **Note:** You do not need to modify the VPC.

_(AWS console screenshot removed.)_

You can then select "Register pending targets" and eventually you should see the "Health Status" for your newly added IP change to Healthy.

Once your IP is Healthy, you can deregister the old IP address. To verify its working you can visit the internal load balancer address (only reachable from your organization's network).

**Note:** If we wanted to scale to multiple clusters/services running you can have multiple IPs here and the Load Balancer will manage routing to the multiple services.
