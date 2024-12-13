
import logging

###### Parsers, Formats, Utils
import json
from string import Template
import copy


def get_cluster_action_ui(action, cluster_id):
   return {
        "type": "Button",
        "label": action['label'],
        "props": {
            "action": action['name']+'_CLUSTER_'+cluster_id,
            "large": False
        }
    }

def get_cluster_summary_ui(id, count, label, description, actions=None):

    if actions is None:
        actions = []

    cluster_actions = []
    for action in actions:
        cluster_actions.append(get_cluster_action_ui(action, id))
    
    ### ui 
    form_ui = {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Markdown",
                "scope": "#/properties/summary"
            },
            { 
                "type": "HorizontalLayout",
                "elements": cluster_actions
            }
        ]
    }

    ### schema
    form_schema = {
        "type": "object",
        "properties": {
        }
    }

    ### data
    summary_markdown = "### " + label + " (" + str(count) + ") "
    summary_markdown += "\n"
    summary_markdown += description

    form_data = { 
        "summary": summary_markdown
    }

    form = {
        "schema": form_schema,
        "data": form_data,
        "uischema": form_ui
    }

    return form

def get_list_action_ui(action, list_id, list_code):
   return {
        "type": "Button",
        "label": action['label'],
        "props": {
            "action": action['name']+'_LIST_'+list_code,
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

def get_separator(separator='┄', length=52, margin=10):
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

def get_column_ui(row, header, actions=None):
    if actions is None:
        actions =  [{"name":"VIEW", "label":"View"}]

    if header == 'Candidate':
        jst = row['job_seeker_title']

        if jst is None:
            jst = "Unknown"
        jsc = row['job_seeker_company']
        if jsc is None:
            jsc = "Unknown"

        return {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Control",
                    "label": "Candidate " + str(row['job_seeker_id']),
                    "scope": "#/properties/" + "CHECK" + "_JOB_SEEKER_" + str(row['job_seeker_id']),
                    "props": {
                        "style": {
                            "width": 200,
                            "fontSize": 14,
                            "fontWeight": "bold"
                        }
                    }
                },
                {
                    "type": "Label",
                    "label": jst + ", " + jsc,
                    "props": {
                        "style": {
                            "width": 200,
                            "fontSize": 12
                        }
                    }
                }
            ]
        }
    elif header == 'Matches':
        match_elements = []
        for skill in row['skills']:
            job_posting_skill = skill["job_posting_skill"]
            job_seeker_has_skill = skill["job_seeker_has_skill"]
            job_posting_must_have_skill = skill["job_posting_must_have_skill"]

            label = job_posting_skill
            font_weight = 400
            if not job_seeker_has_skill and job_posting_must_have_skill:
                label = "𐄂 " + label
                font_weight = 200
            if job_seeker_has_skill and job_posting_must_have_skill:
                label = "✓ " + label
                font_weight = 600

            match_elements.append({
                "type": "Label",
                "label": label,
                "props": {
                    "style": {
                        "width": 200,
                        "fontSize": 12,
                        "fontWeight": font_weight
                    }
                }
            })

        return  {
            "type": "VerticalLayout",
            "elements": match_elements
        }
    elif header == 'Actions':
        action_elements = []
        for action in actions:
            action_elements.append({
                "type": "Button",
                "label": action['label'],
                "props": {
                    "action": action['name'] + "_JOB_SEEKER_" + str(row['job_seeker_id']),
                    "large": False,
                    "style": {
                        "width": 100,
                        "fontWeight": "bold",
                        "marginBottom": 15
                    }
                }
            })

        action_elements.append({
            "type": "Label",
            "label": " ",
            "props": {
                "style": {
                    "width": 200,
                    "fontSize": 12
                }
            }
        })
        
        return  {
            "type": "VerticalLayout",
            "elements": action_elements,
        }
    
    elif header == 'Interested?':
        return  {
            "type": "Control",
            "scope": "#/properties/" + "INTEREST" + "_JOB_SEEKER_" + str(row['job_seeker_id']),
            "props": {
                "style": {
                    "width": 200,
                    "fontWeight": "bold",
                    "marginLeft": 20
                }
            }
        }
    else:
        return  {
        "type": "VerticalLayout",
        "elements": []
    }
    
