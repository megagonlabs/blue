
import logging

###### Parsers, Formats, Utils
import json
from string import Template
import copy


def get_list_action_ui(action, list_id, list_code):
   return {
        "type": "Button",
        "label": action['label'],
        "props": {
            "action": action['name']+'_'+list_code,
            "large": False
        }
    }

def get_list_ui(list_id, list_code, list_name, list_contents, actions=None):

    if actions == None:
        actions = [{"name":"COMPARE", "label":"Compare"},{"name":"SUMMARIZE","label":"Summarize"}]

    list_actions = []
    for action in actions:
        list_actions.append(get_list_action_ui(action, list_id, list_code))

    list_ui = {
        "type": "Group",
        "label": list_name + " [" + str(len(list_contents)) + "]",
        "props": {
            "collapsible": True,
            "defaultIsOpen": True,
            "compact": False,
            "style": {
                "width": 800
            }
        },
        "elements": [
            {
                "type": "VerticalLayout",
                "elements": [
                    get_list_header(),
                    get_separator(separator='━'),
                    {
                        "type": "VerticalLayout",
                        "elements": list_contents
                    },
                    get_separator(separator='━'),
                    {
                        "type": "HorizontalLayout",
                        "elements": list_actions,
                        "props": {
                            "spaceEvenly": False
                        }
                    },
                    {
                        "type": "Label",
                        "label": " ",
                        "props": {
                            "muted": True,
                            "style": {
                                "marginBottom": 5,
                                "fontStyle": "italic"
                            }
                        }
                    }
                ]
            }
        ]
    }

    return list_ui

def get_list_header(headers=None):
    if headers == None:
        headers = ["Candidate", "Matches", "Actions", "Interested?"]

    elements = []
    for header in headers:
        elements.append({
            "type": "Label",
            "label": header,
            "props": {
                "style": {
                    "width": 200,
                    "fontSize": 16,
                    "fontWeight": "bold"
                }
            }
        })
        
    return {
        "type": "HorizontalLayout",
        "elements": elements,
        "props": {
            "spaceEvenly": False
        }
    }

def get_separator(separator='┄', length=50, margin=10):
    return {
        "type": "Label",
        "label": separator * length,
        "props": {
            "muted": True,
            "style": {
                "marginBottom": margin,
            }
        }
    }

