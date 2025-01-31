###### Parsers, Formats, Utils
import argparse
import logging
import json
from enum import Enum, auto


###### Blue
from blue.agent import Agent, AgentFactory
from blue.session import Session
from blue.stream import ControlCode
from blue.utils import string_utils, uuid_utils

###### Agent Specific
import ui_builders

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


class InputType(Enum):
    EXTRACTED = auto()
    UPDATE = auto()
    QUESTION = auto()
    ANSWER_PRESENT = auto()
    NONE = auto()


## Helper functions
def parse_result(result):
    columns = result["result"]["columns"]
    data = result["result"]["data"]
    job_list = []
    for item in data:
        job = {key: value for key, value in zip(columns, item)}
        job_list.append(job)
    return {"Results": job_list}

def extract_json(text):
    """
    Helper function to deal with markdown returned by extractor
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Regular expression pattern to match JSON-like structures
        json_pattern = r"```json\s*({.*?})\s*```"

        # Find all matches in the markdown text
        matches = re.findall(json_pattern, text, re.DOTALL)
        if len(matches) > 1:
            logging.warning(
                "More than one JSON object returned. loading only the first one"
            )
        # Parse the matches as JSON
        try:
            json_object = json.loads(matches[0])
            return json_object
        except json.JSONDecodeError:
            logging.warning("Invalid JSON object found, skipping...")
            return {}


############################
### Agent.JobSearch_PlannerAgent
#
class JobSearch_PlannerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "JOBSEARCH_PLANNER"
        super().__init__(**kwargs)
        self.search_predicates = {
            "job title": "",
            "location": "",
            "minimum salary": "",
            "employment type": "",
        }
        self.user_profile = {
            "years of experience": -1,
            "skills": [],
            "suggested_skills": [],
            "confirmed_skills": [],
        }
        self.form_data = {}  # UI form data
        # TODO: this is currently in memory
        # move this into the session stream data.

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _initialize_properties(self):
        super()._initialize_properties()

        # additional properties
        listeners = {}
        # listen to user
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        self.properties["listens"] = listeners
        default_listeners["includes"] = ["USER"]
        default_listeners["excludes"] = [self.name]

        self.properties["tags"] = {"DEFAULT": ["PLAN"]}

    def _start(self):
        super()._start()
        welcome_message = (
            "Welcome to your personal Job Search Assistant! \n\n"
            "I’m here to help you find the perfect role in Singapore's job market."
            "Share your preferences and skills, and I’ll guide you in building a tailored search query, provide market insights.\n\n"
            "Let’s get started! what type of jobs are you looking for?"
        )

        # say hello
        if self.session:
            self.interact(welcome_message)

    def build_plan(self, plan_dag, stream):
        plan_id = uuid_utils.create_uuid()
        plan_context = {"scope": stream[:-7], "streams": {plan_dag[0][0]: stream}}
        plan = {"id": plan_id, "steps": plan_dag, "context": plan_context}
        return plan

    def write_to_new_stream(self, worker, content, stream_name, tags=None):
        id = uuid_utils.create_uuid()
        if worker:
            output_stream = worker.write_data(
                content, output=stream_name, id=id, tags=tags
            )
            worker.write_eos(output=stream_name, id=id)
        return output_stream

    def issue_sql_query(self, query, final, worker):
        """
        system issued sql queries queries.
        """

        # TODO: hard-coded plan and agent names
        plan_query_planner = [
            ["JOBSEARCH_PLANNER.QUERYPLANNER", "NL2SQL-E2E___INPLAN.DEFAULT"],
            ["NL2SQL-E2E___INPLAN.DEFAULT", "JOBSEARCH_PLANNER.ANSWERPLANNER"],
        ]
        plan_query_final = [
            ["JOBSEARCH_PLANNER.QUERYFINAL", "NL2SQL-E2E___INPLAN.DEFAULT"],
            ["NL2SQL-E2E___INPLAN.DEFAULT", "JOBSEARCH_PLANNER.ANSWERFINAL"],
        ]
        if final:
            plan_query = plan_query_final
            output_stream = self.write_to_new_stream(worker, query, "QUERYFINAL")

        else:
            plan_query = plan_query_planner
            output_stream = self.write_to_new_stream(worker, query, "QUERYPLANNER")

        plan = self.build_plan(plan_query, output_stream)
        self.write_to_new_stream(worker, plan, "DEFAULT", tags=["HIDDEN"])

        return

    def update_memory(self, content):
        for key, value in content.items():

            k = key.lower()
            if k in self.search_predicates and len(value) > 0:
                self.search_predicates[k] = value
            if k in self.user_profile:
                if k == "years of experience":
                    try:
                        value = int(value)
                    except:
                        value = -1

                    self.user_profile[k] = max(value, -1)
                else:
                    if len(value) > 0:
                        self.user_profile[k].extend(value)
                        self.user_profile[k] = sorted(list(set(self.user_profile[k])))
        logging.info("UPDATE MEMORY")
        logging.info(self.search_predicates)
        logging.info(self.user_profile)

        return

    def next_action(self, worker):
        """
        Act based on memory
        """
        logging.info("CURRENT MEMORY")
        logging.info(self.search_predicates)
        logging.info(self.user_profile)
        covered_predicates = [k for k, v in self.search_predicates.items() if v]
        if len(covered_predicates) < 2:

            uncovered_predicates = "\n ".join(
                list(set(self.search_predicates.keys()) - set(covered_predicates))
            )

            clarification_question = f"Could you provide more details about your search? For example:\n {uncovered_predicates}"
            return clarification_question

        elif len(self.user_profile["skills"]) == 0:

            profile_form = ui_builders.build_form_profile()
            if worker:
                self.write_to_new_stream(
                    worker=worker,
                    content="Great! Now that I have a basic idea of what you're seeking, let’s dive deeper into your background to understand more about your experience.",
                    stream_name="PRESENT",
                )
                worker.write_control(
                    ControlCode.CREATE_FORM, profile_form, output="FORM"
                )
            return
        # query insights for additional skills
        elif len(self.user_profile["suggested_skills"]) == 0:

            query = f"What are the top 5 skills that co-occur frequently with {self.user_profile['skills'][0]}"
            self.issue_sql_query(query=query, final=False, worker=worker)
            return
        # ask user to confirm suggested skills
        elif len(self.user_profile["confirmed_skills"]) == 0:

            profile_form = ui_builders.build_form_more_skills(
                self.user_profile["suggested_skills"]
            )
            if worker:
                self.write_to_new_stream(
                    worker=worker,
                    content="Based on the details you've shared, we’ve identified additional skills you might possess.",
                    stream_name="PRESENT",
                )

                worker.write_control(
                    ControlCode.CREATE_FORM, profile_form, output="FORM"
                )
            return
        else:

            # issue final query
            logging.info(self.search_predicates)
            logging.info(self.user_profile)
            employment_type = self.search_predicates["employment type"]
            job_title = self.search_predicates["job title"]
            location = self.search_predicates["location"]
            minimum_salary = self.search_predicates["minimum salary"]
            search_skills = [
                item.replace("_", " ")
                for item in self.user_profile["skills"]
                + self.user_profile["confirmed_skills"]
            ]

            yoe = self.user_profile["years of experience"]
            query = (
                f"Find top 5 {employment_type if len(employment_type)>0 else ''} {job_title if len(job_title)> 0 else ''} job ",
                f"in location {location}, " if len(location) > 0 else "",
                (
                    f"with at least {minimum_salary} salary, "
                    if len(minimum_salary) > 0
                    else ""
                ),
                (
                    f"requiring {','.join(search_skills)} skills,  "
                    if len(search_skills) > 0
                    else ""
                ),
                (
                    f"requiring no more than {yoe} years of experience"
                    if yoe > -1
                    else ""
                ),
            )

            self.issue_sql_query(query="".join(query), final=True, worker=worker)
            return

    def action(self, input_type, input_content, user_stream, worker):
        logging.info("ACTION")
        logging.info([input_type, input_content, user_stream])
        # TODO: hard-coded agent name
        plan_extraction = [
            ["USER.TEXT", "OPENAI___EXTRACTOR2.DEFAULT"],
            ["OPENAI___EXTRACTOR2.DEFAULT", "JOBSEARCH_PLANNER.EXTRACTIONS"],
        ]
        plan_query_user = [
            ["USER.TEXT", "NL2SQL-E2E___INPLAN.DEFAULT"],
            ["NL2SQL-E2E___INPLAN.DEFAULT", "JOBSEARCH_PLANNER.ANSWERUSER"],
        ]

        # user asking exploration questions, call NL2Q
        if input_type == InputType.QUESTION.name:
            plan = self.build_plan(plan_query_user, user_stream)
            self.write_to_new_stream(worker, plan, "DEFAULT", tags=["HIDDEN"])
            return
        # present answer to user
        elif input_type == InputType.ANSWER_PRESENT.name:

            self.write_to_new_stream(
                worker=worker,
                content=parse_result(input_content),
                stream_name="PRESENT",
            )
            return
        # user providing information
        # call extractor
        elif input_type == InputType.UPDATE.name:
            plan = self.build_plan(plan_extraction, user_stream)
            self.write_to_new_stream(worker, plan, "DEFAULT", tags=["HIDDEN"])
            return
        elif input_type == InputType.EXTRACTED.name:

            self.update_memory(input_content)
            return self.next_action(worker)
        else:
            return

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        input_type = InputType.NONE.name
        input_content = None
        stream = None
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                stream_data = ""
                if worker:
                    stream_data = worker.get_data(stream)

                # judge user intent
                # TODO: better matching
                user_input = stream_data[0]
                if user_input.lower().startswith("what"):
                    input_type = "QUESTION"
                    input_content = user_input
                else:
                    input_type = "UPDATE"
                    input_content = user_input

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

        elif input == "EXTRACTIONS":
            if message.isData():
                # process and update
                extractions = message.getData()
                extracted = extract_json(extractions)
                # convert to lowercase
                extracted = {
                    key.lower(): value
                    for key, value in extracted.items()
                    if type(value) is int or len(value) > 0
                }
                logging.info("EXTRACTED")
                logging.info(extracted)
                input_type = InputType.EXTRACTED.name
                input_content = extracted

        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    plan_id = form_id = data["form_id"]
                    action = data["action"]

                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")

                    # when the user clicked DONE
                    if action == "DONE_PROFILE":
                        # get form data
                        skills = worker.get_stream_data(
                            "profile_skills.value", stream=form_data_stream
                        )
                        yoe = worker.get_stream_data(
                            "yoe.value", stream=form_data_stream
                        )

                        # close form
                        worker.write_control(
                            ControlCode.CLOSE_FORM,
                            args={"form_id": form_id},
                            output="FORM",
                        )

                        skills = [item["skill"] for item in skills]

                        input_type = InputType.EXTRACTED.name
                        input_content = {"years of experience": yoe, "skills": skills}

                    elif action == "DONE_MORE_SKILLS":
                        # get form data

                        args = {"form_id": form_id}
                        worker.write_control(
                            ControlCode.CLOSE_FORM, args, output="FORM"
                        )

                        input_type = InputType.EXTRACTED.name

                        logging.info("MORE SKILL FORM")
                        logging.info(input_content)

                        confirmed_skills = []
                        for k, v in self.form_data.items():
                            if k.startswith("more_skills.") and v:
                                confirmed_skills.append(k[len("more_skills.") :])
                        input_content = {"confirmed_skills": confirmed_skills}

                    else:
                        # save form data
                        path = data["path"]
                        timestamp = worker.get_stream_data(
                            path + ".timestamp", stream=form_data_stream
                        )

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:

                            worker.set_stream_data(
                                path,
                                {
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=form_data_stream,
                            )
                        timestamp_local = self.form_data.get(path, None)
                        if timestamp_local is not None:
                            timestamp_local = timestamp_local["timestamp"]
                        if (
                            timestamp_local is None
                            or data["timestamp"] > timestamp_local
                        ):
                            self.form_data[path] = {
                                "value": data["value"],
                                "timestamp": data["timestamp"],
                            }

        elif input == "ANSWERPLANNER":
            if message.isData():
                data = message.getData()
                # TODO: hardcoded, only extract for suggested skills query
                logging.info("RETRIEVAL MORE SKILLs")
                logging.info(data)
                input_type = InputType.EXTRACTED.name
                input_content = {
                    "suggested_skills": [
                        string_utils.remove_non_alphanumeric(item[0])
                        for item in data["result"]["data"]
                    ]
                }

        elif input == "ANSWERUSER" or input == "ANSWERFINAL":
            if message.isData():
                data = message.getData()
                input_type = InputType.ANSWER_PRESENT.name
                input_content = data

        else:
            logging.info("unexpected input stream")

        if input_type == InputType.NONE.name:
            return None
        else:
            return self.action(
                input_type=input_type,
                input_content=input_content,
                user_stream=stream,
                worker=worker,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="JOBSEARCH_PLANNER", type=str)
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
            _class=JobSearch_PlannerAgent,
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
            a = JobSearch_PlannerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = JobSearch_PlannerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
