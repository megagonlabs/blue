from importlib import metadata
import json
import random
import time
import uuid
import sys
from websocket import create_connection

ws = create_connection("ws://localhost:5050/blue/platform/default/sessions/ws")
result = ws.recv()
COMMON_P = (
    "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint "
    "occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
    "mollit anim id est laborum."
)
WORDS = (
    "exercitationem",
    "perferendis",
    "perspiciatis",
    "laborum",
    "eveniet",
    "sunt",
    "iure",
    "nam",
    "nobis",
    "eum",
    "cum",
    "officiis",
    "excepturi",
    "odio",
    "consectetur",
    "quasi",
    "aut",
    "quisquam",
    "vel",
    "eligendi",
    "itaque",
    "non",
    "odit",
    "tempore",
    "quaerat",
    "dignissimos",
    "facilis",
    "neque",
    "nihil",
    "expedita",
    "vitae",
    "vero",
    "ipsum",
    "nisi",
    "animi",
    "cumque",
    "pariatur",
    "velit",
    "modi",
    "natus",
    "iusto",
    "eaque",
    "sequi",
    "illo",
    "sed",
    "ex",
    "et",
    "voluptatibus",
    "tempora",
    "veritatis",
    "ratione",
    "assumenda",
    "incidunt",
    "nostrum",
    "placeat",
    "aliquid",
    "fuga",
    "provident",
    "praesentium",
    "rem",
    "necessitatibus",
    "suscipit",
    "adipisci",
    "quidem",
    "possimus",
    "voluptas",
    "debitis",
    "sint",
    "accusantium",
    "unde",
    "sapiente",
    "voluptate",
    "qui",
    "aspernatur",
    "laudantium",
    "soluta",
    "amet",
    "quo",
    "aliquam",
    "saepe",
    "culpa",
    "libero",
    "ipsa",
    "dicta",
    "reiciendis",
    "nesciunt",
    "doloribus",
    "autem",
    "impedit",
    "minima",
    "maiores",
    "repudiandae",
    "ipsam",
    "obcaecati",
    "ullam",
    "enim",
    "totam",
    "delectus",
    "ducimus",
    "quis",
    "voluptates",
    "dolores",
    "molestiae",
    "harum",
    "dolorem",
    "quia",
    "voluptatem",
    "molestias",
    "magni",
    "distinctio",
    "omnis",
    "illum",
    "dolorum",
    "voluptatum",
    "ea",
    "quas",
    "quam",
    "corporis",
    "quae",
    "blanditiis",
    "atque",
    "deserunt",
    "laboriosam",
    "earum",
    "consequuntur",
    "hic",
    "cupiditate",
    "quibusdam",
    "accusamus",
    "ut",
    "rerum",
    "error",
    "minus",
    "eius",
    "ab",
    "ad",
    "nemo",
    "fugit",
    "officia",
    "at",
    "in",
    "id",
    "quos",
    "reprehenderit",
    "numquam",
    "iste",
    "fugiat",
    "sit",
    "inventore",
    "beatae",
    "repellendus",
    "magnam",
    "recusandae",
    "quod",
    "explicabo",
    "doloremque",
    "aperiam",
    "consequatur",
    "asperiores",
    "commodi",
    "optio",
    "dolor",
    "labore",
    "temporibus",
    "repellat",
    "veniam",
    "architecto",
    "est",
    "esse",
    "mollitia",
    "nulla",
    "a",
    "similique",
    "eos",
    "alias",
    "dolore",
    "tenetur",
    "deleniti",
    "porro",
    "facere",
    "maxime",
    "corrupti",
)
COMMON_WORDS = ("lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipisicing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua")


def sentence():
    sections = [" ".join(random.sample(WORDS, random.randint(3, 12))) for i in range(random.randint(2, 5))]
    s = ", ".join(sections)
    return "%s%s%s" % (s[0].upper(), s[1:], random.choice("?."))


def words(count):
    word_list = []
    c = len(word_list)
    if count > c:
        count -= c
        while count > 0:
            c = min(count, len(WORDS))
            count -= c
            word_list += random.sample(WORDS, c)
    else:
        word_list = word_list[:count]
    return " ".join(word_list)


def send_bos(ws, session_id, connection_id, stream_id, metadata={}):
    ws.send(
        json.dumps(
            {
                "type": "OBSERVER_SESSION_MESSAGE",
                "session_id": session_id,
                "connection_id": connection_id,
                "message": {'label': "CONTROL", 'contents': {"code": "BOS"}, 'content_type': None},
                "stream": stream_id,
                "metadata": {'created_by': 'OBSERVER', **metadata},
                "mode": "streaming",
                "timestamp": int(time.time() * 1000),
                "id": str(uuid.uuid4()),
                "order": 0,
            }
        )
    )


