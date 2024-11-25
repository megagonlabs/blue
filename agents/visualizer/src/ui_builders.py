
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

    vis_schema = {}

    vis_data = {
        "vis": {
                "vl-spec": vis 
        }
    }

    vis_form = {
        "schema": vis_schema,
        "uischema": vis_ui,
        "data": vis_data
    }

    return vis_form