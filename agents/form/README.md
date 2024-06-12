# form agent

Form Agent is a generic Agent that is designed to present a form to the user to collect structured data. The form to be presented is defined as part of the agent properties along with the data to be collected.
`form` property contains the JSON specification of the form, while the `schema` defines the structure of the data. 

For example:
```
 "form": {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Control",
                "label": "First Name",
                "scope": "#/properties/name"
            }
        ]
    },
    "schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            }
        }
    }
```
will render a simple form with a single text field to collect the `name` field as defined in `schema`. 

Once the form is submitted by the user, the Form Agent will deposit a JSON data into its output stream for further processing by other agents. For example, the above properties will result in:
```
{ "name": <input> } 
```
in the output stream.

