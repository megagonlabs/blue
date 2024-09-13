def build_skill_form(extracted_info):
    # design form
    skills_ui = {
        "type": "Control",
        "scope": "#/properties/skills",
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
            {
                "type": "Button",
                "label": "Submit",
                "props": {
                    "intent": "success",
                    "action": "DONE",
                    "large": True,
                },
            },
        ],
    }

    form_schema = {
        "type": "object",
        "properties": {
            "skills": {
                "type": "array",
                "title": "Skills",
                "items": {
                    "type": "object",
                    "properties": {
                        "skill": {"type": "string"},
                        "duration": {"type": "string"},
                    },
                },
            }
        },
    }

    form = {
        "schema": form_schema,
        "data": {"skills": []},
        "uischema": form_ui,
    }
    return form
