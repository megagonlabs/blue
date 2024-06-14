# job search
This demo illustrates two agents chained together, first gathering more data from the user using an interactive form (user profile) and then another agent using collected data to perform a task (job search). 

More specifically, it illustrates:
* Customizing generic form agent to collect structured data for a use case (user profile)
  * Use Form Designer to design a form
* Recorder agent to extract data from JSON and triggering another agent 
* Job search agent to use extracted information to search and display results.

## Running the Demo
* Use Form Designer, and design a UI along with data schema, and create a new agent called `FORM_JOB`.
  * For UI Schema, enter:
    ```
    {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Label",
                "label": "Job Search Form",
                "props": {
                    "large": true,
                    "style": {
                        "marginBottom": 15,
                        "fontSize": "15pt"
                    }
                }
            },
            {
                "type": "Label",
                "label": "Please fill out below information about yourself.",
                "props": {
                    "large": true,
                    "style": {
                        "marginBottom": 15,
                        "fontSize": "10pt",
                        "fontStyle": "italic"
                    }
                }
            },
            {
                "type": "HorizontalLayout",
                "elements": [
                    {
                        "type": "Control",
                        "label": "Name",
                        "scope": "#/properties/name"
                    }
                ]
            },
            {
                "type": "Control",
                "label": "Current Title",
                "scope": "#/properties/current_title"
            },
            {
                "type": "Control",
                "label": "Skills",
                "scope": "#/properties/skills"
            },
            {
                "type": "Label",
                "label": " ",
                "props": {
                    "large": true,
                    "style": {
                        "marginBottom": 15,
                        "fontSize": "12pt",
                        "border-bottom": "thin solid gray"
                    }
                }
            },
            {
                "type": "Label",
                "label": "Job Information",
                "props": {
                    "large": true,
                    "style": {
                        "marginBottom": 15,
                        "fontSize": "12pt"
                    }
                }
            },
            {
                "type": "Label",
                "label": "Please fill out below information about your desired job.",
                "props": {
                    "large": true,
                    "style": {
                        "marginBottom": 15,
                        "fontSize": "10pt",
                        "fontStyle": "italic"
                    }
                }
            },
            {
                "type": "Control",
                "label": "Desired Title",
                "scope": "#/properties/desired_title"
            },
            {
                "type": "Control",
                "label": "Desired Location",
                "scope": "#/properties/desired_location"
            }
        ]
    }
    ```
  * For Data Schema, enter:
    ```
    {
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "current_title": {
                "type": "string"
            },
            "desired_title": {
                "type": "string"
            },
            "desired_location": {
                "type": "string"
            },
            "skills": {
                "type": "string"
            }
        }
    }
    ```
* Open `FORM` agent and create a duplicate, using Actions / Duplicate.
  * Rename agent as `FORM_JOB`
  * Copy above UI and data schema, as properties of the agent, `form` and `schema`, respectively.
  * Additionally, enter the below property to customize trigger text:
  ```
  "triggers": [
        "looking",
        "job"
    ]
  ```
* Deploy `FORM` agent in the `default` registery,  if it isn't already running, using the UI:
  * Browse to Agents / FORM_JOB
  * Actions / Deploy
* Similarly, create a duplicate of `Recorder` agent, with the following properties:
  ```
  "records": [
        {
            "variable": "current_title",
            "single": true,
            "query": "$.current_title"
        },
        {
            "variable": "desired_title",
            "single": true,
            "query": "$.desired_title"
        },
        {
            "variable": "skills",
            "single": true,
            "query": "$.skills"
        },
        {
            "variable": "name",
            "single": true,
            "query": "$.name"
        }
    ]
  ```
  In the above there are JSONPath statements that extract specific data from JSON document.
* Create a new session in the UI
  * Sessions / New
  * Add `FORM_JOB`, `Recorder_JOB`, and `JobSearch` as agents
* Interact in the UI:
  * In the User text area, enter `I am looking for a job` as input
  * Fill the `Job Search Form`
    
### Build 

If not built already build `Recorder`, `FORM`, and `JobSearch` agents, using:

