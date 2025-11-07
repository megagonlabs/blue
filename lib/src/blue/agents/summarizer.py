###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.agents.openai import OpenAIAgent
from blue.agents.plan import AgenticPlan
from blue.utils import string_utils, uuid_utils


GENERATE_PROMPT = """
fill in template with query results in the template below, return only the summary as natural language text, rephrasing the template contents:
${input}
"""

agent_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": GENERATE_PROMPT,
    "openai.temperature": 0,
    "openai.max_tokens": 512,
    "nl2q.case_insensitive": True,
    "rephrase": True,
    "summary_template": "",
    "queries": {},
}


############################
### OpenAIAgent.SummarizerAgent
#
class SummarizerAgent(OpenAIAgent):
    """An agent that summarizes input text using OpenAI's language models, incorporating results from natural language and SQL queries.
    
    Properties (in addition to OpenAIAgent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `template`      | `str`                | `""`      | The template string used to generate the summary, which can include placeholders for query results. |
    | `questions`     | `dict`               | `{}`      | A dictionary of natural language questions to be asked as part of the summarization process. |
    | `queries`       | `dict`               | `{}`      | A dictionary of SQL queries to be executed as part of the summarization process. |
    | `rephrase`      | `bool`               | `True`    | Whether to rephrase the generated summary for improved readability. |

    Inputs:
    - `DEFAULT`: The main input stream where the agent receives text to summarize.

    Outputs:
    - `DEFAULT`: The output stream where the summary text is sent, tagged as SUMMARY.
    """

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "SUMMARIZER"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _initialize_properties(self):
        super()._initialize_properties()

        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the summarizer agent. No inputs by default."""
        return

    def _initialize_outputs(self):
        """Initialize outputs for the summarizer agent, tagged as SUMMARY."""
        self.add_output("DEFAULT", description="summary text incorporating query results", tags=["SUMMARY"])

    def issue_nl_query(self, question, progress_id=None, name=None, worker=None, to_param_prefix="QUESTION_RESULTS_"):
        """Issue a natural language question to the NL2SQL agent as part of the summarization process.

        Parameters:
            question: The natural language question to ask.
            progress_id: An optional progress identifier for tracking.
            name: An optional name for the question.
            worker: The worker handling the processing.
            to_param_prefix: The prefix for the output parameter name.

        Returns:
            None
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
        """Issue a SQL query to the QueryExecutor agent as part of the summarization process.

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

    def summarize_doc(self, progress_id=None, properties=None, input="", worker=None):
        """Summarize the input document using the configured template and query results.

        Parameters:
            progress_id: An optional progress identifier for tracking.
            properties: Additional properties for processing.
            input: The input text to summarize.
            worker: The worker handling the processing.
        """
        if worker == None:
            worker = self.create_worker(None)

        if progress_id is None:
            progress_id = worker.sid

        if properties is None:
            properties = self.properties

        # progress
        worker.write_progress(progress_id=progress_id, label='Summarizing doc...', value=self.current_step / self.num_steps)

        session_data = worker.get_all_session_data()

        if session_data is None:
            session_data = {}

        # create a unique id
        id = uuid_utils.create_uuid()

        summary_template = properties['template']
        summary = string_utils.safe_substitute(summary_template, **self.results, **session_data, input=input)

        if 'rephrase' in properties and properties['rephrase']:
            # progress
            worker.write_progress(progress_id=progress_id, label='Rephrasing doc...', value=self.current_step / self.num_steps)

            session_data = self.session.get_all_data()

            #### call api to rephrase summary
            worker.write_data(self.execute_api_call(summary, properties=properties, additional_data=session_data))
            worker.write_eos()

        else:
            worker.write_data(summary)
            worker.write_eos()

        # progress, done
        worker.write_progress(progress_id=progress_id, label='Done...', value=1.0)

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the summarizer agent, incorporating results from natural language and SQL queries to generate a summary.

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
                worker.set_data("input", input_data)

                if worker:
                    session_data = worker.get_all_session_data()

                    if session_data is None:
                        session_data = {}

                    # user initiated summarizer, kick off queries from template
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
                        for query_name in queries:
                            q = queries[query_name]
                            if type(q) == dict:
                                q = json.dumps(q)
                            else:
                                q = str(q)
                            query = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(query_name)
                            self.issue_sql_query(query, name=query_name, worker=worker, progress_id=self.progress_id)
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

                    self.todos.remove(query)
                    self.results[query] = query_results

                    # all queries received
                    if len(self.todos) == 0:
                        input_data = worker.get_data("input")
                        if input_data is None:
                            input_data = ""
                        self.summarize_doc(properties=properties, input=input_data, worker=worker, progress_id=self.progress_id)
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

                    self.todos.remove(question)
                    self.results[question] = question_results

                    # all questions received
                    if len(self.todos) == 0:
                        input_data = worker.get_data("input")
                        if input_data is None:
                            input_data = ""
                        self.summarize_doc(properties=properties, input=input_data, worker=worker, progress_id=self.progress_id)
                else:
                    self.logger.info("nothing found")
