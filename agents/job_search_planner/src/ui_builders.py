import json

from numpy import integer


def build_submit_button(action_message):
    return {
        "type": "Button",
        "label": "Submit",
        "props": {
            "intent": "success",
            "action": action_message,
            "large": True,
        },
    }


def build_form_profile(extracted_info):
    # design form
    skills_ui = {
        "type": "Control",
        "scope": "#/properties/profile_skills",
        "options": {
            "detail": {
                "type": "VerticalLayout",
                "elements": [
                    {"type": "Label", "label": "Skills"},
                    {
                        "type": "HorizontalLayout",
                        "elements": [
                            {
                                "type": "Control",
                                "scope": "#/properties/skill",
                            },
                            {
                                "type": "Control",
                                "scope": "#/properties/duration",
                            },
                        ],
                    },
                ],
            }
        },
    }

    form_ui = {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Control",
                "label": "Year of experiences",
                "scope": "#/properties/yoe",
            },
            {
                "type": "Label",
                "label": "Skills Profile",
                "props": {"style": {"fontWeight": "bold"}},
            },
            {
                "type": "Label",
                "label": f"List your skills and determine a duration for each skill",
                "props": {
                    "muted": True,
                    "style": {"marginBottom": 15, "fontStyle": "italic"},
                },
            },
            {"type": "VerticalLayout", "elements": [skills_ui]},
            build_submit_button("DONE_PROFILE"),
        ],
    }

    form_schema = {
        "type": "object",
        "properties": {
            "yoe": {"type": "integer"},
            "profile_skills": {
                "type": "array",
                # "title": "Skills",
                "items": {
                    "type": "object",
                    "properties": {
                        "skill": {"type": "string"},
                        "duration": {"type": "integer"},
                    },
                },
            },
        },
    }

    form = {
        "schema": form_schema,
        "data": {"skills": []},
        "uischema": form_ui,
    }
    print(json.dumps(form_schema))
    print(json.dumps(form_ui))

    return form


def build_form_more_skills(arr):
    """
    Build skill form with checkboxes of predicted skills.
    """

    label_list = [
        [
            {"type": "Label", "label": item},
            {
                "type": "Control",
                "label": " ",
                "props": {"switch": False, "style": {}},
                "scope": f"#/properties/more_skills/properties/{item.lower()}",
                "required": False,
            },
        ]
        for item in arr
    ]

    ui_schema = {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "HorizontalLayout",
                "elements": item,
            }
            for item in label_list
        ]
        + [
            build_submit_button("DONE_MORE_SKILLS"),
        ],
    }

    data_schema = {
        "type": "object",
        "properties": {
            "more_skills": {
                "type": "object",
                "properties": {item.lower(): {"type": "boolean"} for item in arr},
            }
        },
    }

    form = {
        "schema": data_schema,
        "data": {item.lower(): False for item in arr},
        "uischema": ui_schema,
    }
    print(json.dumps(ui_schema))
    print(json.dumps(data_schema))

    return form


build_form_profile("test")
print("---")

build_form_more_skills(["apple", "banana", "orange"])
