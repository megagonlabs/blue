from blue.utils.service_utils import ServiceClient
from blue.utils import json_utils
from blue.data.prompt_templates import AGGREGATION_PROMPT

import logging
import json

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
            logging.warning("platform_name is missing! Falling back to default 'default'")
            self.properties['service_url'] = "ws://blue_service_default-openai-1:8001"

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

        # Description aggregation from children
        self.properties['aggregation_prompt'] = AGGREGATION_PROMPT
        self.properties['enable_database_description_generation'] = True
        self.properties['enable_collection_description_generation'] = True


        
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

    def collect_source_metadata(self, data_registry, source, recursive=False, rebuild=False):
        # TODO
        pass

    def collect_source_database_metadata(self, data_registry, source, database, recursive=False, rebuild=False):
        collections = data_registry.get_source_database_collections(source, database)
        collection_descriptions = {}
        
        if self.properties.get('enable_database_description_generation', True):
            current_description = self.get_source_database_description(source, database)
            if not current_description or current_description.strip() == "":
                
                database_metadata = data_registry.get_source_database_property(source, database, "metadata")

                if not database_metadata:
                    database_metadata =  {
                                        "name": database,
                                            "type": "database"
                                        }

                for collection in collections:
                    collection_name = collection.get("name")
                    collection_desc = collection.get("description")
                    collection_descriptions[collection_name] = collection_desc
                    
        
                database_desc = self.enrich_database_description(database, collection_descriptions, database_metadata)
            
                data_registry.set_source_database_description(
                        source, database, database_desc, rebuild=rebuild)

        return 
 

    def collect_source_database_collection_metadata(self, data_registry, source, database, collection, recursive=False, rebuild=False):
        entities = data_registry.get_source_database_collection_entities(source, database, collection)

        entity_descriptions = {}
        for entity in entities:
            entity_name = entity.get("name")
            
            attributes = data_registry.get_source_database_collection_entity_attributes(source, database, collection, entity_name)
            
            entity_attribute_description = self.enrich_entity(entity, attributes)

            try:
                parsed = json_utils.safe_json_parse(entity_attribute_description)
                if not parsed:
                    logging.warning(f"Entity {entity} returned invalid or empty JSON.")
                    continue
            except json.JSONDecodeError:
                logging.warning("LLM did not return valid JSON. Skipping entity enrichment.")
                parsed = {}

            table_desc = parsed.get("table_description", "")
            attribute_descs = parsed.get("attributes", {})
            entity_descriptions[entity_name] = table_desc
            

            # Optionally store them back
            data_registry.set_source_database_collection_entity_description(
                source, database, collection, entity_name, table_desc, rebuild=rebuild)

            for attr, desc in attribute_descs.items():
                data_registry.set_source_database_collection_entity_attribute_description(
                    source, database, collection, entity_name, attr, desc, rebuild=rebuild)
        

        if self.properties.get('enable_collection_description_generation', True):
            current_description = data_registry.get_source_database_collection_description(source, database, collection)
            if not current_description or current_description.strip() == "":
                
                collection_metadata = data_registry.get_source_database_collection_property(source, database, collection, "metadata")
        
                if not collection_metadata:
                    collection_metadata =  {
                                    "name": collection,
                                        "type": "collection"
                                    }

                collection_desc = self.enrich_collection_description(database, entity_descriptions, collection_metadata)
        
        
                data_registry.set_source_database_collection_description(
                    source, database, collection, collection_desc, rebuild=rebuild)

    
    ###### Aggregation
    def build_collection_description_prompt(self, collection_name, entity_descriptions, collection_metadata):
        child_descriptions = [f"{name}: {desc}" for name, desc in entity_descriptions.items() if desc]
        if not child_descriptions:
            child_descriptions = ["No entity descriptions available"]

        return self.properties['aggregation_prompt'].format(
            child_type='entity',
            parent_type='collection',
            child_descriptions='\n'.join(child_descriptions),
            parent_metadata=f"Collection name: {collection_name}\nMetadata: {collection_metadata}"
        )

    def build_database_description_prompt(self, database_name, collection_descriptions, database_metadata):
        child_descriptions = [f"{name}: {desc}" for name, desc in collection_descriptions.items() if desc]
        if not child_descriptions:
            child_descriptions = ["No collection descriptions available"]

        return self.properties['aggregation_prompt'].format(
            child_type='collection',
            parent_type='database',
            child_descriptions='\n'.join(child_descriptions),
            parent_metadata=f"Database name: {database_name}\nMetadata: {database_metadata}"
        )

    def enrich_collection_description(self, collection_name, entity_descriptions, collection_metadata):
        prompt = self.build_collection_description_prompt(collection_name, entity_descriptions, collection_metadata)
        return self.execute_api_call(prompt, properties=self.properties, additional_data={})

    def enrich_database_description(self, database_name, collection_descriptions, database_metadata):
        prompt = self.build_database_description_prompt(database_name, collection_descriptions, database_metadata)
        return self.execute_api_call(prompt, properties=self.properties, additional_data={})
