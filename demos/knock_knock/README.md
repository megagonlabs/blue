# knock knock
This demo illustrates interactive agents. 

More specifically:
* Ability to listen to user stream
* Trigger an interactive agent based on user input
* Handle multiple forms without conflicts

## Running the Demo
* From the UI or command-line deploy `KNOCKKNOCK` agent in the `default` registry, if it isn't already running.
  * Using the UI:
    * Browse to Agents / KNOCKKNOCK
    * Actions / Deploy
  * Using the CLI:
    ```
    $ cd platform/scripts
    $ deploy_agent --registry default --agent KNOCKKNOCK --image blue-agent-template-interactive:latest --properties '{"db.host":"blue_db_redis"}' 
    ```
* Create a new session in the UI
  * Sessions / New
  * Add `KNOCKKNOCK` as agent
* Interact in the UI:
  * In the User text area, enter `knock knock` as input
  * In the form, enter your user name, e.g. `Maria`, and click `Done`
  * In the subsequent form, enter your last name, e.g. `Rose`, and click `Done`
  * The `KNOCKKNOCK` agent will respond with `Hello, Maria Rose`
    
### Build 

```
$ cd agents/template_interactive
$ ./docker_build_agent.sh
$ ./docker_publish_agent.sh
```

### Agent Registry

Create an entry in the agent registry, if one is not already present:
```
{
    "name": "KNOCKKNOCK",
    "type": "agent",
    "scope": "/",
    "description": "template agent to demonstrate interactive agents with UI, try it out by saying \"knock knock\"",
    "properties": {
        "image": "blue-agent-template-interactive:latest",
        "listens": {
            "includes": [
                "USER"
            ],
            "excludes": []
        }
    },
    "contents": {}
}
```