```
$ cd agents/{agent_name}
$ ./docker_build_agent.sh
$ ./docker_publish_agent.sh
```

### Agent Registry

Agent registry should contain:
```
{
    "name": "FORM_JOB",
    "type": "agent",
    "scope": "/",
    "description": "Generic agent that displays a form associated with data of specific schema. Form is displayed when triggered and collects data from the user, by rendering a user interface. When form is submitted the data collected from the form is output as JSON data.",
    "properties": {
        "image": "blue-agent-form:latest",
        "form": {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Label",
                    "label": "Job Search Form",
                    "props": {
                        "large": true,
                        "style": {
                            "marginBottom": 15,
                            "fontSize": "15pt"
                        }
                    }
                },
                {
                    "type": "Label",
                    "label": "Please fill out below information about yourself.",
                    "props": {
                        "large": true,
                        "style": {
                            "marginBottom": 15,
                            "fontSize": "10pt",
                            "fontStyle": "italic"
                        }
                    }
                },
                {
                    "type": "HorizontalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "label": "Name",
                            "scope": "#/properties/name"
                        }
                    ]
                },
                {
                    "type": "Control",
                    "label": "Current Title",
                    "scope": "#/properties/current_title"
                },
                {
                    "type": "Control",
                    "label": "Skills",
                    "scope": "#/properties/skills"
                },
                {
                    "type": "Label",
                    "label": " ",
                    "props": {
                        "large": true,
                        "style": {
                            "marginBottom": 15,
                            "fontSize": "12pt",
                            "border-bottom": "thin solid gray"
                        }
                    }
                },
                {
                    "type": "Label",
                    "label": "Job Information",
                    "props": {
                        "large": true,
                        "style": {
                            "marginBottom": 15,
                            "fontSize": "12pt"
                        }
                    }
                },
                {
                    "type": "Label",
                    "label": "Please fill out below information about your desired job.",
                    "props": {
                        "large": true,
                        "style": {
                            "marginBottom": 15,
                            "fontSize": "10pt",
                            "fontStyle": "italic"
                        }
                    }
                },
                {
                    "type": "Control",
                    "label": "Desired Title",
                    "scope": "#/properties/desired_title"
                },
                {
                    "type": "Control",
                    "label": "Desired Location",
                    "scope": "#/properties/desired_location"
                }
            ]
        },
        "schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "current_title": {
                    "type": "string"
                },
                "desired_title": {
                    "type": "string"
                },
                "desired_location": {
                    "type": "string"
                },
                "skills": {
                    "type": "string"
                }
            }
        },
        "listens": {
            "includes": [
                "USER"
            ],
            "excludes": []
        },
        "tags": [
            "JSON"
        ],
        "triggers": [
            "looking",
            "job"
        ]
    },
    "contents": {}
},
{
    "name": "JobSearch",
    "type": "agent",
    "scope": "/",
    "description": "Search job descriptions database given keywords",
    "properties": {
        "image": "blue-agent-job_search",
        "job_search.db.user": "postgres",
        "job_search.db.host": "10.0.160.75",
        "job_search.db.pwd": "example",
    },
    "contents": {
        "keywords": {
            "name": "keywords",
            "type": "input",
            "scope": "/JobSearch",
            "description": "keywords to query and search the job description database",
            "properties": {},
            "contents": {}
        },
        "jobs": {
            "name": "jobs",
            "type": "output",
            "scope": "/JobSearch",
            "description": "list of jobs descriptions matching job search query keywords",
            "properties": {},
            "contents": {}
        }
    }
},
{
    "name": "Recorder_JOB",
    "type": "agent",
    "scope": "/",
    "description": "Scan JSON documents and find matched entities",
    "properties": {
        "records": [
            {
                "variable": "current_title",
                "single": true,
                "query": "$.current_title"
            },
            {
                "variable": "desired_title",
                "single": true,
                "query": "$.desired_title"
            },
            {
                "variable": "skills",
                "single": true,
                "query": "$.skills"
            },
            {
                "variable": "name",
                "single": true,
                "query": "$.name"
            }
        ],
        "image": "blue-agent-recorder:latest"
    },
    "contents": {}
}
```
