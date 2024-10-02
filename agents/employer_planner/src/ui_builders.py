import json

def build_list_viz():
    viz_ui = { 
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Vega",
                "scope": "#/properties/vis"
            }
        ]
    }

    viz_schema = {
        "type": "object",
        "properties": {
            "vis": {
               "vl-spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "description": "candidate ranking table",
                    "width": "container",
                    "title": {
                        "text": ["Overall Ranking of Candidates:", "Top-20"],
                        "align": "center",
                        "dy": -10,
                        "fontWeight": "bold",
                        "color": "#4F597A",
                        "fontSize": 13,
                        "font": "Montserrat,sans-serif"
                    },
                    "config": {"axis": {"grid": True, "tickBand": "extent"}},
                    "data": {
                        "values": [
                            {"job_seeker_id":"Candidate1","Overall_Score":1.26131699577619, "Experience_Score":1, "Must_Have_Score":0.285714285714285},
                            {"job_seeker_id":"Candidate2","Overall_Score":1.07679430536457, "Experience_Score":1, "Must_Have_Score":0.5},
                            {"job_seeker_id":"Candidate3","Overall_Score":0.984472292227462, "Experience_Score":1, "Must_Have_Score":0.5},
                            {"job_seeker_id":"Candidate4","Overall_Score":0.975357541397898, "Experience_Score":1, "Must_Have_Score":0.5},
                            {"job_seeker_id":"Candidate5","Overall_Score":0.809060094596622, "Experience_Score":1, "Must_Have_Score":0.285714285714285},
                            {"job_seeker_id":"Candidate6","Overall_Score":0.726512483842964, "Experience_Score":1, "Must_Have_Score":0.285714285714285},
                            {"job_seeker_id":"Candidate7","Overall_Score":0.701245858829762, "Experience_Score":1, "Must_Have_Score":0.214285714285714},
                            {"job_seeker_id":"Candidate8","Overall_Score":0.679647326628337, "Experience_Score":1, "Must_Have_Score":0.5},
                            {"job_seeker_id":"Candidate9","Overall_Score":0.679326954961354, "Experience_Score":1, "Must_Have_Score":0.214285714285714},
                            {"job_seeker_id":"Candidate10","Overall_Score":0.675973774052811, "Experience_Score":1, "Must_Have_Score":0.285714285714285},
                            {"job_seeker_id":"Candidate11","Overall_Score":0.668109009444329, "Experience_Score":1, "Must_Have_Score":0.357142857142857},
                            {"job_seeker_id":"Candidate12","Overall_Score":0.668061460079778, "Experience_Score":1, "Must_Have_Score":0.428571428571428},
                            {"job_seeker_id":"Candidate13","Overall_Score":0.661292617616242, "Experience_Score":1, "Must_Have_Score":0.357142857142857},
                            {"job_seeker_id":"Candidate14","Overall_Score":0.614455274130432, "Experience_Score":0.875, "Must_Have_Score":0.428571428571428},
                            {"job_seeker_id":"Candidate15","Overall_Score":0.613492476327006, "Experience_Score":0.875, "Must_Have_Score":0.428571428571428},
                            {"job_seeker_id":"Candidate16","Overall_Score":0.609042067996767, "Experience_Score":0.875, "Must_Have_Score":0.285714285714285},
                            {"job_seeker_id":"Candidate17","Overall_Score":0.595054232542885, "Experience_Score":0.875, "Must_Have_Score":0.642857142857142},
                            {"job_seeker_id":"Candidate18","Overall_Score":0.595054232542885, "Experience_Score":0.875, "Must_Have_Score":0.428571428571428},
                            {"job_seeker_id":"Candidate19","Overall_Score":0.595006683178334, "Experience_Score":0.75, "Must_Have_Score":0.428571428571428},
                            {"job_seeker_id":"Candidate20","Overall_Score":0.571112446251456, "Experience_Score":1, "Must_Have_Score":0.5}
                                ]
                    },
                    "transform": [
                        {"calculate": "datum.Overall_Score", "as": "Overall Score"},
                        {"calculate": "datum.Experience_Score", "as": "Experience Score"},
                        {"calculate": "datum.Must_Have_Score", "as": "Must Have Score"},
                        {"fold": ["Overall_Score", "Experience_Score", "Must_Have_Score"], "as": ["Title", "Value"]}
                    ],
                    "mark": "text",
                    "encoding": {
                        "x": {
                        "field": "Title",
                        "type": "nominal",
                        "sort": "descending",
                        "axis": {
                            "title": None,
                            "labelAngle": 0,
                            "labelFontWeight": "bold",
                            "labelColor": "#303854",
                            "labelFontSize": 10,
                            "labelPadding": 5,
                            "orient": "top"
                        }
                        },
                        "y": {
                        "field": "job_seeker_id",
                        "type": "nominal",
                        "sort": {
                            "field": "Overall Score",
                            "type": "quantitative",
                            "order": "descending"
                        },
                        "axis": {
                            "title": None,
                            "labelAngle": 0,
                            "labelFontWeight": "bold",
                            "labelColor": "#4F597A",
                            "labelFontSize": 10,
                            "labelPadding": 5
                        }
                        }
                    },
                    "layer": [
                        {
                        "mark": "rect",
                        "width": 400,
                        "encoding": {
                            "color": {
                            "legend": None,
                            "field": "Value",
                            "type": "quantitative",
                            "condition": [
                                {
                                "test": "datum.Title == 'Overall Score'",
                                "type": "quantitative",
                                "value": "datum.Value"
                                },
                                {
                                "test": "datum.Title == 'Overall Score'",
                                "type": "quantitative",
                                "value": "datum.Value"
                                },
                                {
                                "test": "datum.Title == 'Overall Score'",
                                "type": "quantitative",
                                "value": "datum.Value"
                                }
                            ]
                            }
                        }
                        },
                        {
                        "mark": {
                            "type": "text",
                            "fontSize": 8,
                            "font": "Montserrat,sans-serif",
                            "align": "center"
                        },
                        "encoding": {"text": {"field": "Value"}}
                        }
                    ]
                    }
            }
        }
    }

    viz = {
        "schema": viz_schema,
        "uischema": viz_ui,
    }

    return viz