def build_ats_form(job_postings, lists, data):
    
    all_list_contents = {}
    ## lists
    lists_ui = {}
    for l in lists:
        list_contents = []
        all_list_contents[l['list_code']] = list_contents
        lists_ui[l['list_id']] = get_list_ui(l['list_id'], l['list_code'], l['list_name'], list_contents)

    form_ui = {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "HorizontalLayout",
                "props": {
                    "spaceEvenly": False
                },
                "elements": [
                    {
                        "type": "Control",
                        "scope": "#/properties/job_posting"
                    },
                    {
                        "type": "Button",
                        "label": "View JD",
                        "props": {
                            "action": "VIEW_JD",
                            "large": False
                        }
                    }
                ]
            },
            {
                "type": "VerticalLayout",
                "props": {
                    "spaceEvenly": False
                },
                "elements": list(lists_ui.values())
            }
        ]
    }
        
    form_schema = {
        "type": "object",
        "properties": {
            "job_posting": {
                "type": "string",
                "enum": ["DEFAULT"]
            },
            "element_3711_interested": {
                "type": "string",
                "enum": [
                    "✓",
                    "?",
                    "𐄂"
                ]
            },
            "element_3712_interested": {
                "type": "string",
                "enum": [
                    "✓",
                    "?",
                    "𐄂"
                ]
            },
            "element_3713_interested": {
                "type": "string",
                "enum": [
                    "✓",
                    "?",
                    "𐄂"
                ]
            },
            "element_3711": {
                "type": "boolean"
            },
            "element_3712": {
                "type": "boolean"
            },
            "element_3713": {
                "type": "boolean"
            }
        }
    }

    ### build form schema
    #job_postings
    
    if len (job_postings) > 0:
        form_schema['properties']['job_posting']['enum'] = []
        for job_posting in job_postings:
            logging.info(job_posting)
            form_schema['properties']['job_posting']['enum'].append(job_posting['job_posting_title'] + ', ' + job_posting['job_posting_company'] + " [#" + str(job_posting['job_posting_id']) + "]" )

    ## data element
    form_data = {}

    form = {
        "schema": form_schema,
        "data": form_data,
        "uischema": form_ui
    }

    return form





            # {
            #     "type": "Group",
            #     "label": "Interviewed",
            #     "props": {
            #         "collapsible": True,
            #         "defaultIsOpen": True,
            #         "compact": False,
            #         "style": {
            #             "width": 800
            #         }
            #     },
            #     "elements": [
            #         {
            #             "type": "VerticalLayout",
            #             "elements": [
            #                 {
            #                     "type": "VerticalLayout",
            #                     "props": {
            #                         "style": {
            #                             "backgroundColor": "red"
            #                         }
            #                     },
            #                     "elements": [

                                    
            #                         {
            #                             "type": "HorizontalLayout",
            #                             "elements": [
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Control",
            #                                             "label": "Candidate 3711",
            #                                             "scope": "#/properties/element_3711",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 14,
            #                                                     "fontWeight": "bold"
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Technical Manager, CISCO",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "✓ Pytorch",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "✓ Machine Learning",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "𐄂 C++",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "✓ LLMs",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Button",
            #                                             "label": "View",
            #                                             "props": {
            #                                                 "action": "VIEW_JOB_SEEKER_3711",
            #                                                 "large": False,
            #                                                 "style": {
            #                                                     "width": 100,
            #                                                     "fontWeight": "bold",
            #                                                     "marginBottom": 5
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": " ",
            #                                             "props": {
            #                                                 "muted": True,
            #                                                 "style": {
            #                                                     "marginBottom": 10,
            #                                                     "width": 200,
            #                                                     "fontStyle": "italic"
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "Control",
            #                                     "scope": "#/properties/element_3711_interested",
            #                                     "props": {
            #                                         "style": {
            #                                             "width": 200,
            #                                             "fontWeight": "bold",
            #                                             "marginLeft": 20
            #                                         }
            #                                     }
            #                                 }
            #                             ],
            #                             "props": {
            #                                 "spaceEvenly": False
            #                             }
            #                         },
                                    
            #                         {
            #                             "type": "HorizontalLayout",
            #                             "elements": [
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Control",
            #                                             "label": "Candidate 3712",
            #                                             "scope": "#/properties/element_3712",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 14,
            #                                                     "fontWeight": "bold"
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Data Scientist III, Google",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "SciKit Learn",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Pytorch",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Clustering",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Algorithm Design",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Deep Learning",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Button",
            #                                             "label": "View",
            #                                             "props": {
            #                                                 "action": "VIEW_JOB_SEEKER_3712",
            #                                                 "large": False,
            #                                                 "style": {
            #                                                     "width": 100,
            #                                                     "fontWeight": "bold",
            #                                                     "marginBottom": 5
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": " ",
            #                                             "props": {
            #                                                 "muted": True,
            #                                                 "style": {
            #                                                     "marginBottom": 10,
            #                                                     "width": 200,
            #                                                     "fontStyle": "italic"
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "Control",
            #                                     "scope": "#/properties/element_3712_interested",
            #                                     "props": {
            #                                         "style": {
            #                                             "width": 200,
            #                                             "fontWeight": "bold",
            #                                             "marginLeft": 20
            #                                         }
            #                                     }
            #                                 }
            #                             ],
            #                             "props": {
            #                                 "spaceEvenly": False
            #                             }
            #                         },
            #                         {
            #                             "type": "Label",
            #                             "label": "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄",
            #                             "props": {
            #                                 "muted": True,
            #                                 "style": {
            #                                     "marginBottom": 10,
            #                                     "fontStyle": "italic"
            #                                 }
            #                             }
            #                         },
            #                         {
            #                             "type": "HorizontalLayout",
            #                             "elements": [
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Control",
            #                                             "label": "Candidate 3713",
            #                                             "scope": "#/properties/element_3713",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 14,
            #                                                     "fontWeight": "bold"
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Staff Research Scientist, DeepMind",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12,
            #                                                     "whiteSpace": "nowrap",
            #                                                     "overflow": "hidden",
            #                                                     "textOverflow": "ellipsis",
            #                                                     "maxWidth": 200
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Pytorch",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Model Training",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "LLM Architecture",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": "Finetuning",
            #                                             "props": {
            #                                                 "style": {
            #                                                     "width": 200,
            #                                                     "fontSize": 12
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "VerticalLayout",
            #                                     "elements": [
            #                                         {
            #                                             "type": "Button",
            #                                             "label": "View",
            #                                             "props": {
            #                                                 "action": "VIEW_JOB_SEEKER_3713",
            #                                                 "large": False,
            #                                                 "style": {
            #                                                     "width": 100,
            #                                                     "fontWeight": "bold",
            #                                                     "marginBottom": 5
            #                                                 }
            #                                             }
            #                                         },
            #                                         {
            #                                             "type": "Label",
            #                                             "label": " ",
            #                                             "props": {
            #                                                 "muted": True,
            #                                                 "style": {
            #                                                     "marginBottom": 10,
            #                                                     "width": 200,
            #                                                     "fontStyle": "italic"
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 },
            #                                 {
            #                                     "type": "Control",
            #                                     "scope": "#/properties/element_3713_interested",
            #                                     "props": {
            #                                         "style": {
            #                                             "width": 200,
            #                                             "fontWeight": "bold",
            #                                             "marginLeft": 20
            #                                         }
            #                                     }
            #                                 }
            #                             ],
            #                             "props": {
            #                                 "spaceEvenly": False
            #                             }
            #                         }
            #                     ]
            #                 },
            #                 {
            #                     "type": "Label",
            #                     "label": " ",
            #                     "props": {
            #                         "muted": True,
            #                         "style": {
            #                             "marginBottom": 10,
            #                             "fontStyle": "italic"
            #                         }
            #                     }
            #                 },
            #                 {
            #                     "type": "Label",
            #                     "label": "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            #                     "props": {
            #                         "muted": True,
            #                         "style": {
            #                             "marginBottom": 10,
            #                             "fontStyle": "italic"
            #                         }
            #                     }
            #                 },
            #                 {
            #                     "type": "HorizontalLayout",
            #                     "elements": [
            #                         {
            #                             "type": "Button",
            #                             "label": "Compare",
            #                             "props": {
            #                                 "action": "COMPARE",
            #                                 "large": False
            #                             }
            #                         },
            #                         {
            #                             "type": "Button",
            #                             "label": "Summarize",
            #                             "props": {
            #                                 "action": "SUMMARIZE",
            #                                 "large": False
            #                             }
            #                         }
            #                     ],
            #                     "props": {
            #                         "spaceEvenly": False
            #                     }
            #                 },
            #                 {
            #                     "type": "Label",
            #                     "label": " ",
            #                     "props": {
            #                         "muted": True,
            #                         "style": {
            #                             "marginBottom": 5,
            #                             "fontStyle": "italic"
            #                         }
            #                     }
            #                 }
            #             ]
            #         }
            #     ]
            # }