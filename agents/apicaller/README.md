### apicaller agent

APIAgent is a generic Agent that is designed to be a base class for a variety of agents that essentially talk to an API. To support this it has a number of properties designed to construct a message to the API from input and other properties and parse response from the API to build the right output. Below are the properties to support this:

`input_json`: Initializes input if JSON is the input format. When set to None, input is just text. Otherwise JSON is constructed from the value of this property and input is plugged in to the right place in the input json using below properties. 

`input_context`: Defines where in the input json input is plugged in using JSONPath.

`input_context_field`: Defines the input field name where input is plugged in.

`input_field`: Defines the input field of the API call. Input is set as the value of this property, as constructued from above process for constructing input. 

`input_template`: Defines the template of the input using a template. When set to None it is assumed that input is passed on without an additionally formatting. Otherwise, `input_template` is expected to be of the following format: `.....{var1}....{input}....{var2}...` where `var1` and `var2` is substituted from the corresponding properties of the agent, and `input` is coming from the input stream. 

`output_path`: Define where in the API response to find the output using JSONPath. For example, `$.result` would point to the `result` property in the response JSON.

`output_template`: Defines the template of the output (in a similar fashion as in `input_template` using a template. When set to None it is assumed that output is returned without an additionally formatting. Otherwise, `output_template` is expected to be of the following format: `.....{var1}....{output}....{var2}...` where `var1` and `var2` is substituted from the corresponding properties of the agent, and `output` is coming from the response, extracted through `output_path`. 

APIAgent also defines two methods that can be overried to suit for a specific API.  `validate_input` is used before calling the API to make sure the input text is validated. If the function returns False, depending on the API, the API call is not made. `process_ouput` is executed over the output data (see above) to produce the final output data to be put back to the output stream from the agent.   