def build_ed_viz():
    viz_ui = { 
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Vega",
                "scope": "#/properties/vis"
            }
        ]
    }

    viz_schema = {
        "type": "object",
        "properties": {
            "vis": {
               "vl-spec": {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "title": {
                        "text": ["All Applies", "Distribution by Highest Education"],
                        "frame": "group"
                    },
                    "data": {
                        "values": [
                        {"category": "BSc.", "value": 14},
                        {"category": "MSc.", "value": 6},
                        {"category": "PhD.", "value": 2},
                        {"category": "GED", "value": 3}
                        ]
                    },
                    "mark": {"type": "arc", "innerRadius": 50},
                    "encoding": {
                        "theta": {"field": "value", "type": "quantitative"},
                        "color": {"field": "category", "type": "nominal"}
                    }
                }
            }
        }
    }

    viz = {
        "schema": viz_schema,
        "uischema": viz_ui,
    }

    return viz

def build_skill_viz():
    viz_ui = { 
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Vega",
                "scope": "#/properties/vis"
            }
        ]
    }

    viz_schema = {
        "type": "object",
        "properties": {
            "vis": {
               "vl-spec": {
                     "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "data":  
                            {
                            "values": [{"duration":27,"skill":"Python"},
                                {"duration":48.86667,"skill":"Python"},
                                {"duration":27.43334,"skill":"Python"},
                                {"duration":39.93333,"skill":"Python"},
                                {"duration":32.96667,"skill":"Python"},
                                {"duration":28.96667,"skill":"Python"},
                                {"duration":43.06666,"skill":"Java"},
                                {"duration":55.2,"skill":"Java"},
                                {"duration":28.76667,"skill":"Java"},
                                {"duration":38.13333,"skill":"Java"},
                                {"duration":29.13333,"skill":"Java"},
                                {"duration":29.66667,"skill":"Java"},
                                {"duration":35.13333,"skill":"C++"},
                                {"duration":47.33333,"skill":"C++"},
                                {"duration":25.76667,"skill":"C++"},
                                {"duration":40.46667,"skill":"C++"},
                                {"duration":29.66667,"skill":"C++"},
                                {"duration":25.7,"skill":"C++"},
                                {"duration":39.9,"skill":"Ruby"},
                                {"duration":50.23333,"skill":"Ruby"},
                                {"duration":26.13333,"skill":"Ruby"},
                                {"duration":41.33333,"skill":"Ruby"},
                                {"duration":23.03333,"skill":"Ruby"},
                                {"duration":26.3,"skill":"Ruby"},
                                {"duration":36.56666,"skill":"Perl"},
                                {"duration":63.8333,"skill":"Perl"},
                                {"duration":43.76667,"skill":"Perl"},
                                {"duration":46.93333,"skill":"Perl"},
                                {"duration":29.76667,"skill":"Perl"},
                                {"duration":33.93333,"skill":"Perl"},
                                {"duration":43.26667,"skill":"Rust"},
                                {"duration":58.1,"skill":"Rust"},
                                {"duration":28.7,"skill":"Rust"},
                                {"duration":45.66667,"skill":"Rust"},
                                {"duration":32.16667,"skill":"Rust"},
                                {"duration":33.6,"skill":"Rust"},
                                {"duration":36.6,"skill":"Go"},
                                {"duration":65.7667,"skill":"Go"},
                                {"duration":30.36667,"skill":"Go"},
                                {"duration":48.56666,"skill":"Go"},
                                {"duration":24.93334,"skill":"Go"},
                                {"duration":28.1,"skill":"Go"},
                                {"duration":32.76667,"skill":"Javascript"},
                                {"duration":48.56666,"skill":"Javascript"},
                                {"duration":29.86667,"skill":"Javascript"},
                                {"duration":41.6,"skill":"Javascript"},
                                {"duration":34.7,"skill":"Javascript"},
                                {"duration":32,"skill":"Javascript"},
                                {"duration":24.66667,"skill":"Swift"},
                                {"duration":46.76667,"skill":"Swift"},
                                {"duration":22.6,"skill":"Swift"},
                                {"duration":44.1,"skill":"Swift"},
                                {"duration":19.7,"skill":"Swift"},
                                {"duration":33.06666,"skill":"Swift"},
                                {"duration":39.3,"skill":"PHP"},
                                {"duration":58.8,"skill":"PHP"},
                                {"duration":29.46667,"skill":"PHP"},
                                {"duration":49.86667,"skill":"PHP"},
                                {"duration":34.46667,"skill":"PHP"},
                                {"duration":31.6,"skill":"PHP"},
                                {"duration":26.9,"skill":"Python","year":1932},
                                {"duration":33.46667,"skill":"Python","year":1932},
                                {"duration":34.36666,"skill":"Python","year":1932},
                                {"duration":32.96667,"skill":"Python","year":1932},
                                {"duration":22.13333,"skill":"Python","year":1932},
                                {"duration":22.56667,"skill":"Python","year":1932},
                                {"duration":36.8,"skill":"Java","year":1932},
                                {"duration":37.73333,"skill":"Java","year":1932},
                                {"duration":35.13333,"skill":"Java","year":1932},
                                {"duration":26.16667,"skill":"Java","year":1932},
                                {"duration":14.43333,"skill":"Java","year":1932},
                                {"duration":25.86667,"skill":"Java","year":1932},
                                {"duration":27.43334,"skill":"C++","year":1932},
                                {"duration":38.5,"skill":"C++","year":1932},
                                {"duration":35.03333,"skill":"C++","year":1932},
                                {"duration":20.63333,"skill":"C++","year":1932},
                                {"duration":16.63333,"skill":"C++","year":1932},
                                {"duration":22.23333,"skill":"C++","year":1932},
                                {"duration":26.8,"skill":"Ruby","year":1932},
                                {"duration":37.4,"skill":"Ruby","year":1932},
                                {"duration":38.83333,"skill":"Ruby","year":1932},
                                {"duration":32.06666,"skill":"Ruby","year":1932},
                                {"duration":32.23333,"skill":"Ruby","year":1932},
                                {"duration":22.46667,"skill":"Ruby","year":1932},
                                {"duration":29.06667,"skill":"Perl","year":1932},
                                {"duration":49.2333,"skill":"Perl","year":1932},
                                {"duration":46.63333,"skill":"Perl","year":1932},
                                {"duration":41.83333,"skill":"Perl","year":1932},
                                {"duration":20.63333,"skill":"Perl","year":1932},
                                {"duration":30.6,"skill":"Perl","year":1932},
                                {"duration":26.43334,"skill":"Rust","year":1932},
                                {"duration":42.2,"skill":"Rust","year":1932},
                                {"duration":43.53334,"skill":"Rust","year":1932},
                                {"duration":34.33333,"skill":"Rust","year":1932},
                                {"duration":19.46667,"skill":"Rust","year":1932},
                                {"duration":22.7,"skill":"Rust","year":1932},
                                {"duration":25.56667,"skill":"Go","year":1932},
                                {"duration":44.7,"skill":"Go","year":1932},
                                {"duration":47,"skill":"Go","year":1932},
                                {"duration":30.53333,"skill":"Go","year":1932},
                                {"duration":19.9,"skill":"Go","year":1932},
                                {"duration":22.5,"skill":"Go","year":1932},
                                {"duration":28.06667,"skill":"Javascript","year":1932},
                                {"duration":36.03333,"skill":"Javascript","year":1932},
                                {"duration":43.2,"skill":"Javascript","year":1932},
                                {"duration":25.23333,"skill":"Javascript","year":1932},
                                {"duration":26.76667,"skill":"Javascript","year":1932},
                                {"duration":31.36667,"skill":"Javascript","year":1932},
                                {"duration":30,"skill":"Swift","year":1932},
                                {"duration":41.26667,"skill":"Swift","year":1932},
                                {"duration":44.23333,"skill":"Swift","year":1932},
                                {"duration":32.13333,"skill":"Swift","year":1932},
                                {"duration":15.23333,"skill":"Swift","year":1932},
                                {"duration":27.36667,"skill":"Swift","year":1932},
                                {"duration":38,"skill":"PHP","year":1932},
                                {"duration":58.16667,"skill":"PHP","year":1932},
                                {"duration":47.16667,"skill":"PHP","year":1932},
                                {"duration":35.9,"skill":"PHP","year":1932},
                                {"duration":20.66667,"skill":"PHP","year":1932},
                                {"duration":29.33333,"skill":"PHP","year":1932}]
                            },
                        "encoding": {"y": {"field": "skill", "type": "ordinal"}},
                         "title": {
                            "text": ["All Applies", "Skill Duration Ranges (Min/Max)"],
                            "frame": "group"
                        },
                        "layer": [
                            {
                            "mark": {"type": "point", "filled": True},
                            "encoding": {
                                "x": {
                                "aggregate": "mean",
                                "field": "duration",
                                "type": "quantitative",
                                "scale": {"zero": False},
                                "title": "Duration"
                                },
                                "color": {"value": "black"}
                            }
                            },
                            {
                            "mark": {"type": "errorbar", "extent": "ci"},
                            "encoding": {
                                "x": {"field": "duration", "type": "quantitative", "title": ""}
                            }
                            }
                        ]
               }
            }
        }
    }

    viz = {
        "schema": viz_schema,
        "uischema": viz_ui,
    }

    return viz

