###### Parsers, Formats, Utils
import logging
import json


###### Blue
from blue.agent import Agent
from blue.stream import ControlCode
from blue.plan import Plan
from blue.utils import string_utils, uuid_utils


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


##### Helper functions
def build_doc_form(doc):
    doc_ui = { 
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Markdown",
                "scope": "#/properties/markdown",
                "props": {
                    "style": {}
                }
            }
        ]
    }

    doc_form = {
        "schema": {},
        "uischema": doc_ui,
        "data": { "markdown": doc }
    }

    return doc_form

#########################
### Agent.DocumenterAgent
#
class DocumenterAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "DOCUMENTER"
        super().__init__(**kwargs)


    def _initialize_properties(self):
        super()._initialize_properties()


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
    
    def hilite_doc(self, doc, properties=None, worker=None):
        if 'hilite' in properties:
            hilite = properties['hilite']

            if worker == None:
                worker = self.create_worker(None)

            if properties is None:
                properties = self.properties

            # progress
            worker.write_progress(progress_id=worker.sid, label='Highlighting document...', value=self.current_step/self.num_steps)

            session_data = worker.get_all_session_data()

            if session_data is None:
                session_data = {}

            processed_hilite = string_utils.safe_substitute(hilite, **properties,  **session_data, **self.results)

            hilite_contents = {
                "hilite": processed_hilite,
                "doc": doc
            }

            hilite_contents_json = json.dumps(hilite_contents, indent=3)

            # plan
            p = Plan(scope=worker.prefix)
            # set input
            p.define_input("doc", value=hilite_contents_json)
            # set plan
            p.connect_input_to_agent(from_input="doc", to_agent="OPENAI___HILITER")
            p.connect_agent_to_agent(from_agent="OPENAI___HILITER", to_agent=self.name, to_agent_input="DOC")
            
            # submit plan
            p.submit(worker)

    def process_doc(self, properties=None, input="", worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        # progress
        worker.write_progress(progress_id=worker.sid, label='Processing document...', value=self.current_step/self.num_steps)

        doc = self.substitute_doc(worker, self.results, properties, input)

        if 'hilite' in properties:
            self.hilite_doc(doc, properties=properties, worker=worker)
        else:
            self.render_doc(doc, properties=properties, worker=worker)

    def substitute_doc(self, worker, results, properties, input):
        session_data = worker.get_all_session_data()
        if session_data is None:
            session_data = {}

        template = properties['template']
        if type(template) is dict:
            template = json.dumps(template)

        processed_template = string_utils.safe_substitute(template, **properties,  **session_data, **results, input=input)

        return processed_template

    def render_doc(self, doc, properties=None, worker=None):
        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        doc_form = build_doc_form(doc)

        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, doc_form, output="DOC"
        )

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
                    if 'hilite' in self.properties:
                        self.num_steps = self.num_steps + 1
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
                    if 'questions' not in self.properties and 'queries' not in self.properties:
                        self.process_doc(properties=properties, input=input_data, worker=None)

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

                    self.results[query] = query_results
                    self.todos.remove(query)
                    
                    
                    # progress
                    self.current_step = len(self.results)
                    q = ""
                    if 'query' in data and data['query']:
                        q = data['query']

                    worker.write_progress(progress_id=worker.sid, label='Received query results: ' + q, value=self.current_step/self.num_steps)

                    if len(self.todos) == 0:
                        input_data = worker.get_data("input")
                        if input_data is None:
                            input_data = ""
                        self.process_doc(properties=properties, input=input_data, worker=worker)
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

                    self.results[question] = question_results
                    self.todos.remove(question)
                    
                    input_data = worker.get_data("input")
                    if input_data is None:
                        input_data = ""
                    # progress
                    self.current_step = len(self.results)
                    q = ""
                    if 'question' in data and data['question']:
                        q = data['question']

                    worker.write_progress(progress_id=worker.sid, label='Received question results: ' + q, value=self.current_step/self.num_steps)

                    if len(self.todos) == 0:
                        input_data = worker.get_data("input")
                        if input_data is None:
                            input_data = ""
                        self.process_doc(properties=properties, input=input_data, worker=worker)
                else:
                    logging.info("nothing found")
        elif input == "DOC":
            if message.isData():
                data = message.getData()

                # progress
                self.current_step = self.num_steps - 1
                worker.write_progress(progress_id=worker.sid, label='Received highlighted document...', value=self.current_step/self.num_steps)

                doc = str(data)
                self.render_doc(doc, properties=properties, worker=worker)
