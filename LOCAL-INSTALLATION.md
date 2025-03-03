# installation

Blue can be deployed in two modes: (1) `localhost` (2) `swarm` mode. `localhost` is more suitable for development and `swarm` mode is more suitable for staging and production deployment. Below, we describe how you can install blue in `localhost` mode and further down we will talk about `swarm` mode when we discuss production mode of deployment.

## requirements
Blue requires docker engine to build and run the infrastructure and agents. To develop on your local machine you would need to install docker engine from 
https://docs.docker.com/engine/install/

## configuration

Most of blue scripts require a number of parameters. While you can use the defaults, configuring your setup can be more easy, if you set environment variables for your choices. Below is the list of environment varibles:

- `BLUE_CORE_DOCKER_ORG`, docker org to push/pull core blue components, often, `megagonlabs`
- `BLUE_DEV_DOCKER_ORG`, docker org to push/pull blue agents and services, your own org or `megagonlabs`
- `BLUE_INSTALL_DIR`, directory containing blue source code, for example, `/Users/me/blue`
- `BLUE_DEPLOY_TARGET`, deployment target, `localhost` (default) or `swarm`
- `BLUE_DEPLOY_PLATFORM`, platform name, `default` (default)
- `BLUE_DEPLOY_VERSION`, deployment version, `latest` (default)
- `BLUE_DEPLOY_SECURE`, use HTTP vs HTTPS, False or True. Set to False for local deployment
- `BLUE_DEPLOY_DEVELOPMENT`, set development mode, False or True
- `BLUE_PUBLIC_API_SERVER`, server address for the API, for example, `localhost`
- `BLUE_PUBLIC_API_SERVER_PORT`, port number for API server, for example, `5050`
- `BLUE_PUBLIC_API_SERVER_PORT_MAPPED`, port number of API server to expose, for example, `5050`
- `BLUE_PUBLIC_WEB_SERVER`, server address for the WEB, for example, `localhost`
- `BLUE_PUBLIC_WEB_SERVER_PORT`, port number for WEB server, for example, `3000`
- `BLUE_PUBLIC_WEB_SERVER_PORT_MAPPED`, port number of WEB server to expose, for example, `3000`
- `BLUE_PUBLIC_DB_SERVER`, server address for the DB (redis), for example, `localhost`
- `BLUE_PUBLIC_DB_SERVER_PORT`, port number for DB server, for example, `6379`
- `BLUE_PUBLIC_DB_SERVER_PORT_MAPPED`, port number of DB server to expose, for example, `6379`
- `BLUE_DATA_DIR`, directory hosting daa for blue services, for example `${BLUE_INSTALL_DIR}/data`
- `BLUE_AGENT_REGISTRY`, agent registry name, `default` (default)
- `BLUE_DATA_REGISTRY`, data registry name, `default` (default)
- `BLUE_AGENT_REGISTRY_MODEL`, file path to the model file 
- `BLUE_RBAC_CONFIG_FOLDER`, folder path to the role-based access control configurations

Use of utilities such as [direnv](https://direnv.net/) is strongly encouraged to help management environment variables.

## setup

### data volume setup


A data volume is added to several services (agents, API, etc.) where common data such as models can be stored within a platform (e.g. `default`). To create a data volume on your development environment, run:

```
$ cd platform/scripts
$ ./create_data_volume.sh --platform default
```
This will create a directory called `default` under the `$BLUE_DATA_DIR` directory, and create a volume on that directory.

#### data volume contents

In the default configuration some of the components of blue require data and models, stored in the data volume. Below are the steps to put them into the volume you just created:

```
$ brew install git-lfs
$ git lfs install
$ cd $BLUE_DATA_DIR/$BLUE_DEPLOY_PLATFORM
$ mkdir models
$ cd models
$ git clone https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2
$ cd $BLUE_INSTALL_DIR
$ cp -r platform/api/src/casbin $BLUE_DATA_DIR/$BLUE_DEPLOY_PLATFORM
```
Then set the environment variables to point to the correct location
```
$ export BLUE_AGENT_REGISTRY_MODEL="/blue_data/models/paraphrase-MiniLM-L6-v2"
$ export BLUE_RBAC_CONFIG_FOLDER="/blue_data/casbin"
```

## build

Even when running blue locally during development, many components of blue should be run as docker containers. As such it is important to build the various docker images first.

### building agents

To build docker images for all agents, run:
```
$ cd agents
$ ./docker_build_all_agents.sh
```

Or if you can also build images for certain agents, you can do so by first changing to the directory for the agent, for example, to build user agent only:
```
$ cd agents/user
$ ./docker_build_agent.sh
```

### building services 

To build docker images for all services that agents use, run:
```
$ cd services
$ ./docker_build_all_services.sh.
```

Or if you can also build images for certain services, you can do so by first changing to the directory for the service, for example, to build openai service only:
```
$ cd services/openai
$ ./docker_build_service.sh
```


### building platform components

The key components in platform that require building are the API and the frontend.

#### building API

Run:
```
$ cd platform/api
$ ./docker_build_api.sh
```

#### building frontend

Before building the frontend you need to update `secrets/fa.token`, please contact eser@megagon.ai or rafael@megagon.ai to get the token.

Run:
```
$ cd platform/frontend
$ ./docker_build_frontend.sh
```

While not necessary to build images for agent and data regisries, if you would like to use them independently, you could build images for them as well. Simply `cd agent_registry` and `./docker_build_agent_regisry.sh` to build agent registry and `cd data_registry` and `./docker_build_data_regisry.sh` to build data registry. See more in [agent_registry](platform/agent_regisry) and [data_registry](platform/data_registry).

## deployment

To deploy blue locally, with the default options, run:
```
$ cd platform/scripts
$ ./deploy_platform.sh
```

To test your deployment you can run:
```
$ docker ps
```

and the list should contain three containers running: redis, api , and frontend

If you want to see it in action on the web, you can bring up the frontend by browsing to `http://localhost:3000` and the API documentation on `http://localhost:5050/docs#/`


</br>
</br>
