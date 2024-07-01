import json
import random
import time
import uuid

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


session_id = input("session_id: ")
connection_id = input("connection_id: ")
for _ in range(1):
    stream_id = f"local-test-client-{int(time.time() * 1000)}"
    sentence_string = sentence()
    words_string = words(random.randint(4, 11))
    ws.send(
        json.dumps(
            {
                "type": "OBSERVER_SESSION_MESSAGE",
                "session_id": session_id,
                "connection_id": connection_id,
                "message": {'label': "BOS", 'content': None, 'dtype': None},
                "stream": stream_id,
                "mode": "streaming",
                "timestamp": int(time.time() * 1000),
                "id": str(uuid.uuid4()),
                "order": 0,
            }
        )
    )
    ws.send(
        json.dumps(
            {
                "type": "OBSERVER_SESSION_MESSAGE",
                "connection_id": connection_id,
                "session_id": session_id,
                "message": {"label": "DATA", "content": random.choice([sentence_string, words_string]), "dtype": "str"},
                "stream": stream_id,
                "mode": "streaming",
                "timestamp": int(time.time() * 1000),
                "id": str(uuid.uuid4()),
                "order": 0,
            }
        )
    )
    ws.send(
        json.dumps(
            {
                "type": "OBSERVER_SESSION_MESSAGE",
                "session_id": session_id,
                "connection_id": connection_id,
                "message": {'label': "EOS", 'content': None, 'dtype': None},
                "stream": stream_id,
                "mode": "streaming",
                "timestamp": int(time.time() * 1000),
                "id": str(uuid.uuid4()),
                "order": 0,
            }
        )
    )