def get_row_ui(row, headers=None, actions=None):
    if headers == None:
        headers = ["Candidate", "Matches", "Actions", "Interested?"]

    column_uis = []
    for header in headers:
        column_uis.append(get_column_ui(row, header, actions=actions))

    return  {
        "type": "VerticalLayout",
        "elements": [
            {
            "type": "HorizontalLayout",
            "elements": column_uis
            },
            {
                "type": "Label",
                "label": " ",
                "props": {
                    "muted": True,
                    "style": {
                        "marginBottom": 10,
                        "fontStyle": "italic"
                    }
                }
            }
        ]
    }

def process_data(data):
    by_job_seeker = {}

    by_list = {}

    if 'job_posting_job_seeker_last_experience' in data:
        job_posting_job_seeker_last_experience = data['job_posting_job_seeker_last_experience']
        for e in job_posting_job_seeker_last_experience:
            job_seeker_id = e['job_seeker_id']
            job_seeker_title = e['job_seeker_title']
            job_seeker_company = e['job_seeker_company']

            job_seeker_data = {}
            by_job_seeker[job_seeker_id] = job_seeker_data
            job_seeker_data['job_seeker_id'] = job_seeker_id
            job_seeker_data['job_seeker_title'] = job_seeker_title
            job_seeker_data['job_seeker_company'] = job_seeker_company
            job_seeker_data['skills'] = []

    if 'matched_job_posting_seeker_skills' in data:
            matched_job_posting_seeker_skills = data['matched_job_posting_seeker_skills']
            for ms in matched_job_posting_seeker_skills:
                job_posting_id = ms['job_posting_id']
                job_seeker_id = ms['job_seeker_id']
                job_posting_skill = ms['job_posting_skill']
                job_seeker_has_skill = ms['job_seeker_has_skill']
                job_posting_must_have_skill = ms['job_posting_must_have_skill']

                if job_seeker_id in by_job_seeker:
                    job_seeker_data = by_job_seeker[job_seeker_id]
                else:
                    job_seeker_data = {}
                    by_job_seeker[job_seeker_id] = job_seeker_data
                    job_seeker_data['job_seeker_id'] = job_seeker_id
                    job_seeker_data['job_seeker_title'] = "unknown"
                    job_seeker_data['job_seeker_company'] = "unknown"
                    job_seeker_data['skills'] = []
                    
                s = job_seeker_data['skills']
                sd = {}
                sd["job_posting_skill"] = job_posting_skill
                sd["job_seeker_has_skill"] = job_seeker_has_skill
                sd["job_posting_must_have_skill"] = job_posting_must_have_skill
                s.append(sd)

    if 'job_posting_job_seeker_lists' in data:
        job_posting_job_seeker_lists = data['job_posting_job_seeker_lists']
        for j in job_posting_job_seeker_lists:
            job_posting_id = j['job_posting_id']
            job_seeker_id = j ['job_seeker_id']
            list_id = j['list_id']

            if list_id in by_list:
                l = by_list[list_id]
            else:
                l = {}
                by_list[list_id] = l


            if job_seeker_id in by_job_seeker:
                job_seeker_data = by_job_seeker[job_seeker_id]
            else:
                job_seeker_data = {}
                by_job_seeker[job_seeker_id] = job_seeker_data
                job_seeker_data['job_seeker_title'] = "unknown"
                job_seeker_data['job_seeker_company'] = "unknown"
                job_seeker_data['skills'] = []

            l[job_seeker_id] = copy.deepcopy(job_seeker_data)

    # process "all" from experience list
    if 'job_posting_job_seeker_last_experience' in data:
        job_posting_job_seeker_last_experience = data['job_posting_job_seeker_last_experience']
        for e in job_posting_job_seeker_last_experience:
            job_seeker_id = e['job_seeker_id']

            # all
            list_id = 0
            if list_id in by_list:
                l = by_list[list_id]
            else:
                l = {}
                by_list[list_id] = l

            if job_seeker_id in l:
                continue

            if job_seeker_id in by_job_seeker:
                job_seeker_data = by_job_seeker[job_seeker_id]
                l[job_seeker_id] = copy.deepcopy(job_seeker_data)

    return by_list
    

