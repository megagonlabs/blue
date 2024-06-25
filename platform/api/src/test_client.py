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
ws.send(
    json.dumps(
        {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": session_id,
            "connection_id": connection_id,
            "message": {
                "label": "INTERACTION",
                "content": {
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
                },
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