time.sleep(2)
stream_id = f"local-test-client-{int(time.time() * 1000)}"
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {'label': "BOS", 'content': None, 'dtype': None},
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
json_form = {
    "type": "JSONFORM",
    "form_id": 'local-test-client-form-1',
    "content": {
        "schema": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
        },
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
    },
}
# json_form = json.loads(
#     '{"type": "JSONFORM", "content": {"schema": {"type": "object", "properties": {"step_0": {"type": "object", "properties": {"selected": {"type": "boolean"}, "from_agent": {"type": "string", "enum": ["USER"]}, "from_output": {"type": "string", "enum": ["TEXT"]}, "to_agent": {"type": "string", "enum": ["FORM_PROFILER"]}, "to_input": {"type": "string", "enum": ["PROFILE"]}}}, "step_1": {"type": "object", "properties": {"selected": {"type": "boolean"}, "from_agent": {"type": "string", "enum": ["FORM_PROFILER"]}, "from_output": {"type": "string", "enum": ["PROFILE"]}, "to_agent": {"type": "string", "enum": ["JOBSEARCH"]}, "to_input": {"type": "string", "enum": ["JOBSEEKERDATA"]}}}, "step_2": {"type": "object", "properties": {"selected": {"type": "boolean"}, "from_agent": {"type": "string", "enum": ["USER"]}, "from_output": {"type": "string", "enum": ["TEXT"]}, "to_agent": {"type": "string", "enum": ["JOBSEARCH"]}, "to_input": {"type": "string", "enum": ["CRITERIA"]}}}}}, "uischema": {"type": "VerticalLayout", "elements": [{"type": "Label", "label": "PROPOSED PLAN", "props": {"style": {"fontWeight": "bold"}}}, {"type": "Label", "label": "Review the proposed plan below and if necessary make appropriate adjustments", "props": {"muted": true, "style": {"marginBottom": 15, "fontStyle": "italic"}}}, {"type": "VerticalLayout", "elements": [{"type": "Group", "label": "STEP 0", "props": {"collapsible": true, "compact": true, "style": {"marginBottom": 15}}, "elements": [{"type": "Control", "props": {"large": true, "switch": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}, "scope": "#/properties/step_0/properties/selected"}, {"type": "VerticalLayout", "elements": [{"type": "VerticalLayout", "elements": [{"type": "Label", "label": "From:", "props": {"style": {"fontWeight": "bold"}}}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Agent:", "scope": "#/properties/step_0/properties/from_agent", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Parameter:", "scope": "#/properties/step_0/properties/from_output", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}]}]}, {"type": "VerticalLayout", "elements": [{"type": "Label", "label": "To:", "props": {"style": {"fontWeight": "bold"}}}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Agent:", "scope": "#/properties/step_0/properties/to_agent", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Parameter:", "scope": "#/properties/step_0/properties/to_input", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}]}]}, {"type": "Group", "label": "STEP 1", "props": {"collapsible": true, "compact": true, "style": {"marginBottom": 15}}, "elements": [{"type": "Control", "props": {"large": true, "switch": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}, "scope": "#/properties/step_1/properties/selected"}, {"type": "VerticalLayout", "elements": [{"type": "VerticalLayout", "elements": [{"type": "Label", "label": "From:", "props": {"style": {"fontWeight": "bold"}}}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Agent:", "scope": "#/properties/step_1/properties/from_agent", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Parameter:", "scope": "#/properties/step_1/properties/from_output", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}]}]}, {"type": "VerticalLayout", "elements": [{"type": "Label", "label": "To:", "props": {"style": {"fontWeight": "bold"}}}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Agent:", "scope": "#/properties/step_1/properties/to_agent", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Parameter:", "scope": "#/properties/step_1/properties/to_input", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}]}]}, {"type": "Group", "label": "STEP 2", "props": {"collapsible": true, "compact": true, "style": {"marginBottom": 15}}, "elements": [{"type": "Control", "props": {"large": true, "switch": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}, "scope": "#/properties/step_2/properties/selected"}, {"type": "VerticalLayout", "elements": [{"type": "VerticalLayout", "elements": [{"type": "Label", "label": "From:", "props": {"style": {"fontWeight": "bold"}}}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Agent:", "scope": "#/properties/step_2/properties/from_agent", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Parameter:", "scope": "#/properties/step_2/properties/from_output", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}]}]}, {"type": "VerticalLayout", "elements": [{"type": "Label", "label": "To:", "props": {"style": {"fontWeight": "bold"}}}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Agent:", "scope": "#/properties/step_2/properties/to_agent", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}, {"type": "HorizontalLayout", "props": {"spaceEvenly": false}, "elements": [{"type": "Control", "label": "Parameter:", "scope": "#/properties/step_2/properties/to_input", "props": {"inline": true, "streamId": "PLATFORM:dev:SESSION:17ae09bf:AGENT:INTERACTIVEPLANNER:24898e88:STREAM:d190aa10:EVENT_MESSAGE:c99c9e0d", "formId": "c99c9e0d"}}, {"type": "Label", "label": "", "props": {"muted": true, "small": true, "style": {"fontStyle": "italic"}}}]}]}]}]}]}}, "form_id": "c99c9e0d"}'
# )
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {
                "label": "INTERACTION",
                "content": json_form,
                "dtype": 'json',
            },
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
time.sleep(2)
sentence_string = sentence()
words_string = words(random.randint(4, 11))
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {
                "label": "INTERACTION",
                "content": {"type": "DONE", "form_id": 'local-test-client-form-1'},
            },
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
time.sleep(1)
stream_id = f"local-test-client-{int(time.time() * 1000)}"
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {'label': "BOS", 'content': None, 'dtype': None},
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {
                "label": "DATA",
                "content": {"type": "DONE"},
                "dtype": "json",
            },
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {
                "label": "DATA",
                "content": {"type": "NOT_DONE"},
                "dtype": "json",
            },
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {'label': "EOS", 'content': None, 'dtype': None},
            "stream": stream_id,
            "mode": "streaming",
            "timestamp": int(time.time() * 1000),
            "id": str(uuid.uuid4()),
            "order": 0,
        }
    )
)
time.sleep(1)
ws.close()