def build_ats_form(selected_job_posting_id, job_postings, lists, data, list_actions=None, job_seeker_actions=None, page=0, page_size=10):
    
    if type(selected_job_posting_id) == str:
        selected_job_posting_id = int(selected_job_posting_id)

    by_list = process_data(data)
    # print(json.dumps(by_list, indent=3))

    all_list_contents = {}
    ## lists
    lists_uis = []
    lists_labels = []

    list_id_by_code = {}
    for l in lists:
        list_contents = []
        list_id_by_code[l['list_code']] = l['list_id']
        all_list_contents[l['list_id']] = list_contents


    form_data = {}

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
                            "action": "VIEW_JD_" + str(selected_job_posting_id),
                            "large": False
                        }
                    }
                ]
            },
            {
                "type": "Tabs",
                "scope": "#/properties/LIST_ID",
                "tabs": lists_labels,
                "elements": lists_uis
            }
        ]
    }
        
    interested_enums = ["✓","?","𐄂"]
    interested_enums_by_list_code = {"interested": "✓", "undecided": "?", "rejected": "𐄂"}

   
    form_schema = {
        "type": "object",
        "properties": {
            "job_posting": {
                "type": "string",
                "enum": ["DEFAULT"]
            }
        }
    }

    ### build form schema
    #job_postings
    selected_job_posting_label = None
    if len (job_postings) > 0:
        form_schema['properties']['job_posting']['enum'] = []
        for job_posting in job_postings:
            job_posting_label = job_posting['job_posting_title'] + ', ' + job_posting['job_posting_company'] + " [#" + str(job_posting['job_posting_id']) + "]" 
            form_schema['properties']['job_posting']['enum'].append(job_posting_label)
            if job_posting['job_posting_id'] == selected_job_posting_id:
                selected_job_posting_label = job_posting_label

        for list_id in by_list:
            list_contents = all_list_contents[list_id]

            list = by_list[list_id]
            rows = list.values()

            # ui
            job_seekers_page_set = set()

            i = 0 
            for row in rows:
                if 'job_seeker_id' not in row:
                    continue 
                # filter by page
                if i < page * page_size:
                    i = i + 1
                    continue
                if i >= ( page + 1 ) * page_size:
                    break
                job_seeker_id = row['job_seeker_id']
                job_seekers_page_set.add(job_seeker_id)
                list_contents.append(get_row_ui(row, actions=job_seeker_actions))
                i = i + 1

                # properties
                if job_seeker_id in job_seekers_page_set:

                    form_schema['properties']["CHECK" + "_JOB_SEEKER_" + str(job_seeker_id)] = { "type": "boolean" }
                    form_schema['properties']["INTEREST" + "_JOB_SEEKER_" + str(job_seeker_id)] = { "type": "string", "enum": copy.deepcopy(interested_enums) }

                    # update interested status
                    if list_id == list_id_by_code['interested']:
                        form_data["INTEREST" + "_JOB_SEEKER_" + str(job_seeker_id)] = interested_enums_by_list_code['interested']
                    elif list_id == list_id_by_code['undecided']:
                        form_data["INTEREST" + "_JOB_SEEKER_" + str(job_seeker_id)] = interested_enums_by_list_code['undecided']
                    elif list_id == list_id_by_code['rejected']:
                        form_data["INTEREST" + "_JOB_SEEKER_" + str(job_seeker_id)] = interested_enums_by_list_code['rejected']
                


    for l in lists:
        list_id = l['list_id']
        if list_id not in by_list:
            continue
        list_contents = all_list_contents[list_id]
        lists_labels.append(l['list_name'] + " [" + str(len(by_list[list_id].values())) + "]")
        lists_uis.append(get_list_ui(l['list_id'], l['list_code'], l['list_name'], list_contents, actions=list_actions))

   
    ### data element
    if selected_job_posting_label:
        form_data["job_posting"] = selected_job_posting_label
        
    ### selected tab
    selected_list_id = None
    if selected_list_id is None:
        selected_list_id = 1

    form_data["LIST_ID"] = selected_list_id
        
    form = {
        "schema": form_schema,
        "data": form_data,
        "uischema": form_ui
    }

    return form



