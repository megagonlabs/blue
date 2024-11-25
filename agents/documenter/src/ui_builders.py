
import logging

###### Parsers, Formats, Utils
import json
from string import Template
import copy

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

