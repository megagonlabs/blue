###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.stream import ControlCode
from blue.agents.plan import AgenticPlan
from blue.utils import string_utils, uuid_utils


##### Helper functions
def build_vis_form(vis):
    vis_ui = {"type": "VerticalLayout", "elements": [{"type": "Vega", "scope": "#/properties/vis"}]}

    vis_schema = {}

    vis_data = {"vis": vis}

    vis_form = {"schema": vis_schema, "uischema": vis_ui, "data": vis_data}

    return vis_form


##########################
### Agent.VisualizerAgent
#
class VisualizerAgent(Agent):
    """An agent that generates visualizations based on natural language questions and SQL queries.
    The agent can issue questions to an NL2SQL agent and queries to a QueryExecutor agent,
    and then uses the results to create visualizations using a specified template.

    Properties (in addition to Agent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `template`      | `str`                | `""`      | The template string used to generate the visualization, which can include placeholders for query results. |
    | `questions`     | `dict`               | `{}`      | A dictionary of natural language questions to be asked as part of the visualization process. |
    | `queries`       | `dict`               | `{}`      | A dictionary of SQL queries to be executed as part of the visualization process. |
    | `rephrase`      | `bool`               | `True`    | Whether to rephrase the generated visualization for improved readability. |
    | `auto_template` | `bool`               | `False`   | Whether to automatically generate visualization templates based on query results. |

    Inputs:
    - `DEFAULT`: The main input stream where the agent receives user input to trigger the visualization process.

    Outputs:
    - `DEFAULT`: The output stream where the generated visualizations are sent, tagged as VIS.
    - `VIS`: Control output stream for visualization UI interactions.
    
    """

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "VISUALIZER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the visualizer agent. By default, no inputs are defined."""
        return

    def _initialize_outputs(self):
        """Initialize outputs for the visualizer agent, tagged as VIS."""
        self.add_output("DEFAULT", description="visualization", tags=["VIS"])

    def write_to_new_stream(self, worker, content, output, id=None, tags=None, scope="worker"):
        """Write content to a new stream with a unique ID.

        Parameters:
            worker: The worker handling the processing.
            content: The content to write to the new stream.
            output: The output stream name.
            id: An optional unique identifier for the stream. If None, a new UUID is generated.
            tags: Optional tags to associate with the stream.
            scope: The scope of the stream, default is "worker".

        Returns:
            The name of the output stream where the content was written.
        """
        # create a unique id
        if id is None:
            id = uuid_utils.create_uuid()

        if worker:
            output_stream = worker.write_data(content, output=output, id=id, tags=tags, scope=scope)
            worker.write_eos(output=output, id=id, scope=scope)

        return output_stream

    def issue_nl_query(self, question, progress_id=None, name=None, worker=None, to_param_prefix="QUESTION_RESULTS_"):
        """Issue a natural language question to the NL2SQL agent as part of the visualization process.

        Parameters:
            question: The natural language question to ask.
            progress_id: An optional progress identifier for tracking.
            name: An optional name for the question.
            worker: The worker handling the processing.
            to_param_prefix: The prefix for the output parameter name.

        """
        if worker == None:
            worker = self.create_worker(None)

        if progress_id is None:
            progress_id = worker.sid

        # progress
        worker.write_progress(progress_id=progress_id, label='Issuing question:' + question, value=self.current_step / self.num_steps)

        # plan
        p = AgenticPlan(scope=worker.prefix)
        # set input
        p.define_input(name, value=question)
        # set plan
        p.connect_input_to_agent(from_input=name, to_agent="NL2SQL")
        p.connect_agent_to_agent(from_agent="NL2SQL", to_agent=self.name, to_agent_input=to_param_prefix + name)

        # submit plan
        p.submit(worker)

    def issue_sql_query(self, query, progress_id=None, name=None, worker=None, to_param_prefix="QUERY_RESULTS_"):
        """Issue a SQL query to the QueryExecutor agent as part of the visualization process.

        Parameters:
            query: The SQL query to execute.
            progress_id: An optional progress identifier for tracking.
            name: An optional name for the query.
            worker: The worker handling the processing.
            to_param_prefix: The prefix for the output parameter name.
        """
        if worker == None:
            worker = self.create_worker(None)

        if progress_id is None:
            progress_id = worker.sid

        # progress
        worker.write_progress(progress_id=progress_id, label='Issuing query:' + query, value=self.current_step / self.num_steps)

        # plan
        p = AgenticPlan(scope=worker.prefix)
        # set input
        p.define_input(name, value=query)
        # set plan
        p.connect_input_to_agent(from_input=name, to_agent="QUERYEXECUTOR")
        p.connect_agent_to_agent(from_agent="QUERYEXECUTOR", to_agent=self.name, to_agent_input=to_param_prefix + name)

        # submit plan
        p.submit(worker)

    def generate_template(self, query_results, progress_id=None, name=None, worker=None, to_param_prefix="VIS_RESULTS_"):
        """Generate a visualization template based on the query results.

        Parameters:
            query_results: The results from the query to use for generating the template.
            progress_id: An optional progress identifier for tracking.
            name: An optional name for the visualization.
            worker: The worker handling the processing.
            to_param_prefix: The prefix for the output parameter name.
        """
        if worker == None:
            worker = self.create_worker(None)

        if progress_id is None:
            progress_id = worker.sid

        # progress
        worker.write_progress(progress_id=progress_id, label='Visualizing :' + str(query_results), value=self.current_step / self.num_steps)

        # plan
        p = AgenticPlan(scope=worker.prefix)
        # set input
        p.define_input(name, value=query_results)
        # set plan
        p.connect_input_to_agent(from_input=name, to_agent="OPENAI___VISUALIZER")
        p.connect_agent_to_agent(from_agent="OPENAI___VISUALIZER", to_agent=self.name, to_agent_input=to_param_prefix + name)

        # submit plan
        p.submit(worker)

    def render_vis(self, progress_id=None, template=None, properties=None, worker=None):
        """Render the visualization using the provided template and query results.

        Parameters:
            progress_id: An optional progress identifier for tracking.
            template: An optional template for the visualization. If None, the agent's default template is used.
            properties: Additional properties for processing.
            worker: The worker handling the processing.
        """
        if worker == None:
            worker = self.create_worker(None)

        if progress_id is None:
            progress_id = worker.sid

        if properties is None:
            properties = self.properties
        # progress
        worker.write_progress(progress_id=progress_id, label='Rendering visualization...', value=self.current_step / self.num_steps)

        session_data = worker.get_all_session_data()

        if session_data is None:
            session_data = {}

        if template is None:
            template = self.properties['template']

        if type(template) is dict:
            template = json.dumps(template)

        vis_json = string_utils.safe_substitute(template, **self.properties, **self.results, **session_data)

        vis = json.loads(vis_json)
        vis_form = build_vis_form(vis)

        # write vis
        worker.write_control(ControlCode.CREATE_FORM, vis_form, output="VIS")

        # progress, done
        worker.write_progress(progress_id=progress_id, label='Done...', value=1.0)

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the visualizer agent, incorporating results from natural language and SQL queries to generate a summary.

        Parameters:
            message: The incoming message to process.
            input: The input stream name. Defaults to "DEFAULT".
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                self.progress_id = stream

                stream_data = worker.get_data(stream)
                input_data = " ".join(stream_data)

                if worker:
                    session_data = worker.get_all_session_data()

                    if session_data is None:
                        session_data = {}

                    # user initiated visualizer, kick off queries from template
                    self.results = {}
                    self.todos = set()

                    self.num_steps = 1
                    self.current_step = 0

                    if 'questions' in self.properties:
                        self.num_steps = self.num_steps + len(self.properties['questions'].keys())
                    if 'queries' in self.properties:
                        self.num_steps = self.num_steps + len(self.properties['queries'].keys())

                    # nl questions
                    if 'questions' in self.properties:
                        questions = self.properties['questions']
                        for question_name in questions:
                            q = questions[question_name]
                            question = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(question_name)
                            self.issue_nl_query(question, name=question_name, worker=worker, progress_id=self.progress_id)
                    # db queries
                    if 'queries' in self.properties:
                        queries = self.properties['queries']
                        for question_name in queries:
                            q = queries[question_name]
                            if type(q) == dict:
                                q = json.dumps(q)
                            else:
                                q = str(q)
                            query = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(question_name)
                            self.issue_sql_query(query, name=question_name, worker=worker, progress_id=self.progress_id)
                    if 'questions' not in self.properties and 'queries' not in self.properties:
                        self.render_vis(properties=properties, worker=worker, progress_id=self.progress_id)

                    return

            elif message.isBOS():
                stream = message.getStream()

                # init private stream data to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                stream = message.getStream()

                # append to private stream data
                if worker:
                    worker.append_data(stream, data)

        elif input.find("QUERY_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()

                # get query
                query = input[len("QUERY_RESULTS_") :]

                data = message.getData()

                if 'result' in data:
                    query_results = data['result']

                    self.results[query] = json.dumps(query_results)
                    self.todos.remove(query)

                    # progress
                    self.current_step = len(self.results)
                    q = ""
                    if 'query' in data and data['query']:
                        q = data['query']
                    if 'question' in data and data['question']:
                        q = data['question']

                    worker.write_progress(progress_id=self.progress_id, label='Received query results: ' + q, value=self.current_step / self.num_steps)

                    # for auto-template create a vis for each question/query
                    auto_template = False

                    if "auto_template" in properties:
                        auto_template = properties["auto_template"]

                    if auto_template:
                        self.generate_template(data, name=query, progress_id=self.progress_id)
                    else:
                        if len(self.todos) == 0:
                            if len(query_results) == 0:
                                self.write_to_new_stream(worker, "No results...", "TEXT")
                                worker.write_progress(progress_id=self.progress_id, label='Done...', value=1.0)
                            else:
                                self.render_vis(properties=properties, worker=worker, progress_id=self.progress_id)
                else:
                    self.logger.info("nothing found")
        elif input.find("QUESTION_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()

                # get question
                question = input[len("QUESTION_RESULTS_") :]

                data = message.getData()

                if 'result' in data:
                    question_results = data['result']

                    self.results[question] = json.dumps(question_results)
                    self.todos.remove(question)

                    # progress
                    self.current_step = len(self.results)
                    q = ""

                    if 'question' in data and data['question']:
                        q = data['question']

                    worker.write_progress(progress_id=self.progress_id, label='Received question results: ' + q, value=self.current_step / self.num_steps)

                    # for auto-template create a vis for each question/query
                    auto_template = False

                    if "auto_template" in properties:
                        auto_template = properties["auto_template"]

                    if auto_template:
                        self.generate_template(data, name=question, progress_id=self.progress_id)
                    else:
                        if len(self.todos) == 0:
                            if len(question_results) == 0:
                                self.write_to_new_stream(worker, "No results...", "TEXT")
                                worker.write_progress(progress_id=self.progress_id, label='Done...', value=1.0)
                            else:
                                self.render_vis(properties=properties, worker=worker)
                else:
                    self.logger.info("nothing found")

        elif input.find("VIS_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()

                # get q
                q = input[len("VIS_RESULTS_") :]

                template = message.getData()

                self.render_vis(template=template, properties=properties, worker=worker, progress_id=self.progress_id)
