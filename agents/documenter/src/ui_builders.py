
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

    doc_schema = {
        "type": "object",
        "properties": {
            "markdown": {
                "md-content": doc
            }
        }
    }

    doc_form = {
        "schema": doc_schema,
        "uischema": doc_ui,
    }

    return doc_form

