# blue CLI

## Installation

* Install `blue` using pip install with either SSH or HTTPS:

```
pip install git+ssh://git@github.com/rit-git/blue.git
pip install git+https://github.com/rit-git/blue.git
```

## Combluends
> Combluend options are **case-sensitive**

### Profile
#### Show profile values
```
blue profile <profile_name:optional> show

key1 value1
key2 value2
```

the currently selected profile will be used if profile_name is not provided

#### List all profiles
```
blue profile ls

  profile 1
* profile 2
```

\* (asterisk) denotes the currently selected profile

#### Select or remove a blue profile
```
blue profile <profile_name:required> select/delete
```
#### Update profile configurations and variables
```
blue profile <profile_name:optional> config key value
```
the currently selected profile will be used if profile_name is not provided
#### Create a blue profile
```
blue profile <profile_name:required> create --AWS-PROFILE <value> --FORCE
```
Options
- `--AWS-PROFILE`, value, profile name for AWS, reference ~/.aws/credentials

### Session
#### List all sessions
```
blue session ls

* session 1
  project 2
```
\* (asterisk) denotes the "selected" session 

#### Create a session
```
blue session create
```


