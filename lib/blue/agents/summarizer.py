###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.agents.openai import OpenAIAgent
from blue.plan import Plan
from blue.utils import string_utils, uuid_utils

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")



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
    "tags": {"PLAN": ["PLAN"]},
    "summary_template": "",
    "queries": {}
}

############################
### OpenAIAgent.SummarizerAgent
#
class SummarizerAgent(OpenAIAgent):
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

    def issue_nl_query(self, question, name=None, worker=None, to_param_prefix="QUESTION_RESULTS_"):

        if worker == None:
            worker = self.create_worker(None)

        # progress
        worker.write_progress(progress_id=worker.sid, label='Issuing question:' + question, value=self.current_step/self.num_steps)

        # plan
        p = Plan(scope=worker.prefix)
        # set input
        p.define_input(name, value=question)
        # set plan
        p.connect_input_to_agent(from_input=name, to_agent="NL2SQL")
        p.connect_agent_to_agent(from_agent="NL2SQL", to_agent=self.name, to_agent_input=to_param_prefix + name)
        
        # submit plan
        p.submit(worker)

    def issue_sql_query(self, query, name=None, worker=None, to_param_prefix="QUERY_RESULTS_"):

        if worker == None:
            worker = self.create_worker(None)

        # progress
        worker.write_progress(progress_id=worker.sid, label='Issuing query:' + query, value=self.current_step/self.num_steps)

        # plan
        p = Plan(scope=worker.prefix)
        # set input
        p.define_input(name, value=query)
        # set plan
        p.connect_input_to_agent(from_input=name, to_agent="QUERYEXECUTOR")
        p.connect_agent_to_agent(from_agent="QUERYEXECUTOR", to_agent=self.name, to_agent_input=to_param_prefix + name)
       
        # submit plan
        p.submit(worker)

    def summarize_doc(self, properties=None, input="", worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        # progress
        worker.write_progress(progress_id=worker.sid, label='Summarizing doc...', value=self.current_step/self.num_steps)

        session_data = worker.get_all_session_data()
        
        if session_data is None:
            session_data = {}

        # create a unique id
        id = uuid_utils.create_uuid()

        summary_template = properties['template']
        summary = string_utils.safe_substitute(summary_template, **self.results,  **session_data, input=input)

        if 'rephrase' in properties and properties['rephrase']:
            # progress 
            worker.write_progress(progress_id=worker.sid, label='Rephrasing doc...', value=self.current_step/self.num_steps)
            
            #### call api to rephrase summary
            worker.write_data(self.handle_api_call([summary], properties=properties))
            worker.write_eos()

        else:
            worker.write_data(summary)
            worker.write_eos()

        # progress, done
        worker.write_progress(progress_id=worker.sid, label='Done...', value=1.0)

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
    
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

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
                            self.issue_nl_query(question, name=question_name, worker=worker)

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
                            self.issue_sql_query(query, name=query_name, worker=worker)
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
                query = input[len("QUERY_RESULTS_"):]

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
                        self.summarize_doc(properties=properties, input=input_data, worker=worker)
                else:
                    logging.info("nothing found")
        elif input.find("QUESTION_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()
                
                # get question 
                question = input[len("QUESTION_RESULTS_"):]

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
                        self.summarize_doc(properties=properties, input=input_data, worker=worker)
                else:
                    logging.info("nothing found")