def send_eos(ws, session_id, connection_id, stream_id):
    ws.send(
        json.dumps(
            {
                "type": "OBSERVER_SESSION_MESSAGE",
                "session_id": session_id,
                "connection_id": connection_id,
                "message": {'label': "CONTROL", 'contents': {"code": "EOS"}, 'content_type': None},
                "stream": stream_id,
                "metadata": {'created_by': 'OBSERVER'},
                "mode": "streaming",
                "timestamp": int(time.time() * 1000),
                "id": str(uuid.uuid4()),
                "order": 0,
            }
        )
    )


def send_message(ws, session_id, connection_id, stream_id, message):
    ws.send(
        json.dumps(
            {
                "type": "OBSERVER_SESSION_MESSAGE",
                "connection_id": connection_id,
                "session_id": session_id,
                "message": message,
                "stream": stream_id,
                "metadata": {'created_by': 'OBSERVER'},
                "mode": "streaming",
                "timestamp": int(time.time() * 1000),
                "id": str(uuid.uuid4()),
                "order": 0,
            }
        )
    )


session_id = input("session_id: ")
connection_id = input("connection_id: ")
for _ in range(1):
    stream_id = f"local-test-client-{int(time.time() * 1000)}"
    sentence_string = sentence()
    words_string = words(random.randint(4, 11))
    send_bos(ws, session_id, connection_id, stream_id)
    send_message(ws, session_id, connection_id, stream_id, message={"label": "DATA", "contents": random.choice([sentence_string, words_string]), "content_type": "STR"})
    send_eos(ws, session_id, connection_id, stream_id)
