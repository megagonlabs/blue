# blue CLI

## Installation

* Install `blue` CLI using pip install with either SSH or HTTPS:

```
$ cd blue/platform/cli
$ python setup.py install
```

Note: Once blue CLI is released there will be `pip install` option.


### Profile

#### Create a blue profile

```
$ blue profile create
```

Above command will create a profile named `default`. If you would like to create a profile with a different name, you need to provide it as an option:

```
$ blue profile --profile-name me create
```

Options:
- `--AWS_PROFILE`, profile name for AWS, reference ~/.aws/credentials
- `--BLUE_INSTALL_DIR`, blue installation directory, `~/blue` (default)
- `--BLUE_DEPLOY_TARGET`, blue deployment target, `localhost` (default), `swarm`
- `--BLUE_DEPLOY_PLATFORM`, blue platform name, `default` (default)
- `--BLUE_PUBLIC_API_SERVER`, blue api server address, `localhost:5050` (default)
- `--BLUE_DATA_DIR`, directory to host blue data, `~/.blue/data` (default)


#### List all profiles
```
$ blue profile ls

  default
* me
```

Note: * next to the profile indicated selected profile.


#### Select a blue profile

You need to select a profile to use the configuration in the profile for blue commands. To do so:

```
$ blue profile --profile-name me select
```


#### Show profile configuration

```
$ blue profile show
default
AWS_PROFILE             default
BLUE_INSTALL_DIR        ~/blue
BLUE_DEPLOY_TARGET      localhost
BLUE_DEPLOY_PLATFORM    default
BLUE_PUBLIC_API_SERVER  10.0.160.75:5050
BLUE_DATA_DIR           ~/.blue/data
$ blue profile --profile-name me show
me
AWS_PROFILE             default
BLUE_INSTALL_DIR        ~/blue
BLUE_DEPLOY_TARGET      localhost
BLUE_DEPLOY_PLATFORM    default
BLUE_PUBLIC_API_SERVER  10.0.160.75:5050
BLUE_DATA_DIR           ~/.blue/data
```

Note: The currently selected profile will be used if profile_name is not provided


#### Delete a blue profile
```
$ blue profile --profile-name me delete
```

#### Update profile configurations and variables

```
$ blue profile --profile-name config AWS_PROFILE me
```

Note: The currently selected profile will be used if profile_name is not provided

### Session

#### Create a session
```
$ blue session create
Session Created:
id                name              description
SESSION:566c1b1a  SESSION:566c1b1a
```

#### List all sessions
```
$ blue session ls

Sessions:
id                name              description
SESSION:6ddc87b7  SESSION:6ddc87b7
SESSION:16162503  SESSION:16162503
...
```
\* (asterisk) denotes the "selected" session 

#### Join a session

Using the `blue session join` you can also agents join a session through the CLI. To do so:

```
$ blue session --session-id SESSION:6ddc87b7 join --REGISTRY default --AGENT User --AGENT_PROPERTIES '{"p":3}' --AGENT_INPUT 'hello world!'
```

## Help

You can use `--help` in any of the blue commands to get help. For example:
```
$ blue session join --help
Usage: blue session join [OPTIONS]

  add an agent to a session

Options:
  --AGENT_INPUT TEXT       optional input text
  --AGENT_PROPERTIES TEXT  optional properties of the agent in JSON
  --AGENT TEXT             name of the agent  [required]
  --REGISTRY TEXT          name of the agent registry
  --help                   Show this message and exit.
```

## Output formats

Many of the blue commands can produce other output formats (e.g. JSON, CSV) and support further querying so that can be used in scripting.
For example:
```
$ blue session --output json create
{
   "id": "SESSION:cd041ad9",
   "name": "SESSION:cd041ad9",
   "description": ""
}
$ blue session --output json --query '$.id' create
"SESSION:de75be9b"
$ blue session --output csv ls
,id,name,description
0,SESSION:6ddc87b7,SESSION:6ddc87b7,
1,SESSION:16162503,SESSION:16162503,
2,SESSION:40914ba6,SESSION:40914ba6,
...
```


