
import logging

###### Parsers, Formats, Utils
import json
from string import Template
import copy

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

    vis_schema = {
        "type": "object",
        "properties": {
            "vis": {
                 "vl-spec": vis 
            }
        }
    }

    vis_form = {
        "schema": vis_schema,
        "uischema": vis_ui,
    }

    return vis_form