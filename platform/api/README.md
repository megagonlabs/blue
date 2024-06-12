# API 

Many of the blue platform is available through a REST API. 

## build

To build the API:
```
$ cd platform/api
$  ./docker_build_api.sh
```
## deploy

API is deployed as part of the overall platform.
```
$ cd platform/scripts
$ ./deploy_platform.sh
```

## run

To run it locally during development:

First, install the dependencies by running:  `pip install -r src/requirements.txt`
Then, copy build, `./build_api.sh`

Finally, you can start the server by running: `uvicorn server:app --app-dir src --port 5050 --reload`

To set environment variables, `api.env` file, and run:  `set -a; source api.env; set +a`

## documentation

Documentation is available via a web browser when deployed. Locallly it is available at [SwaggerUI](http://localhost:5050/docs)

