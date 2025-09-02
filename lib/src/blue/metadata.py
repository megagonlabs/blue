from blue.utils.service_utils import ServiceClient
import logging

class MetaData(ServiceClient):
 
    def __init__(self, platform_id=None, properties=None):
        self.platform_name = platform_id
        self.properties = properties or {}
        self.name = "metadata"
        self._initialize_properties()
        
    ###### initialization
    def _initialize_properties(self):
        if self.platform_name:
            self.properties['service_url'] = f"ws://blue_service_{self.platform_name}-openai-1:8001"
        else:
            logging.warning("platform_name is missing! Falling back to default 'blue'")
            self.properties['service_url'] = "ws://blue_service_blue-openai-1:8001"

        self.properties['openai.api'] = 'ChatCompletion'
        self.properties['openai.model'] = "gpt-4o"
        self.properties['input_json'] = "[{\"role\": \"user\"}]"
        self.properties['input_context'] = "$[0]"
        self.properties['input_context_field'] = "content"
        self.properties['input_field'] = "messages"
        self.properties['input_template'] = "${input}"
        self.properties['output_path'] = '$.choices[0].message.content'
        self.properties['openai.stream'] = False
        self.properties['openai.max_tokens'] = 300

        # prefix for service specific properties
        self.properties['service_prefix'] = 'openai'
        self.properties['output_transformations'] = [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}]
        self.properties['output_strip'] = True

        
    def build_entity_description_prompt(self, entity_obj, attributes):
        """
        Given an entity object from the data registry, prepare a structured
        prompt for an LLM to generate a human-readable description of the entity
        and its attributes, in structured JSON format.
        """

        # Extract basic info
        name = entity_obj.get("name", "Unknown")
        scope = entity_obj.get("scope", "Unknown")
        etype = entity_obj.get("type", "Unknown")

        attr_lines = []

        for attr in attributes:
            attr_properties = attr.get("properties", {})
            attr_properties_info = attr_properties.get("info", {})
            attr_type = attr_properties_info.get("type", "unknown")
        
            attr_name = attr.get("name")
            attr_stats =  attr_properties.get("stats", {})
            
            sample_values = (
                attr_stats
                .get("sample_values", [])
            )

            attr_lines.append(
                f"- {attr_name} ({attr_type}), samples: {', '.join(map(str, sample_values[:3]))}"
            )

        # Build the final prompt
        prompt = f"""
        You are given a database entity definition with its attributes and metadata.
        Your task is to generate a structured JSON output with:
        1. A concise human-readable description of what this table/entity represents.
        2. Concise descriptions of each attribute.

        Entity Name: {name}
        Scope: {scope}
        Type: {etype}

        Attributes:
        {chr(10).join(attr_lines)}

        Output JSON format (do not include extra commentary, only valid JSON):

        {{
        "table_description": "string",
        "attributes": {{
            "attr_name": "description of attribute",
            ...
        }}
        }}
        """
        return prompt

    def enrich_entity(self, entity, attributes):
        entity_prompt = self.build_entity_description_prompt(entity, attributes)
        return self.execute_api_call(entity_prompt, properties=self.properties, additional_data={})
    



   