def build_form():
    form_ui = {
        "type": "VerticalLayout",
        "elements": [
            {
                "type": "Label",
                "label": "Employer Assistant",
                "props": {
                    "style": {
                        "fontWeight": "bold"
                    }
                }
            },
            {
                "type": "Label",
                "label": "Below are your posted JDs. Select a JD to continue...",
                "props": {
                    "muted": True,
                    "style": {
                        "marginBottom": 15,
                        "fontStyle": "italic"
                    }
                }
            },
            {
                "type": "VerticalLayout",
                "elements": [
                    {
                        "type": "Control",
                        "scope": "#/properties/JOB_ID"
                    }
                ]
            },
            {
                "type": "Label",
                "label": "Select an action from below to examine applicants...",
                "props": {
                    "muted": True,
                    "style": {
                        "marginBottom": 15,
                        "fontStyle": "italic"
                    }
                }
            },
            {
                "type": "HorizontalLayout",
                "elements": [
                    {
                        "type": "VerticalLayout",
                        "elements": [
                            {
                                "type": "Button",
                                "label": "Summary",
                                "props": {
                                    "action": "SUMMARIZE",
                                    "large": False
                                }
                            },
                            {
                                "type": "Label",
                                "label": "",
                                "props": {
                                    "muted": True,
                                    "style": {
                                        "marginBottom": 5,
                                        "fontStyle": "italic"
                                    }
                                }
                            },
                            {
                                "type": "Button",
                                "label": "Recent Applies",
                                "props": {
                                    "action": "RECENT",
                                    "large": False
                                }
                            },
                            {
                                "type": "Label",
                                "label": "",
                                "props": {
                                    "muted": True,
                                    "style": {
                                        "marginBottom": 5,
                                        "fontStyle": "italic"
                                    }
                                }
                            },
                            {
                                "type": "Button",
                                "label": "Top Applies",
                                "props": {
                                    "action": "TOP",
                                    "large": False
                                }
                            }
                        ]
                    },
                    {
                        "type": "VerticalLayout",
                        "elements": [
                          
                            {
                                "type": "Button",
                                "label": "Short List",
                                "props": {
                                    "action": "SHORTLIST",
                                    "large": False
                                }
                            },
                            {
                                "type": "Label",
                                "label": "",
                                "props": {
                                    "muted": True,
                                    "style": {
                                        "marginBottom": 5,
                                        "fontStyle": "italic"
                                    }
                                }
                            },
                            {
                                "type": "Button",
                                "label": "Compare",
                                "props": {
                                    "action": "COMPARE",
                                    "large": False
                                }
                            },
                            {
                                "type": "Label",
                                "label": "",
                                "props": {
                                    "muted": True,
                                    "style": {
                                        "marginBottom": 5,
                                        "fontStyle": "italic"
                                    }
                                }
                            },
                            {
                                "type": "Button",
                                "label": "Skills Distribution",
                                "props": {
                                    "action": "SKILLS",
                                    "large": False
                                }
                            },
                            {
                                "type": "Label",
                                "label": "",
                                "props": {
                                    "muted": True,
                                    "style": {
                                        "marginBottom": 5,
                                        "fontStyle": "italic"
                                    }
                                }
                            },
                            {
                                "type": "Button",
                                "label": "Smart Queries",
                                "props": {
                                    "action": "SMARTQUERIES",
                                    "large": False
                                }
                            }
                        ]
                    }
                ]
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
            },
            {
                "type": "Button",
                "label": "Done",
                "props": {
                    "intent": "success",
                    "action": "DONE",
                    "large": True
                }
            }
        ]
    }
    
    form_schema = {
        "type": "object",
        "properties": {
            "JOB_ID": {
                "type": "string",
                "enum": [
                    "2001",
                    "2002"
                ]
            }
        }
    }

    form = {
        "schema": form_schema,
        "data": {"JOB_ID": ""},
        "uischema": form_ui,
    }

    return form
