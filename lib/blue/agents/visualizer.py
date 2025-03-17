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
def build_vis_form(vis):
    vis_ui = { 
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Vega",
                "scope": "#/properties/vis"
            }
        ]
    }

    vis_schema = {}

    vis_data = {
        "vis": vis
    }

    vis_form = {
        "schema": vis_schema,
        "uischema": vis_ui,
        "data": vis_data
    }

    return vis_form

##########################
### Agent.VisualizerAgent
#
class VisualizerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "VISUALIZER"
        super().__init__(**kwargs)


    def _initialize_properties(self):
        super()._initialize_properties()

    def write_to_new_stream(self, worker, content, output, id=None, tags=None, scope="worker"):
        
        # create a unique id
        if id is None:
            id = uuid_utils.create_uuid()

        if worker:
            output_stream = worker.write_data(
                content, output=output, id=id, tags=tags, scope=scope
            )
            worker.write_eos(output=output, id=id, scope=scope)

        return output_stream
    
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

    
    def render_vis(self, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties
        # progress
        worker.write_progress(progress_id=worker.sid, label='Rendering visualization...', value=self.current_step/self.num_steps)

        session_data = worker.get_all_session_data()

        if session_data is None:
            session_data = {}

        template = self.properties['template']
        if type(template) is dict:
            template = json.dumps(template)

        vis_json = string_utils.safe_substitute(template, **self.properties, **self.results,  **session_data)

        vis = json.loads(vis_json)
        vis_form = build_vis_form(vis)

        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, vis_form, output="VIS"
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
                            self.issue_nl_query(question, name=question_name, worker=worker)
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
                            self.issue_sql_query(query, name=question_name, worker=worker)
                    if 'questions' not in self.properties and 'queries' not in self.properties:
                        self.render_vis(properties=properties, worker=None)

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

                    self.results[query] = json.dumps(query_results)
                    self.todos.remove(query)

                    # progress
                    self.current_step = len(self.results)
                    q = ""
                    if 'query' in data and data['query']:
                        q = data['query']
                    if 'question' in data and data['question']:
                        q = data['question']

                    worker.write_progress(progress_id=worker.sid, label='Received query results: ' + q, value=self.current_step/self.num_steps)

                    if len(self.todos) == 0:
                        if len(query_results) == 0:
                            self.write_to_new_stream(worker, "No results...", "TEXT")
                            worker.write_progress(progress_id=worker.sid, label='Done...', value=1.0)
                        else:
                            self.render_vis(properties=properties, worker=worker)
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

                    self.results[question] = json.dumps(question_results)
                    self.todos.remove(question)

                    # progress
                    self.current_step = len(self.results)
                    q = ""
                    
                    if 'question' in data and data['question']:
                        q = data['question']

                    worker.write_progress(progress_id=worker.sid, label='Received question results: ' + q, value=self.current_step/self.num_steps)

                    if len(self.todos) == 0:
                        if len(question_results) == 0:
                            self.write_to_new_stream(worker, "No results...", "TEXT")
                            worker.write_progress(progress_id=worker.sid, label='Done...', value=1.0)
                        else:
                            self.render_vis(properties=properties, worker=worker)
                else:
                    logging.info("nothing found")
