# installation

Blue can be deployed in two modes: (1) `localhost` (2) `swarm` mode. `localhost` is more suitable for development and `swarm` mode is more suitable for staging and production deployment. Below, we describe how you can install blue in `localhost` mode. See [Swarm Deployment](SWARM-DEPLOYMENT.md) for deployment in `swarm` mode when we discuss production mode of deployment.

## requirements
Blue requires docker engine to build and run the infrastructure and agents. To develop on your local machine you would need to install docker engine from 
https://docs.docker.com/engine/install/

## downloads
Most convenient way to install and configure blue is through its CLI (`blue-cli`). In this option you would not need to build any images as they will be downloaded from docker hub. Another approach is through cloning code from this repo, building images and manually configuring. We recommend following blue-cli approach for most people.

### installation through `blue-cli`

#### install blue-cli
To download and install `blue-cli`, you can pip install it as shown below. It is highly recommended to create a virtual environment to avoid any conflicts:
```
$ pip install --no-cache --extra-index-url  http://10.0.160.75:8888/simple/ --trusted-host 10.0.160.75 blue_cli==0.9
```

`blue-cli` also installs `blue-py`, the python library for blue.

Once installed, you can invoke blue cli, for example:
```
$ blue
```

This would list the various blue commands, as shown below:
Usage: blue [OPTIONS] COMMAND [ARGS]...
```
Options:
  --help  Show this message and exit.

Commands:
  platform  command group to interact with blue platforms
  profile   command group to interact with blue profiles
  service   command group to interact with blue services
```

#### configure blue profile 

To use `blue-cli` most conveniently you need to create a blue profile, which captures profile specific configuration of the blue deployment. By default `defajult` profile is automatically created which you can see from the output of:
```
$ blue profile ls`
name
* default
```

The * next to the default profile entry indicates that it is the currently selected profile. This is a convenience as you would not need to specify `--profile_name` option with each profile command following.

To configure the selected profile:
```
$ blue profile config
```

This will ask you a number of questions with you can skip just using the default values, such as:
- `BLUE_INSTALL_DIR`, directory where blue is installed (only used for during development)
- `BLUE_DATA_DIR`, directory hosting data for blue services, will be used to create a docker volume
- `BLUE_DEV_DOCKER_ORG`, docker org to push/pull blue agents and services, your own org if you develop your own agents, or `megagonlabs` otherwise 
- `BLUE_CORE_DOCKER_ORG`, docker org to push/pull core blue components, often, `megagonlabs`

Once you configure you can see the entire profile configuration using:
```$ blue profile show
default
BLUE_INSTALL_DIR      /home/ubuntu/blue
BLUE_DATA_DIR         /home/ubuntu/blue/data
BLUE_DEV_DOCKER_ORG   megagonlabs
BLUE_CORE_DOCKER_ORG  megagonlabs
```
and later you can change any specific configuration, for example: `blue profile config BLUE_DATA_DIR /home/ubuntu/data`

#### configure blue platform

In the next step you will need to configure platform specific configuration. To do so:
```
$ blue platform config
```

As before you will most likely accept the default values for these configuration options. The `platform` commands are very similar to `profile` commands. For example, you can use `blue platform show` to list platform configuration.

#### install platform

To install platform, you can run:
```
$ blue platform install
```
This will download all docker images used in the deployment, including base agent images.

#### start platform

To start platform, you can run:
```
$ blue platform start
```

This will run the redis backend, api server, and the web application server for blue. If you type `docker ps` you should see three containers running, similar to below:
```
docker ps
CONTAINER ID   IMAGE                                       COMMAND                  CREATED        STATUS        PORTS                                                 NAMES
081a9c8e59a8   megagonlabs/blue-platform-frontend:v0.9   "docker-entrypoint.s…"   2 days ago     Up 2 days     0.0.0.0:3000->3000/tcp, :::3000->3000/tcp             frosty_knuth
2233a2c7cde9   megagonlabs/blue-platform-api:v0.9        "sh -c 'uvicorn serv…"   2 days ago     Up 2 days     0.0.0.0:5050->5050/tcp, :::5050->5050/tcp             hardcore_jemison
79c773d9060d   redis/redis-stack:latest                    "/entrypoint.sh"         2 days ago     Up 2 days     0.0.0.0:6379->6379/tcp, :::6379->6379/tcp, 8001/tcp   bold_bhaskara
```

#### start services

Optionally, at this point you can also start common blue services that some agents use, for example the `OPENAI` service. To do so:
```
$ blue service --service_name OPENAI create
```
and the configure it:
```
$ blue service  --service_name OPENAI config
```

To install (downloads service image) and start (start running service containers):
```
$ blue service  --service_name OPENAI install
$ blue service  --service_name OPENAI start
```

### installation from repo

#### configuration

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
- `BLUE_PRIVATE_API_SERVER_PORT`, port number for API server, for example, `5050`
- `BLUE_PUBLIC_API_SERVER_PORT`, port number of API server to expose, for example, `5050`
- `BLUE_PUBLIC_WEB_SERVER`, server address for the WEB, for example, `localhost`
- `BLUE_PRIVATE_WEB_SERVER_PORT`, port number for WEB server, for example, `3000`
- `BLUE_PUBLIC_WEB_SERVER_PORT`, port number of WEB server to expose, for example, `3000`
- `BLUE_PUBLIC_DB_SERVER`, server address for the DB (redis), for example, `localhost`
- `BLUE_PRIVATE_DB_SERVER_PORT`, port number for DB server, for example, `6379`
- `BLUE_PUBLIC_DB_SERVER_PORT`, port number of DB server to expose, for example, `6379`
- `BLUE_DATA_DIR`, directory hosting data for blue services, for example `${BLUE_INSTALL_DIR}/data`
- `BLUE_AGENT_REGISTRY`, agent registry name, `default` (default)
- `BLUE_DATA_REGISTRY`, data registry name, `default` (default)
- `BLUE_AGENT_REGISTRY_MODEL`, file path to the model file 
- `BLUE_RBAC_CONFIG_FOLDER`, folder path to the role-based access control configurations

Use of utilities such as [direnv](https://direnv.net/) is strongly encouraged to help management environment variables.

#### setup

##### data volume setup


A data volume is added to several services (agents, API, etc.) where common data such as models can be stored within a platform (e.g. `default`). To create a data volume on your development environment, run:

```
$ cd platform/scripts
$ ./create_data_volume.sh --platform default
```
This will create a directory called `default` under the `$BLUE_DATA_DIR` directory, and create a volume on that directory.

###### data volume contents

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

#### build

Even when running blue locally during development, many components of blue should be run as docker containers. As such it is important to build the various docker images first.

##### building agents

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

##### building services 

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


##### building platform components

The key components in platform that require building are the API and the frontend.

#### building API

Run:
```
$ cd platform/api
$ ./docker_build_api.sh
```

###### building frontend

Before building the frontend you need to update `secrets/fa.token`, please contact eser@megagon.ai or rafael@megagon.ai to get the token.

Run:
```
$ cd platform/frontend
$ ./docker_build_frontend.sh
```

While not necessary to build images for agent and data regisries, if you would like to use them independently, you could build images for them as well. Simply `cd agent_registry` and `./docker_build_agent_regisry.sh` to build agent registry and `cd data_registry` and `./docker_build_data_regisry.sh` to build data registry. See more in [agent_registry](platform/agent_regisry) and [data_registry](platform/data_registry).

#### deployment

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