time.sleep(2)
# sys.exit()
stream_id = f"local-test-client-{int(time.time() * 1000)}"
send_bos(ws, session_id, connection_id, stream_id, metadata={"tags": {"WORKSPACE": True}})
json_form = {
    "code": "CREATE_FORM",
    "args": {
        "form_id": 'local-test-client-form-1',
        "uischema": {
            "type": "HorizontalLayout",
            "elements": [
                {
                    "type": "Control",
                    "label": "First Name",
                    "scope": "#/properties/first_name",
                },
                {
                    "type": "Control",
                    "label": "Last Name",
                    "scope": "#/properties/last_name",
                },
            ],
        },
        "schema": {"type": "object", "properties": {"first_name": {"type": "string"}, "last_name": {"type": "string"}}},
    },
}
send_message(
    ws,
    session_id,
    connection_id,
    stream_id,
    message={
        "label": "CONTROL",
        "contents": json_form,
        "content_type": 'JSON',
    },
)
send_eos(ws, session_id, connection_id, stream_id)
time.sleep(2)
send_bos(ws, session_id, connection_id, stream_id, metadata={"tags": {"WORKSPACE": True}})
json_form["code"] = 'UPDATE_FORM'
json_form["args"]['uischema'] = {
    "type": "HorizontalLayout",
    "elements": [
        {
            "type": "Control",
            "label": "Last Name",
            "scope": "#/properties/last_name",
        },
        {
            "type": "Control",
            "label": "First Name",
            "scope": "#/properties/first_name",
        },
    ],
}
json_form['args']['schema'] = {"type": "object", "properties": {"first_name": {"type": "string"}, "last_name": {"type": "string"}}}
send_message(
    ws,
    session_id,
    connection_id,
    stream_id,
    message={
        "label": "CONTROL",
        "contents": json_form,
        "content_type": 'JSON',
    },
)
send_eos(ws, session_id, connection_id, stream_id)
# sys.exit()
time.sleep(2)
send_message(
    ws,
    session_id,
    connection_id,
    stream_id,
    message={
        "label": "CONTROL",
        "contents": {"code": "CLOSE_FORM", "args": {"form_id": 'local-test-client-form-1'}},
    },
)
time.sleep(1)
send_eos(ws, session_id, connection_id, stream_id)
# sys.exit()
time.sleep(1)
stream_id = f"local-test-client-{int(time.time() * 1000)}"
json_form = {
    "code": "CREATE_FORM",
    "args": {
        "schema": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "title": "Steps",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from_agent": {
                                "type": "string",
                                "enum": [
                                    "USER",
                                    "RECORDER",
                                    "OBSERVER",
                                    "COORDINATOR",
                                    "INTERACTIVEPLANNER",
                                    "GPTPLANNER",
                                    "NEO4J",
                                    "POSTGRES",
                                    "OPENAI",
                                    "OPENAI_SQLQUERY",
                                    "FORM",
                                    "JOBSEARCH",
                                    "FORM_PROFILER",
                                    "OPENAI_PLANNER",
                                ],
                            },
                            "from_agent_param": {"type": "string", "enum": ["QUERY", "PROFILE", "RESULT", "JOBSEEKERDATA", "OUTPUT", "CRITERIA", "PROMPT", "TEXT", "JOBS", "DATA", "MATCHES"]},
                            "to_agent": {
                                "type": "string",
                                "enum": [
                                    "USER",
                                    "RECORDER",
                                    "OBSERVER",
                                    "COORDINATOR",
                                    "INTERACTIVEPLANNER",
                                    "GPTPLANNER",
                                    "NEO4J",
                                    "POSTGRES",
                                    "OPENAI",
                                    "OPENAI_SQLQUERY",
                                    "FORM",
                                    "JOBSEARCH",
                                    "FORM_PROFILER",
                                    "OPENAI_PLANNER",
                                ],
                            },
                            "to_agent_param": {"type": "string", "enum": ["QUERY", "PROFILE", "RESULT", "JOBSEEKERDATA", "OUTPUT", "CRITERIA", "PROMPT", "TEXT", "JOBS", "DATA", "MATCHES"]},
                        },
                    },
                }
            },
        },
        "data": {
            "steps": [
                {"from_agent": "USER", "from_agent_param": "TEXT", "to_agent": "FORM_PROFILER", "to_agent_param": "PROFILE"},
                {"from_agent": "FORM_PROFILER", "from_agent_param": "PROFILE", "to_agent": "JOBSEARCH", "to_agent_param": "JOBSEEKERDATA"},
                {"from_agent": "JOBSEARCH", "from_agent_param": "MATCHES", "to_agent": "RECORDER", "to_agent_param": "RESULT"},
            ],
            "context": {
                "scope": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d",
                "streams": {"USER.TEXT": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:STREAM"},
            },
        },
        "uischema": {
            "type": "VerticalLayout",
            "elements": [
                {"type": "Label", "label": "PROPOSED PLAN", "props": {"style": {"fontWeight": "bold"}}},
                {
                    "type": "Label",
                    "label": "Review the proposed plan below and if necessary make appropriate adjustments",
                    "props": {"muted": True, "style": {"margin-bottom": '15px', "fontStyle": "italic"}},
                },
                {
                    "type": "VerticalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "scope": "#/properties/steps",
                            "options": {
                                "detail": {
                                    "type": "VerticalLayout",
                                    "elements": [
                                        {"type": "Label", "label": "From"},
                                        {
                                            "type": "HorizontalLayout",
                                            "elements": [
                                                {
                                                    "type": "Control",
                                                    "scope": "#/properties/from_agent",
                                                    "props": {"streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:INTERACTIVEPLANNER:730d15d5:EVENT:d15ef06d:STREAM", "formId": "d15ef06d"},
                                                },
                                                {
                                                    "type": "Control",
                                                    "scope": "#/properties/from_agent_param",
                                                    "props": {"streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:INTERACTIVEPLANNER:730d15d5:EVENT:d15ef06d:STREAM", "formId": "d15ef06d"},
                                                },
                                            ],
                                        },
                                        {"type": "Label", "label": "To"},
                                        {
                                            "type": "HorizontalLayout",
                                            "elements": [
                                                {
                                                    "type": "Control",
                                                    "scope": "#/properties/to_agent",
                                                    "props": {"streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:INTERACTIVEPLANNER:730d15d5:EVENT:d15ef06d:STREAM", "formId": "d15ef06d"},
                                                },
                                                {
                                                    "type": "Control",
                                                    "scope": "#/properties/to_agent_param",
                                                    "props": {"streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:INTERACTIVEPLANNER:730d15d5:EVENT:d15ef06d:STREAM", "formId": "d15ef06d"},
                                                },
                                            ],
                                        },
                                    ],
                                }
                            },
                            "props": {"visualization": "DAG", "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:INTERACTIVEPLANNER:730d15d5:EVENT:d15ef06d:STREAM", "formId": "d15ef06d"},
                        }
                    ],
                },
                {
                    "type": "Button",
                    "label": "Submit",
                    "props": {
                        "intent": "success",
                        "action": "DONE",
                        "large": True,
                        "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:INTERACTIVEPLANNER:730d15d5:EVENT:d15ef06d:STREAM",
                        "formId": "d15ef06d",
                    },
                },
            ],
        },
        "form_id": "d15ef06d",
    },
}
send_bos(ws, session_id, connection_id, stream_id)
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {
                "label": "CONTROL",
                "contents": json_form,
                "content_type": 'JSON',
            },
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
send_eos(ws, session_id, connection_id, stream_id)
time.sleep(1)
stream_id = f"local-test-client-{int(time.time() * 1000)}"
send_bos(ws, session_id, connection_id, stream_id)
send_message(
    ws,
    session_id,
    connection_id,
    stream_id,
    message={
        "label": "DATA",
        "contents": {
            "id": "d15ef06d",
            "steps": [["USER.TEXT", "FORM_PROFILER.CRITERIA"], ["FORM_PROFILER.PROFILE", "JOBSEARCH.JOBSEEKERDATA"]],
            "context": {
                "scope": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d",
                "streams": {"USER.TEXT": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:STREAM"},
            },
        },
        "content_type": "JSON",
    },
)
send_message(
    ws,
    session_id,
    connection_id,
    stream_id,
    message={
        "label": "DATA",
        "contents": {"name": "John", "current_title": "engineer", "desired_title": "engineer", "desired_location": "mountan view", "skills": "python"},
        "content_type": "JSON",
    },
)
send_eos(ws, session_id, connection_id, stream_id)
time.sleep(1)
stream_id = f"local-test-client-{int(time.time() * 1000)}"
json_form = {
    "code": "CREATE_FORM",
    "args": {
        "schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "current_title": {"type": "string"}, "desired_title": {"type": "string"}, "desired_location": {"type": "string"}, "skills": {"type": "string"}},
        },
        "uischema": {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "VerticalLayout",
                    "elements": [
                        {"type": "Label", "label": "Job Search Form", "props": {"large": True, "style": {"margin-bottom": '15px', "fontSize": "15pt"}}},
                        {
                            "type": "Label",
                            "label": "Please fill out below information about yourself.",
                            "props": {"large": True, "style": {"margin-bottom": '15px', "fontSize": "10pt", "fontStyle": "italic"}},
                        },
                        {
                            "type": "HorizontalLayout",
                            "elements": [
                                {
                                    "type": "Control",
                                    "label": "Name",
                                    "scope": "#/properties/name",
                                    "props": {
                                        "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:PLAN:d15ef06d:FORM_PROFILER:7c0b0731:EVENT:a7d80949:STREAM",
                                        "formId": "a7d80949",
                                    },
                                }
                            ],
                        },
                        {
                            "type": "Control",
                            "label": "Current Title",
                            "scope": "#/properties/current_title",
                            "props": {
                                "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:PLAN:d15ef06d:FORM_PROFILER:7c0b0731:EVENT:a7d80949:STREAM",
                                "formId": "a7d80949",
                            },
                        },
                        {
                            "type": "Control",
                            "label": "Skills",
                            "scope": "#/properties/skills",
                            "props": {
                                "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:PLAN:d15ef06d:FORM_PROFILER:7c0b0731:EVENT:a7d80949:STREAM",
                                "formId": "a7d80949",
                            },
                        },
                        {"type": "Label", "label": " ", "props": {"large": True, "style": {"margin-bottom": '15px', "fontSize": "12pt", "border-bottom": "thin solid gray"}}},
                        {"type": "Label", "label": "Job Information", "props": {"large": True, "style": {"margin-bottom": '15px', "fontSize": "12pt"}}},
                        {
                            "type": "Label",
                            "label": "Please fill out below information about your desired job.",
                            "props": {"large": True, "style": {"margin-bottom": '15px', "fontSize": "10pt", "fontStyle": "italic"}},
                        },
                        {
                            "type": "Control",
                            "label": "Desired Title",
                            "scope": "#/properties/desired_title",
                            "props": {
                                "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:PLAN:d15ef06d:FORM_PROFILER:7c0b0731:EVENT:a7d80949:STREAM",
                                "formId": "a7d80949",
                            },
                        },
                        {
                            "type": "Control",
                            "label": "Desired Location",
                            "scope": "#/properties/desired_location",
                            "props": {
                                "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:PLAN:d15ef06d:FORM_PROFILER:7c0b0731:EVENT:a7d80949:STREAM",
                                "formId": "a7d80949",
                            },
                        },
                    ],
                },
                {
                    "type": "Button",
                    "label": "Submit",
                    "props": {
                        "intent": "success",
                        "action": "DONE",
                        "large": True,
                        "streamId": "PLATFORM:default:SESSION:74a7ce7:AGENT:USER:5WgRzdacRdOEvj8JBmCXFZSvWmH3:OUTPUT:TEXT:29051a4d:PLAN:d15ef06d:FORM_PROFILER:7c0b0731:EVENT:a7d80949:STREAM",
                        "formId": "a7d80949",
                    },
                },
            ],
        },
        "form_id": "a7d80949",
    },
}
send_bos(ws, session_id, connection_id, stream_id)
send_message(
    ws,
    session_id,
    connection_id,
    stream_id,
    message={
        "label": "CONTROL",
        "contents": json_form,
        "content_type": 'JSON',
    },
)
send_eos(ws, session_id, connection_id, stream_id)
time.sleep(1)
ws.close()
