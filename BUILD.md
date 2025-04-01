# building from repo

## git cloning

It is recommended that you fork from the blue repo: `https://github.com/megagonlabs/blue` and clone your forked repository.

## configuration

Most of blue scripts require configuration of environment variables. Below is the list of environment varibles and brief descriptions:

- `BLUE_AGENT_REGISTRY` - agent registry name (e.g. `default`)
- `BLUE_AGENT_REGISTRY_MODEL` - agent registry model path (e.g. `/blue_data/models/paraphrase-MiniLM-L6-v2`)
- `BLUE_BUILD_PLATFORM` - list of platforms to build for (e.g. `linux/arm64/v8,linux/arm64,linux/arm/v7,linux/amd64,linux/amd64/v2,linux/amd64/v3,linux/amd64/v4,linux/386`)
- `BLUE_CORE_DOCKER_ORG` - docker org to push/pull core blue components (e.g. `megagonlabs`)
- `BLUE_DATA_DIR` - directory hosting data for blue, location for docker volume (e.g. `~/.blue/data`)
- `BLUE_DATA_REGISTRY` - data registry name (e.g. `default`)
- `BLUE_DATA_REGISTRY_MODEL` - data registry model path (e.g. `/blue_data/models/paraphrase-MiniLM-L6-v2`)
- `BLUE_DEPLOY_DEVELOPMENT` - set development mode, False or True (e.g. `True`)
- `BLUE_DEPLOY_PLATFORM` - platform name (e.g. `default`)
- `BLUE_DEPLOY_SECURE` - use HTTP vs HTTPS, False or True (e.g. `False``)
- `BLUE_DEPLOY_TARGET` - deployment target, `localhost` or `swarm`(e.g. localhost)
- `BLUE_DEPLOY_VERSION` - deployment version, `v0.9` or `latest`  (e.g. `v0.9`)
- `BLUE_DEV_DOCKER_ORG` - docker org to push/pull blue agents and services, your own org or `megagonlabs` (e.g. `megagonlabs`)
- `BLUE_EMAIL_DOMAIN_WHITE_LIST` - allow domain list for web app authentication (e.g. `megagon.ai`)
- `BLUE_INSTALL_DIR` - directory containing blue source code (e.g. `~/blue`)
- `BLUE_PRIVATE_API_SERVER_PORT` - private port for the API server (e.g. 5050)
- `BLUE_PRIVATE_DB_SERVER_PORT` - private port for the DB server (e.g. 6379)
- `BLUE_PRIVATE_WEB_SERVER_PORT` - private port for the web application server (e.g. 3000)
- `BLUE_PUBLIC_API_SERVER` - server address for the API (e.g. localhost)
- `BLUE_PUBLIC_API_SERVER_PORT` - public port for the API server  (e.g. 5050)
- `BLUE_PUBLIC_DB_SERVER` - server address for the DB  (e.g. localhost)
- `BLUE_PUBLIC_DB_SERVER_PORT` - public port for the DB server (e.g. 6379)
- `BLUE_PUBLIC_WEB_SERVER` - server address for the web application (e.g. localhost)
- `BLUE_PUBLIC_WEB_SERVER_PORT` -  public port for the web application server (e.g. 3000)
- `BLUE_RBAC_CONFIG_FOLDER` - folder path to the role-based access control configurations (e.g. /blue_data/config/rbac)
- `BLUE_BUILD_LIB_ARG`, specific index-url settings for blue lib, for public set to empty, for private set to `--extra-index-url <private_pypi_server> --trusted-host <private_pypy_server_ip>`
- `BLUE_BUILD_CACHE_ARG`, cache option, set to empty or `--no-cache`
- `BLUE_BUILD_IMG_SUFFIX`, additional image suffix, set to empty or `-private`

A default value for these environment variable is in `localhost.envrc`. You can update them for your own configuration and simply set them by `source localhost.envrc`. Alternatively you can use utilities such as [direnv](https://direnv.net/) is  to help management environment variables and save your configuration as `.envrc`

#### setup

Refer to [Local Installation](LOCAL-INSTALLATION) for software and hardware requirements. Make sure you have `docker` already setup on your development environment.

##### builders

If you plan to use multi-platform builds (as specified in `BLUE_BUILD_PLATFORM`). It is recommended that you create a multi-platform builder in your environment. Please refer to [docker buildx](https://docs.docker.com/reference/cli/docker/buildx/) for more details. 

Below is a quick builder setup:
```
$ docker buildx create --name multi_platform_builder --platform $BLUE_BUILD_PLATFORM
$ docker buildx use multi_platform_builder
$ docker buildx ls
```

If occasionally you run into disk space problems you can clean up your builder, and check disk usage:
```
$ docker buildx prune
$ docker buildx du
```

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
$ cd $BLUE_INSTALL_DIR/platform/setup
$ ./build_setup.sh
$ cd $BLUE_INSTALL_DIR/platform/scripts
# ./setup_data_volume.sh
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
