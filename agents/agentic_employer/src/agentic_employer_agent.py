###### Parsers, Formats, Utils
import argparse
import logging
import json
import copy
import re

###### Blue
from blue.agent import Agent, AgentFactory
from blue.agents.coordinator import CoordinatorAgent
from blue.session import Session
from blue.stream import ControlCode
from blue.utils import json_utils, string_utils, uuid_utils

##### Agent Specific
import ui_builders

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

##############################
### Agent.AgenticEmployerAgent
#
class AgenticEmployerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "AGENTIC_EMPLOYER"
        super().__init__(**kwargs)
        
    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _start(self):
        super()._start()
        welcome_message = (
            "Hi! \n\n"
            "I’m here to help you find the perfect candidates for your JDs.\n"
            "Let’s get started!\n"
            "Select a JD to work on...\n"
        )

        # say welcome, show form
        if self.session:
            # welcome
            self.interact(welcome_message)

            # init session
            self.init_session()
            
            # ats form
            self.show_ats_form(properties=self.properties)
            
            # get lists
            self.get_lists(properties=self.properties)

            # get job postings 
            self.get_job_postings(properties=self.properties)

    def init_session(self):
        worker = self.create_worker(None)

        # init data, todos
        self.lists = {}
        self.list_id_by_code = {}
        self.job_postings = {}
        self.results = {}
        self.todos = set()
        self.clusters = {}
        self.cluster_id_by_label = {}

        self.selected_job_posting_id = None
        self.selected_list_id = None

        # session data
        worker.set_session_data("JOB_POSTING_ID", self.selected_job_posting_id)
        worker.set_session_data("LISTS", self.lists)
        worker.set_session_data("LIST_ID", self.selected_list_id)


    def build_plan(self, plan_dag, stream, id=None):
        
        # create a plan id
        if id is None:
            id = uuid_utils.create_uuid()
        
        # plan context, initial streams, scope
        plan_context = {"scope": stream[:-7], "streams": {plan_dag[0][0]: stream}}
        
        # construct plan
        plan = {"id": id, "steps": plan_dag, "context": plan_context}

        return plan

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

    def issue_nl_query(self, question, worker, name=None, id=None):

        # create a unique id
        if id is None:
            id = uuid_utils.create_uuid()

        if name is None:
            name = "unspecified"

        # progress
        worker.write_progress(progress_id=worker.sid, label='Issuing question:' + question, value=self.current_step/self.num_steps)

        # query plan
        query_plan = [
            [self.name + ".Q", "NL2SQL-E2E___INPLAN.DEFAULT"],
            ["NL2SQL-E2E___INPLAN.DEFAULT", self.name+".QUESTION_RESULTS_" + name],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, question, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return

    def issue_sql_query(self, query, worker, name=None, id=None):

        # create a unique id
        if id is None:
            id = uuid_utils.create_uuid()

        if name is None:
            name = "unspecified"

        # query plan
        query_plan = [
            [self.name + ".Q", "QUERYEXECUTOR.DEFAULT"],
            ["QUERYEXECUTOR.DEFAULT", self.name+".QUERY_RESULTS_" + name],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    def issue_queries(self, properties=None, worker=None):
        if worker == None:
            worker = self.create_worker(None)

        session_data = worker.get_all_session_data()

        # init results, todos
        self.results = {}
        self.todos = set()

        # issue queries
        if 'queries' in self.properties:
            queries = self.properties['queries']
            for query_name in queries:
                q = queries[query_name]
                if type(q) == dict:
                    q = json.dumps(q)
                else:
                    q = str(q)
                query = string_utils.safe_substitute(q, **properties, **session_data)
                self.todos.add(query_name)
                self.issue_sql_query(query, worker, name=query_name)

    def move_job_seeker_to_list(self, job_seeker_id, from_list, to_list, properties=None, worker=None):
        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        session_data = worker.get_all_session_data()
        
        if type(from_list) == list:
            from_list = ",".join(map(str, from_list))
        else:
            from_list = str(from_list)

        to_list = str(to_list)

        if 'move_job_seeker_to_list' in properties:
            move_job_seeker_to_list_query_template = properties['move_job_seeker_to_list']
            query_template = move_job_seeker_to_list_query_template['query']
            query = string_utils.safe_substitute(query_template, **properties, **session_data, JOB_SEEKER_ID=job_seeker_id, FROM_LIST=from_list, TO_LIST=to_list)
            q = copy.deepcopy(move_job_seeker_to_list_query_template)
            q["query"] = query
            self.issue_sql_query(q, worker, name="move_job_seeker_to_list")
        else:
            logging.error("No `move_job_seeker_to_list` query template found in agent properties!")

    def get_lists(self, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if 'lists' in properties:
            lists_property = properties['lists']

            if type(lists_property) == list:
                self.lists = lists_property
            else:
                # query lists
                query = lists_property
                self.issue_sql_query(query, worker, name="lists")

    def get_job_postings(self, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if 'job_postings' in properties:
            job_postings_property = properties['job_postings']

            if type(job_postings_property) == list:
                self.job_postings = job_postings_property
            else:
                # query job_postings
                query = job_postings_property
                self.issue_sql_query(query, worker, name="job_postings")

    def show_ats_form(self, properties=None, worker=None, update=False):

        if worker == None:
            worker = self.create_worker(None)

        list_actions = []
        job_seeker_actions = []

        if 'actions' in properties:
            if 'LIST' in properties['actions']:
                list_actions = properties['actions']['LIST']
                list_actions = list(list_actions.values())
        
        if 'actions' in properties:
            if 'JOB_SEEKER' in properties['actions']:
                job_seeker_actions = properties['actions']['JOB_SEEKER']
                job_seeker_actions = list(job_seeker_actions.values())

        form = ui_builders.build_ats_form(self.selected_job_posting_id, self.job_postings, self.lists, self.results, list_actions=list_actions, job_seeker_actions=job_seeker_actions)
        form['form_id'] = "ats"

        # write form, updating existing if necessary 
        # update = False
        if update:
            worker.write_control(
                ControlCode.UPDATE_FORM, form, output="FORM", id="ats", scope="agent", tags=["WORKSPACE"]
            )
        else:
            worker.write_control(
                ControlCode.CREATE_FORM, form, output="FORM", id="ats", scope="agent", tags=["WORKSPACE"]
            )


    def view_jd(self,  properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)
    
        # create a unique id
        id = uuid_utils.create_uuid()

        # view plan
        view_plan = [
            [self.name + ".DEFAULT", "DOCUMENTER___JD.DEFAULT"]
        ]
    
        # write job_seeker_id to stream
        a_stream = self.write_to_new_stream(worker, "jd", "DEFAULT", tags=["HIDDEN"], id=id)

        # build plan
        plan = self.build_plan(view_plan, a_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return
    
    def view_job_seeker(self, job_seeker_id, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        # create a unique id
        id = uuid_utils.create_uuid()

        # view plan
        view_plan = [
            [self.name + ".DEFAULT", "DOCUMENTER___JOBSEEKER.DEFAULT"]
        ]
    
        # write job_seeker_id to stream
        a_stream = self.write_to_new_stream(worker, str(job_seeker_id), "DEFAULT", tags=["HIDDEN"], id=id)

        # build plan
        plan = self.build_plan(view_plan, a_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return
    
    def summarize_list(self, list_code, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        session_data = worker.get_all_session_data()

        # create a unique id
        id = uuid_utils.create_uuid()

        # get code from id
        list_id = self.list_id_by_code[list_code]

        # context
        context = session_data
        context['LIST_ID'] = list_id

        # set query
        query = ""
        if "job_seekers_in_list" in properties:
            job_seekers_in_list_query_template = properties['job_seekers_in_list']
            query_template = job_seekers_in_list_query_template['query']
            query = string_utils.safe_substitute(query_template, **properties, **context)
            
        # choose summarizer agent
        summarizer = "SUMMARIZER___LIST"
        if list_code == "all":
            summarizer = "SUMMARIZER___ALL"
        elif list_code == "new":
            summarizer = "SUMMARIZER___RECENT"

        # summary plans
        summary_plan = [
            [self.name + ".SQ", summarizer + ".DEFAULT"]
        ]
        # DEMO
        if list_code == "new":
            summary_plan = [
                [self.name + ".SQ", "SUMMARIZER___RECENTP1" + ".DEFAULT"],
                [self.name + ".SQ", "SUMMARIZER___RECENTP2" + ".DEFAULT"],
                [self.name + ".SQ", "SUMMARIZER___RECENTP3" + ".DEFAULT"]
            ]

        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "SQ", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(summary_plan, query_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return

    def cluster_label_to_id(self, cluster_label):
        if cluster_label in self.cluster_id_by_label:
            return self.cluster_id_by_label[cluster_label]
        else:
            cluster_id = uuid_utils.create_uuid()
            self.cluster_id_by_label[cluster_label] = cluster_id
            return cluster_id
        
    def identify_clusters(self, list_code, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        session_data = worker.get_all_session_data()

        # create a unique id
        id = uuid_utils.create_uuid()

        # get code from id
        list_id = self.list_id_by_code[list_code]

        # context
        context = session_data
        context['LIST_ID'] = list_id

        # set query
        query = ""
        if "job_seekers_in_list" in properties:
            job_seekers_in_list_query_template = properties['job_seekers_in_list']
            query_template = job_seekers_in_list_query_template['query']
            query = string_utils.safe_substitute(query_template, **properties, **context)
            

        # cluster plans
        # cluster_plan = [
        #     [self.name + ".CQ", "CLUSTERER___JOBSEEKER.DEFAULT"],
        #     ["CLUSTERER___JOBSEEKER.CLUSTER_INFO", self.name + ".CLUSTER_INFO_RESULTS"]
        # ]

        cluster_plan = [
            [self.name + ".CQ", "CLUSTERER___JOBSEEKER.DEFAULT"]
        ]

        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "CQ", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(cluster_plan, query_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    def extract_job_posting_id(self, s):
        results = re.findall(r"\[\s*\+?#(-?\d+)\s*\]", s)
        if len(results) > 0:
            return results[0]
        else:
            return None

    def extract_action(self, s):

        # identify scope
        scope = None
        if s.find("_JD_") >= 0:
            scope = "JD"
        elif s.find("_JOB_SEEKER_") >= 0:
            scope = "JOB_SEEKER"
        elif s.find("_LIST_") >= 0:
            scope = "LIST"
        elif s.find("_CLUSTER_") >= 0:
            scope = "CLUSTER"

        if scope is None:
            return None, None, None, None
        
        # process s
        si =  s.find(scope+"_")

        # action
        action = None
        if si > 0:
            action = s[:si-1]

        s = s[si+len(scope + "_"):]
        ss = s.split("_")
        category = None
        id = ss[0]
        if len(ss) > 1:
            category = ss[1]

        return scope, action, id, category


    def handle_action_with_plan(self, scope, action, data, properties=None, worker=None):
        if properties is None:
            properties = self.properties
            
        actions = None
        if "actions" in properties:
            actions = properties['actions']

            if scope in actions:
                scope_actions = actions[scope]

                if action in scope_actions:
                    action_properties = scope_actions[action]

                    if 'plan' in action_properties:
                        p = action_properties['plan']

                        # create worker if not given
                        if worker == None:
                            worker = self.create_worker(None)

                        action_context = {}
                        # merge session data to action context
                        session_data = worker.get_all_session_data()
                        action_context = json_utils.merge_json(action_context, session_data)

                        # input data 
                        if 'input' in action_properties:
                            input = action_properties['input']

                            # additional scope-specific data
                            scope_data = {}
                            if scope == "LIST":
                                list_code = data
                                list_id = self.list_id_by_code[list_code]
                                scope_data["LIST_ID"] = list_id
                                scope_data["LIST_CODE"] = list_code 

                            # merge scope data to action context
                            action_context = json_utils.merge_json(action_context, scope_data)
                            # substitute, if string
                            if type(input) == str:
                                data = string_utils.safe_substitute(input, **properties, **action_context)


                        ## fix plan
                        action_plan = []
                        # substitue self
                        for step in p:
                            f = step[0]
                            t = step[1]

                            if f == "self":
                                f = self.name + "." + action + "_" + scope + "_INPUT"
                            if t == "self":
                                t = self.name + "." + action + "_" + scope + "_OUTPUT"

                            action_plan.append([f,t])

                        # create a unique id
                        id = uuid_utils.create_uuid()

                       

                        # feed data as input, to output variable SCOPE + ACTION + "DATA"
                        a_stream = self.write_to_new_stream(worker, data, action + "_" + scope + "_" + "INPUT", tags=["HIDDEN"], id=id)

                        # build plan
                        plan = self.build_plan(action_plan, a_stream, id=id)

                        # write plan
                        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)


    #### INTENT
    def identify_intent(self, input_stream, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        # create a unique id
        id = uuid_utils.create_uuid()

        # intent plan
        intent_plan = [
            ["USER.TEXT", "OPENAI___CLASSIFIER.DEFAULT"],
            ["OPENAI___CLASSIFIER.DEFAULT", self.name + ".INTENT"]
        ]
    
        # build query plan
        plan = self.build_plan(intent_plan, input_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN", "HIDDEN"], id=id)

        return

    ## INIT ACTION BASED ON INTENT
    def init_action(self, intent, entities, input, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        # get session data
        context = worker.get_all_session_data()

        if context is None:
            context = {}

        if entities is None:
            entities = {}

        # update context, if JOB_POSTING_ID, JOB_SEEKER_ID specified in user input
        if "JOB_POSTING_ID" in entities:
            worker.set_session_data("JOB_POSTING_ID", entities["JOB_POSTING_ID"])

        if "JOB_SEEKER_ID" in entities:
            worker.set_session_data("JOB_SEEKER_ID", entities["JOB_SEEKER_ID"])

        logging.info(intent)
        logging.info(json.dumps(entities))
        logging.info(input)
    
        if intent == "QUERY":
            self.issue_smart_query(context, entities, input, properties=properties, worker=worker)
        elif intent == "VIEW":
            if "JOB_POSTING_ID" in entities:
                self.view_jd(properties=properties, worker=None)
            elif "JOB_SEEKER_ID" in entities:
                job_seeker_id = entities['JOB_SEEKER_ID']
                job_seeker_id = int(job_seeker_id)
                self.view_job_seeker(job_seeker_id, properties=properties, worker=None)
        else:
            self.write_to_new_stream(worker, "I don't know how to help you on that, try summarizing, querying, comparing applies...", "TEXT")  

    #### ACTIONS FROM USER INPUT
    def context_to_nl(self, context):
        context_text = ""
        if 'JOB_SEEKER_ID' in context:
            if context['JOB_SEEKER_ID']:
                context_text += "Job seeker id is " + context['JOB_SEEKER_ID'] + "\n"
        if 'JOB_POSTING_ID' in context:
            if context['JOB_POSTING_ID']:
                context_text += "Job posting id is " + context['JOB_POSTING_ID'] + "\n"
        if 'LIST' in context:
            if context['LIST'] and len(context['LIST']) > 0:
                context_text += "The current list is " + context['LIST'] + "\n"
        return context_text

    def issue_smart_query(self, context, entities, input, properties=None, worker=None):
        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        if "QUESTION" in entities:
            question = entities["QUESTION"]
        else:
            question = input

        # Convert context into text
        context_text = self.context_to_nl(context)
       
        # Provide additional context to user question
        expanded_question = "Answer the following question with the below context. Ignore information in context if the query overrides context:\n"
        expanded_question += "question: " + question + "\n"
        expanded_question += "context: " + "\n" + context_text + "\n"
        
        logging.info("ISSUE NL QUERY:" + expanded_question)

        # create a unique id
        id = uuid_utils.create_uuid()

        # question plan
        question_plan = [
            [self.name + ".QUESTION", "NL2SQL-E2E___INPLAN.DEFAULT"],
            ["NL2SQL-E2E___INPLAN.DEFAULT", "OPENAI___EXPLAINER.DEFAULT"],
        ]

        # write query to strea
        question_stream = self.write_to_new_stream(worker, expanded_question, "QUESTION",  tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(question_plan, question_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN", "HIDDEN"], id=id)

        return



    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):


        ##### PROCESS USER input text
        if input == "DEFAULT":
           
            if message.isEOS():
                stream = message.getStream()

                # identify intent
                self.identify_intent(stream, properties=properties, worker=None)
                
        ##### PROCESS RESULTS FROM INTENT CLASSIFICATION   
        elif input == "INTENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    logging.info(json.dumps(data, indent=3))

                    input = None
                    intent = None
                    entities = {}

                    # massage extracted intent, entities
                    for key in data:
                        if key.upper() == 'INPUT':
                            input = data[key]
                        elif key.upper() == 'INTENT':
                            intent = data[key]
                        elif key.upper() == 'ENTITIES' or key.upper() == "ENTITY":
                            entities = data[key]
                        else:
                            entities[key.upper()] = data[key]

                    self.init_action(intent, entities, input, properties=properties, worker=None)

        ##### PROCESS QUERY RESULTS
        elif input.find("QUERY_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()
            
                # get query 
                query = input[len("QUERY_RESULTS_"):]

                data = message.getData()
            
                if 'result' in data:
                    query_results = data['result']

                    if query == "job_postings":
                        self.job_postings = query_results
                        # render ats form with job postings
                        self.show_ats_form(properties=properties, worker=worker, update=True)
                    elif query == "lists":
                        self.lists = query_results

                        # build id by code
                        for l in self.lists:
                            self.list_id_by_code[l["list_code"]]= l["list_id"]
                        
                        # render ats form with lists
                        self.show_ats_form(properties=properties, worker=worker, update=True)
                    elif query == "move_job_seeker_to_list":
                        # reissue queries, to reflect update in ui
                        self.issue_queries(properties=properties)
                    else:
                        self.todos.remove(query)
                        self.results[query] = query_results

                        # all queries received
                        if len(self.todos) == 0:
                            # render ats form with jobseekers data
                            self.show_ats_form(properties=properties, worker=worker, update=True)
                else:
                    logging.info("nothing found")
    
        ##### PROCESS CLUSTER RESULTS
        elif input == "CLUSTER_INFO_RESULTS":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()

                    clusters = data
                    self.write_to_new_stream(worker, "Analyzing all job seekers, we found " + str(len(clusters)) + " groups...", "TEXT")  

                    cluster_actions = []

                    if 'actions' in properties:
                        if 'CLUSTER' in properties['actions']:
                            cluster_actions = properties['actions']['CLUSTER']
                            cluster_actions = list(cluster_actions.values())
                            
                    for cluster_label in clusters:
                        
                        cluster = clusters[cluster_label]
                        cluster_size = cluster["cluster_size"]
                        cluster_description = cluster["description"]

                        # create a unique id
                        cluster_id = self.cluster_label_to_id(cluster_label)
                        

                        cluster_info = {}
                        if cluster_id in self.clusters:
                            cluster_info = self.clusters[cluster_id]
                        else:
                            self.clusters[cluster_id] = cluster_info

                        cluster_info["id"] = cluster_id
                        cluster_info["label"] = cluster_label
                        cluster_info["size"] = cluster_size
                        cluster_info["description"] = cluster_description

                        cluster_form = ui_builders.get_cluster_summary_ui(cluster_id, cluster_size, cluster_label, cluster_description, actions=cluster_actions)
                        cluster_form['form_id']= "CLUSTER_" + cluster_id

                        worker.write_control(
                            ControlCode.CREATE_FORM, cluster_form, output="CLUSTER_FORM", id=cluster_id, tags=[]
                        )

        elif input == "CLUSTER_MAPPINGS_RESULTS":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()

                    cluster_mappings = data["result"]
                    self.cluster_to_job_seeker = {}

                    for cluster_mapping in cluster_mappings:

                        job_seeker_id = cluster_mapping['id']
                        cluster_label = cluster_mapping['cluster']
                        cluster_id = self.cluster_label_to_id(cluster_label)

                        cluster_info = {}
                        if cluster_id in self.clusters:
                            cluster_info = self.clusters[cluster_id]
                        else:
                            self.clusters[cluster_id] = cluster_info

                        cluster_info["id"] = cluster_id
                        cluster_job_seekers = []
                        if "job_seekers" in cluster_info:
                            cluster_job_seekers = cluster_info["job_seekers"]
                        else:
                            cluster_info["job_seekers"] = cluster_job_seekers
                        
                        cluster_job_seekers.append(job_seeker_id)





                        

        ##### PROCESS FORM UI EVENTS
        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    form_id = data["form_id"]
                    action = data["action"]
                    
                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")
                    
                    print(action)
                    print(form_id)
                    if form_id == "ats":
                        if action is None:
                            # save form data
                            path = data["path"]
                            value = data["value"]

                            timestamp = worker.get_data(path + ".timestamp")

                            if timestamp is None or data["timestamp"] > timestamp:

                                prev_value = worker.get_data(path + ".value")
                                
                                worker.set_data(path,
                                    {
                                        "value": value,
                                        "timestamp": data["timestamp"],
                                    }
                                )
                                
                                # new job posting selected
                                if path == "job_posting":
                                    # new value
                                    if prev_value != value:
                                        # extract JOB_POSTING_ID
                                        JOB_POSTING_ID = self.extract_job_posting_id(value)
                                        if JOB_POSTING_ID:
                                            # save to session
                                            worker.set_session_data("JOB_POSTING_ID", JOB_POSTING_ID)
                                            self.selected_job_posting_id = JOB_POSTING_ID

                                            # issue other queries to populate tabs
                                            self.issue_queries(properties=properties, worker=worker)

                                            # issue recent summarizer
                                            self.summarize_list("new", properties=properties, worker=None)

                                            # issue clusters
                                            self.identify_clusters("all", properties=properties, worker=None)


                                # job seeker actions
                                else:
                                    scope, action, id, category = self.extract_action(path)
                                    
                                    if scope == "JOB_SEEKER" and action == "INTEREST":
                                        
                                        # interested value to code
                                        interested_enums_by_list_code = {"✓": 2, "?": 3, "𐄂":4 }
                                        from_list = list(interested_enums_by_list_code.values())
                                        to_list = interested_enums_by_list_code[value]

                                        # issue db delete/insert transaction
                                        self.move_job_seeker_to_list(id, from_list, to_list, properties=properties, worker=worker)
                        else:
                            scope, action, id, category = self.extract_action(action)
                            self.handle_action_with_plan(scope, action, str(id), properties=properties, worker=None)

                    elif form_id.find("CLUSTER_") == 0:
                        scope, action, id, category = self.extract_action(action)
                        
                        cluster_id = id
                        if cluster_id in self.clusters:
                            cluster_info = self.clusters[cluster_id]
                            if "job_seekers" in cluster_info:
                                job_seekers = cluster_info["job_seekers"]
                                self.handle_action_with_plan(scope, action, ",".join([str(js) for js in job_seekers]), properties=properties, worker=None)

                        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="AGENTIC_EMPLOYER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str)
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.serve:
        platform = args.platform

        af = AgentFactory(
            _class=AgenticEmployerAgent,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = AgenticEmployerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = AgenticEmployerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
