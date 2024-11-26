
import logging

###### Parsers, Formats, Utils
import json
from string import Template
import copy

def build_vis_form(vis):
    vis_ui = {
        "type": "Vega",
        "scope": "#/properties/vega-spec",
        "props": {"style": {}} 
    }

    vis_schema = {
        "type": "object",
        "properties": {}
    }

    vis_form = {
        "schema": vis_schema,
        "uischema": vis_ui,
        "data": vis
    }

    return vis_form