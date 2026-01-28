from blue.utils.service_utils import ServiceClient
from blue.utils import json_utils
from blue.data.prompt_templates import AGGREGATION_PROMPT
from blue.properties import PROPERTIES

import logging
import json
import os
import math
import numpy as np




class MetaData(ServiceClient):

    SEMANTIC_ROLES = [
        "IDENTIFIER",            # IDs, UUIDs
        "EVENT_TIME",             # e.g. transaction_time, crash_time
        "EVIDENCE",               # e.g. skill_months
        "SEGMENTATION_DRIVER",    # e.g. country of high-value customers
        "DESCRIPTIVE"             # weak explanatory power
    ]

    # ------------------------------------------------------------------
    # Value Semantics type taxonomy (domain-agnostic, value-centric)
    # ------------------------------------------------------------------
    VALUE_SEMANTIC_TYPES = [
        "UNKNOWN",

        # structural
        "BOOLEAN",
        "INTEGER",
        "FLOAT",
        "NUMERIC_GENERAL",
        "STRING",
        "FREE_TEXT",

        # temporal
        "DATE",
        "DATETIME",
        "TIME",
        "YEAR",
        "MONTH",
        "DAY_OF_WEEK",
        "DURATION",

        # location / codes
        "US_STATE_CODE",
        "US_STATE_NAME",
        "COUNTRY_CODE_ISO2",
        "COUNTRY_CODE_ISO3",
        "CITY_NAME",
        "POSTAL_CODE",
        "ADDRESS_FREEFORM",

        # financial / numeric semantics
        "CURRENCY_AMOUNT",
        "PERCENTAGE",
        "RATIO",

        # identity / ids
        "ID_NUMERIC",
        "ID_STRING",
        "UUID",
        "HASH",

        # contact / web
        "EMAIL",
        "PHONE_NUMBER",
        "URL",

        # categories & labels
        "ENUM_CATEGORY",
        "TEXT_CATEGORY",
        "TAG",
        "LABEL",

        # human / skills-ish / terms
        "PERSON_NAME",
        "ORG_NAME",
        "JOB_TITLE",
        "SKILL_TERM",
        "CONTROLLED_TERM",

        # demographic-ish but still value-level
        "AGE",
        "AGE_GROUP",
        "DEMOGRAPHIC_TERM",
    ]
 
    def __init__(self, properties=None):
        self.name = "metadata"
        super().__init__(self.name, properties=properties)
        self._init_metadata_properties()

    ###### initialization
    def _init_metadata_properties(self):

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
        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]

        # transformations
        self.properties['output_transformations'] = [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}]
        self.properties['output_strip'] = True

        self.properties['enable_entity_description_generation'] = True
        self.properties['enable_attribute_description_generation'] = True

        # Description aggregation from children
        self.properties['aggregation_prompt'] = AGGREGATION_PROMPT
        self.properties['enable_database_description_generation'] = True
        self.properties['enable_collection_description_generation'] = True

        self.properties['enable_value_semantics_inference'] = True
        self.properties['enable_semantic_discovery_inference'] = True
        
        self.properties['enable_domain_concept_mapping'] = True

        self.properties['enable_value_axis_inference'] = True
        self.properties['enable_semantic_links_inference'] = True
        self.properties['enable_interpretive_semantics'] = True

        self.properties["concept_taxonomy_path"] = "/blue_data/config/concept_taxonomy.json"
        self.properties["concept_taxonomy"] = self._load_concept_taxonomy()

    @staticmethod
    def mean_safe(vals):
        return sum(vals) / len(vals) if vals else None

    @staticmethod
    def safe_pearson(x, y):
        if len(x) < 5 or len(y) < 5:
            return 0.0
        mx, my = sum(x)/len(x), sum(y)/len(y)
        num = sum((a-mx)*(b-my) for a,b in zip(x,y))
        denx = math.sqrt(sum((a-mx)**2 for a in x))
        deny = math.sqrt(sum((b-my)**2 for b in y))
        if denx == 0 or deny == 0:
            return 0.0
        return num / (denx * deny)


    @staticmethod
    def get_numeric_samples(attr):
        stats = attr.get("properties", {}).get("stats", {})
        samples = stats.get("sample_values", [])
        nums = []
        for v in samples:
            try:
                nums.append(float(v))
            except Exception:
                pass
        return nums

    def has_row_cooccurrence(self, a, b, row_samples, min_rows=5):
        a_name = a["name"]
        b_name = b["name"]

        count = 0
        for row in row_samples:
            if row.get(a_name) is not None and row.get(b_name) is not None:
                count += 1
                if count >= min_rows:
                    return True
        return False

    def functional_dependency_signal(self, a, b):
        """
        Detect potential functional / monotonic dependency between two attributes.
        """
        a_vals = self.get_numeric_samples(a)
        b_vals = self.get_numeric_samples(b)

        if len(a_vals) < 5 or len(b_vals) < 5:
            return False

        corr = abs(self.safe_pearson(a_vals, b_vals))
        return corr > 0.7

    def temporal_alignment_signal(self, a, b):
        """
        Detect weak temporal alignment without semantic commitment.
        """
        a_type = a.get("properties", {}).get("value_semantics", {}).get("semantic_type")
        b_type = b.get("properties", {}).get("value_semantics", {}).get("semantic_type")

        temporal_types = {"DATE", "DATETIME", "TIME", "DURATION"}
        return a_type in temporal_types and b_type not in temporal_types



    
    
    def _load_concept_taxonomy(self):
        """
        Load domain concept taxonomy from the shared /blue_data/config folder.
        """
        taxonomy_path = self.properties.get(
            "concept_taxonomy_path",
            "/blue_data/config/concept_taxonomy.json"
        )

        if not os.path.exists(taxonomy_path):
            logging.warning(f"[MetaData] Domain taxonomy not found at: {taxonomy_path}")
            return []

        try:
            with open(taxonomy_path, "r") as f:
                data = json.load(f)
                return data.get("concepts", [])
        except Exception as e:
            logging.error(f"[MetaData] Failed loading taxonomy: {e}")
            return []


    def build_entity_description_prompt(self, entity_obj, attributes):
        """
        Build a prompt for generating an entity description using an LLM.

        Constructs a structured text prompt containing entity metadata and attribute
        information, suitable for guiding an LLM to produce a JSON-formatted
        description of the entity and its attributes.

        Parameters:
            entity_obj (dict): A dictionary representing the entity, from
                the data registry.
            attributes (list[dict]): A list of attribute definitions.

        Returns:
            str: A formatted multi-line string prompt, instructing the LLM to produce
            a JSON object with:
                - "table_description": Human-readable description of the entity.
                - "attributes": Mapping of attribute names to their descriptions.

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
            attr_stats = attr_properties.get("stats", {})

            sample_values = attr_stats.get("sample_values", [])

            attr_lines.append(f"- {attr_name} ({attr_type}), samples: {', '.join(map(str, sample_values[:3]))}")

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
        """
        Generate an enriched description for an entity using its attributes.

        Builds a prompt from the entity and its attributes, then calls the
        external LLM API to produce the enriched description.

        Parameters:
            entity (dict): The entity metadata to enrich.
            attributes (dict): Attribute data associated with the entity.

        Returns:
            str: Enriched description text generated by the API.
        """
        entity_prompt = self.build_entity_description_prompt(entity, attributes)
        return self.execute_api_call(entity_prompt, properties=self.properties, additional_data={})

    def collect_source_metadata(self, data_registry, source, recursive=False, rebuild=False):
        """
        Collect and optionally recursively enrich metadata for a data source.

        If recursive is True, iterates through all databases under the source
        and collects/enriches their metadata.

        Parameters:
            data_registry (DataRegistry): Registry instance for metadata access/storage.
            source (str): Identifier of the data source.
            recursive (bool, optional): Whether to include child databases. Defaults to False.
            rebuild (bool, optional): Whether to regenerate existing descriptions. Defaults to False.

        Returns:
            None
        """
        if recursive:
            databases = data_registry.get_source_databases(source)
            for database in databases:
                self.collect_source_database_metadata(data_registry, source, database, recursive=recursive, rebuild=rebuild)
        return

    def collect_source_database_metadata(self, data_registry, source, database, recursive=False, rebuild=False):
        """
        Collect and enrich metadata for a database within a data source.

        This method checks whether the database already has a description. If not,
        it uses available metadata and collection descriptions to generate an
        enriched description (via `enrich_database_description`) and stores it
        back into the data registry. Optionally, it can also recurse into
        collections to collect their metadata.

        Parameters:
            data_registry (DataRegistry): The registry object that manages sources,
                databases, collections, and metadata.
            source (str): Identifier for the data source.
            database (str): Name of the database to collect metadata for.
            recursive (bool, optional): If True, also collect metadata for all
                collections within the database. Defaults to False.
            rebuild (bool, optional): If True, forces metadata to be rebuilt or
                refreshed even if it already exists. Defaults to False.

        Returns:
            None

        """
        collections = data_registry.get_source_database_collections(source, database)
        collection_descriptions = {}

        if recursive:
            for collection in collections:
                collection_name = collection.get("name")
                self.collect_source_database_collection_metadata(
                    data_registry,
                    source,
                    database,
                    collection_name,
                    recursive=True,
                    rebuild=rebuild
                )

        
        if self.properties.get('enable_database_description_generation', True):
            current_description = data_registry.get_source_database_description(source, database)
            if rebuild or not current_description or current_description.strip() == "":
                database_metadata = data_registry.get_source_database_property(source, database, "metadata")

                if not database_metadata:
                    database_metadata = {"name": database, "type": "database"}

                for collection in collections:
                    collection_name = collection.get("name")
                    collection_desc = collection.get("description")
                    collection_descriptions[collection_name] = collection_desc

                database_desc = self.enrich_database_description(database, collection_descriptions, database_metadata)

                data_registry.set_source_database_description(source, database, database_desc, rebuild=rebuild)

        return

    def collect_source_database_collection_metadata(self, data_registry, source, database, collection, recursive=False, rebuild=False):
        """
        Collect and enrich metadata for a specific collection and its entities within a database.

        For each entity in the collection, generates enriched table and attribute descriptions
        using the LLM-based enrichment process, and stores them in the data registry if missing.
        Optionally, also generates a collection-level description.

        Parameters:
            data_registry (DataRegistry): Registry instance for accessing and storing metadata.
            source (str): Identifier of the data source.
            database (str): Name of the database containing the collection.
            collection (str): Name of the collection to process.
            recursive (bool, optional): Whether to process nested collections or entities. Defaults to False.
            rebuild (bool, optional): Whether to regenerate existing descriptions. Defaults to False.

        Returns:
            None
        """

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

            if self.properties.get('enable_entity_description_generation', True):
                current_description = data_registry.get_source_database_collection_entity_description(source, database, collection, entity_name)

                if not current_description or current_description.strip() == "":
                    data_registry.set_source_database_collection_entity_description(source, database, collection, entity_name, table_desc, rebuild=rebuild)

            if self.properties.get('enable_attribute_description_generation', True):
                for attr, desc in attribute_descs.items():
                    current_description = data_registry.get_source_database_collection_entity_attribute_description(source, database, collection, entity_name, attr)
                    if not current_description or current_description.strip() == "":
                        data_registry.set_source_database_collection_entity_attribute_description(source, database, collection, entity_name, attr, desc, rebuild=rebuild)

            self.current_entity_attributes = attributes

            if self.properties.get("enable_value_semantics_inference", True):
                for attr_obj in attributes:
                    attr_name = attr_obj.get("name")

                    # Skip attributes without stats or samples
                    attr_stats = attr_obj.get("properties", {}).get("stats", {})
                    if not attr_stats:
                        continue

                    # Check existing semantics
                    existing = data_registry.get_source_database_collection_entity_attribute_property(
                        source, database, collection, entity_name, attr_name, "value_semantics"
                    )

                    # Infer only if missing or rebuild=True
                    if existing and not rebuild:
                        continue

                    #inferred = self.infer_attribute_value_semantics(entity_name, attr_obj)
                    inferred = self.infer_attribute_vsi(entity_name, attr_obj)
                    
                    if inferred:
                        data_registry.set_source_database_collection_entity_attribute_property(
                            source,
                            database,
                            collection,
                            entity_name,
                            attr_name,
                            "value_semantics",
                            inferred,
                            rebuild=rebuild
                        )
                    
                    sdi = self.infer_attribute_sdi(entity_name, attr_obj)
                    if sdi:
                        data_registry.set_source_database_collection_entity_attribute_property(
                            source, database, collection, entity_name, attr_name,
                            "semantic_discovery", sdi, rebuild=rebuild
                        )
            

                ### refresh attributes after value semantics inference
                attributes = data_registry.get_source_database_collection_entity_attributes(
                    source, database, collection, entity_name
                )
            
            if self.properties.get("enable_domain_concept_mapping", True):
                for attr_obj in attributes:
                    attr_name = attr_obj.get("name")

                    # Skip attributes without value semantics
                    attr_properties = attr_obj.get("properties", {})
                    if "value_semantics" not in attr_properties:
                        continue

                    existing = data_registry.get_source_database_collection_entity_attribute_property(
                        source, database, collection, entity_name, attr_name, "domain_concept"
                    )

                    if existing and not rebuild:
                        continue

                    inferred = self.infer_domain_concept(entity_name, attr_obj)
                    if inferred:
                        data_registry.set_source_database_collection_entity_attribute_property(
                            source,
                            database,
                            collection,
                            entity_name,
                            attr_name,
                            "domain_concept",
                            inferred,
                            rebuild=rebuild
                        )
            
            if self.properties.get("enable_interpretive_semantics", True):
                logging.info(f"[MetaData] Inferring interpretive semantics for entity: {entity_name}")
                for attr in attributes:
                    ivs = self.infer_interpretive_semantics(entity_name, attr)
                    if ivs:
                        data_registry.set_source_database_collection_entity_attribute_property(
                            source,
                            database,
                            collection,
                            entity_name,
                            attr["name"],
                            "interpretive_semantics",
                            ivs,
                            rebuild=rebuild
                        )

                        logging.info(
                            f"[IVS] Inferred interpretive semantics for "
                            f"{entity_name}.{attr['name']}: {ivs}"
                        )
            
            # Refresh attributes after IVS
            attributes = data_registry.get_source_database_collection_entity_attributes(
                source, database, collection, entity_name
            )
            
            if self.properties.get("enable_value_axis_inference", True):
                logging.info(f"[MetaData] Inferring value axes for entity: {entity_name}")
                axes = self.infer_value_axis(
                    attributes,
                    self.current_entity_row_samples
                )

                logging.info(f"[MetaData] Inferred value axes for entity {entity_name}: {axes}")
                
                for attr_name, axis in axes.items():
                    data_registry.set_source_database_collection_entity_attribute_property(
                        source, database, collection, entity_name,
                        attr_name, "value_axis", axis, rebuild=rebuild
                    )

                    logging.info(
                        f"[MetaData] Inferred VALUE_AXIS for {entity_name}.{attr_name}: {axis}"
                    )
            

            if self.properties.get("enable_semantic_links_inference", True):
                # -------------------------------------------------
                # 3. SEMANTIC LINK DISCOVERY (STRUCTURAL + SOFT LLM)
                # -------------------------------------------------
                semantic_links = self.infer_semantic_links(attributes)

                row_links = self.infer_row_based_links(
                    attributes,
                    self.current_entity_row_samples
                )

                # TAG row-grounded links
                for l in row_links:
                    l["row_support"] = True

                semantic_links = semantic_links + row_links

                validated_links = []

                for link in semantic_links:
                    try:
                        src = next(a for a in attributes if a["name"] == link["source"])
                        tgt = next(a for a in attributes if a["name"] == link["target"])
                    except StopIteration:
                        continue

                    result = self.validate_semantic_link(src, tgt, link["signal"])

                    # -------------------------------------------------
                    # SOFT ACCEPT LOGIC
                    # -------------------------------------------------
                    relationship = result.get("relationship") if result else None

                    signal_type = (
                        link["signal"].get("type")
                        if isinstance(link["signal"], dict)
                        else link["signal"]
                    )

                    if relationship == "UNRELATED" and signal_type in {
                        "grouped_distribution",
                        "functional_dependency",
                        "temporal_alignment",
                    }:
                        relationship = {
                            "grouped_distribution": "SEGMENTS",
                            "functional_dependency": "DERIVES",
                            "temporal_alignment": "SUPPORTS",
                        }[signal_type]


                    # -------------------------------------------------
                    # FINALIZE LINK
                    # -------------------------------------------------
                    if relationship:
                        if link.get("row_support"):
                            # Row-grounded links dominate LLM disagreement
                            confidence = max(
                                0.7,
                                result.get("confidence", 0.7) if result else 0.7
                            )
                        else:
                            confidence = (
                                result.get("confidence", 0.55)
                                if result and relationship == result.get("relationship")
                                else 0.55
                            )

                        validated_links.append({
                            "source": link["source"],
                            "target": link["target"],
                            "relationship": relationship,
                            "confidence": confidence,
                            "rationale": (
                                result.get("rationale")
                                if result else "Structure-backed semantic signal"
                            ),
                        })

                # Persist links
                if validated_links:
                    data_registry.set_source_database_collection_entity_property(
                        source,
                        database,
                        collection,
                        entity_name,
                        "semantic_links",
                        validated_links,
                        rebuild=rebuild
                    )
                # -------------------------------------------------
                # 4. SEMANTIC ROLE INFERENCE (LINK-DRIVEN)
                # -------------------------------------------------
                for attr in attributes:
                    attr_name = attr["name"]

                    role = self.infer_semantic_role(
                        attr,
                        attributes,
                        semantic_links=(validated_links or semantic_links)
                    )

                    if role:
                        data_registry.set_source_database_collection_entity_attribute_property(
                            source, database, collection, entity_name,
                            attr_name, "semantic_role", role, rebuild=rebuild
                        )
        
        if self.properties.get('enable_collection_description_generation', True):
            current_description = data_registry.get_source_database_collection_description(source, database, collection)
            if not current_description or current_description.strip() == "":

                collection_metadata = data_registry.get_source_database_collection_property(source, database, collection, "metadata")

                if not collection_metadata:
                    collection_metadata = {"name": collection, "type": "collection"}

                collection_desc = self.enrich_collection_description(collection, entity_descriptions, collection_metadata)

                data_registry.set_source_database_collection_description(source, database, collection, collection_desc, rebuild=rebuild)

    ###### Aggregation
    def build_collection_description_prompt(self, collection_name, entity_descriptions, collection_metadata):
        """
        Build a prompt string for generating or enriching a collection description.

        Constructs a formatted text prompt using entity-level descriptions and
        metadata, suitable for passing to an LLM or enrichment API.

        Parameters:
            collection_name (str): The name of the collection.
            entity_descriptions (dict): Mapping of entity names to their descriptions.
            collection_metadata (dict or str): Additional metadata for the collection.

        Returns:
            str: A formatted prompt string for collection-level description enrichment.
        """
        child_descriptions = [f"{name}: {desc}" for name, desc in entity_descriptions.items() if desc]
        if not child_descriptions:
            child_descriptions = ["No entity descriptions available"]

        return self.properties['aggregation_prompt'].format(
            child_type='entity',
            parent_type='collection',
            child_descriptions='\n'.join(child_descriptions),
            parent_metadata=f"Collection name: {collection_name}\nMetadata: {collection_metadata}",
        )

    def build_database_description_prompt(self, database_name, collection_descriptions, database_metadata):
        """
        Build a prompt string for generating or enriching a database description.

        Constructs a formatted text prompt using collection-level descriptions and
        metadata, suitable for passing to an LLM or enrichment API.

        Parameters:
            database_name (str): The name of the database.
            collection_descriptions (dict): Mapping of collection names to their descriptions.
            database_metadata (dict or str): Additional metadata for the database.

        Returns:
            str: A formatted prompt string for database-level description enrichment.
        """

        child_descriptions = [f"{name}: {desc}" for name, desc in collection_descriptions.items() if desc]
        if not child_descriptions:
            child_descriptions = ["No collection descriptions available"]

        return self.properties['aggregation_prompt'].format(
            child_type='collection', parent_type='database', child_descriptions='\n'.join(child_descriptions), parent_metadata=f"Database name: {database_name}\nMetadata: {database_metadata}"
        )

    def enrich_collection_description(self, collection_name, entity_descriptions, collection_metadata):
        """
        Enrich a collection description using LLM.

        Builds a prompt from the provided entity descriptions and metadata, then
        executes an LLM call to generate or refine the collection-level description.

        Parameters:
            collection_name (str): The name of the collection.
            entity_descriptions (dict): Mapping of entity names to their descriptions.
            collection_metadata (dict or str): Additional metadata for the collection.

        Returns:
            Any: The enriched collection description, as returned by the LLM.
        """
        prompt = self.build_collection_description_prompt(collection_name, entity_descriptions, collection_metadata)
        return self.execute_api_call(prompt, properties=self.properties, additional_data={})

    def enrich_database_description(self, database_name, collection_descriptions, database_metadata):
        """
        Enrich a database description using LLM.

        Builds a prompt from the provided collection descriptions and metadata, then
        executes an API call to generate or refine the database-level description.

        Parameters:
            database_name (str): The name of the database.
            collection_descriptions (dict): Mapping of collection names to their descriptions.
            database_metadata (dict or str): Additional metadata for the database.

        Returns:
            Any: The enriched database description.
        """

        prompt = self.build_database_description_prompt(database_name, collection_descriptions, database_metadata)
        return self.execute_api_call(prompt, properties=self.properties, additional_data={})

    
    def build_attribute_context(self, attributes, target_attr_name):
        """
        Build lightweight cross-attribute context for VSI / SDI.

        Design principles:
        - Descriptive, not prescriptive
        - Distributional, not role-based
        - Column-attached, not joint inference
        - Safe for first-pass VSI / SDI
        """

        context = {
            "sibling_attributes": [],
            "numeric_distributions": {},
            "temporal_hints": [],
            "co_occurrence_hints": [],
            "relative_behavior": []   # distributional semantics
        }

        for attr in attributes:
            name = attr.get("name")
            if name == target_attr_name:
                continue

            props = attr.get("properties", {}) or {}
            stats = props.get("stats", {}) or {}
            sem = props.get("value_semantics", {}) or {}

            samples = stats.get("sample_values", [])[:5]

            # -------------------------------------------------
            # Sibling attribute names
            # -------------------------------------------------
            context["sibling_attributes"].append(name)

            # -------------------------------------------------
            # Robust numeric detection (NO VSI DEPENDENCY)
            # -------------------------------------------------
            min_val = stats.get("min")
            max_val = stats.get("max")

            is_numeric = (
                isinstance(min_val, (int, float))
                or isinstance(max_val, (int, float))
            )

            if is_numeric:
                context["numeric_distributions"][name] = {
                    "min": min_val,
                    "max": max_val,
                    "distinct": stats.get("distinct_count")
                }

                # -------------------------------------------------
                # Distributional role hints (NOT semantic roles)
                # Skip identifiers — they distort scale semantics
                # -------------------------------------------------
                if not sem.get("is_identifier"):
                    magnitude = max_val
                    if isinstance(magnitude, (int, float)):
                        context["relative_behavior"].append({
                            "attribute": name,
                            "scale_hint": (
                                "small_range" if magnitude < 100
                                else "medium_range" if magnitude < 10000
                                else "large_range"
                            )
                        })

            # -------------------------------------------------
            # Temporal hints (weak, non-binding)
            # -------------------------------------------------
            if sem.get("semantic_type") in ("DATE", "DATETIME", "DURATION"):
                context["temporal_hints"].append(name)

            # -------------------------------------------------
            # Co-occurrence hints (cheap evidence only)
            # -------------------------------------------------
            if samples:
                context["co_occurrence_hints"].append({
                    "attribute": name,
                    "sample_values": samples
                })

        # -------------------------------------------------
        # OPTIONAL: relative scale comparison across attributes
        # (strengthens distributional semantics without roles)
        # -------------------------------------------------
        if len(context["relative_behavior"]) >= 2:
            context["relative_behavior_summary"] = {
                "comparison": [
                    (rb["attribute"], rb["scale_hint"])
                    for rb in context["relative_behavior"]
                ]
            }

        return context
    
    def build_vsi_prompt(self, entity_name, attr_name, attr_properties, context=None):
        """
        VSI (Value Semantics Inference) — deterministic, bounded.
        Uses stats + sample values + bounded semantic types.
        """

        stats = attr_properties.get("stats", {}) or {}
        sample_values = stats.get("sample_values", [])[:10]
        if not sample_values:
            sample_values = ["<NO SAMPLE VALUES AVAILABLE>"]

        attr_type = attr_properties.get("info", {}).get("type", "unknown")

        stats_json = json.dumps(stats, indent=2)
        samples_json = json.dumps(sample_values, indent=2)
        allowed_json = json.dumps(self.VALUE_SEMANTIC_TYPES, indent=2)
        context_json = json.dumps(context or {}, indent=2)


        schema_json = """{
  "value_semantics": {
    "primary_type": "<ONE_OF_ALLOWED_TYPES>",
    "secondary_types": [],
    "is_categorical": false,
    "is_identifier": false,
    "is_free_text": false,
    "numeric": {
      "is_numeric": false,
      "is_continuous": false,
      "is_discrete": false,
      "min": null,
      "max": null
    },
    "temporal": {
      "is_date": false,
      "is_datetime": false,
      "is_duration": false,
      "granularity": null
    },
    "normalization": {
      "can_normalize": false,
      "normalized_examples": [],
      "normalization_strategy": null
    },
    "confidence": 0.0,
    "examples_used": [],
    "notes": []
  }
}"""

        prompt = f"""
You are performing Value Semantics Inference (VSI), a deterministic and bounded semantic classification
module used by autonomous agents. You MUST infer WHAT THE VALUES *ARE*, not what they represent in the domain.

Rules:
- Use ONLY value patterns + statistics.
- You MAY use other attributes ONLY for structural AND distributional disambiguation
  (e.g., distinguishing durations vs counts, identifiers vs categories,
   event times vs boundaries).
- You MUST NOT infer business, policy, or domain concepts from context.
- Cross-attribute context is evidence, not ground truth.
- Use ONLY allowed semantic types.
- You MUST be deterministic, safe, and predictable.
- You MUST produce machine-usable semantics.
- DO NOT invent new types. Stay within allowed types.
- DO NOT infer business/domain meanings.

───────────────────────────────
ATTRIBUTE CONTEXT
───────────────────────────────
Entity: {entity_name}
Attribute: {attr_name}
Declared Type: {attr_type}

ATTRIBUTE_STATS:
{stats_json}

SAMPLE_VALUES:
{samples_json}

OTHER_ATTRIBUTES_IN_ENTITY (contextual structural hints only):
{context_json}


ALLOWED_SEMANTIC_TYPES:
{allowed_json}

───────────────────────────────
OUTPUT FORMAT (STRICT JSON ONLY)
───────────────────────────────

{schema_json}

Return ONLY this JSON structure, filled in appropriately.
"""
        return prompt.strip()

    
    def build_sdi_prompt(self, entity_name, attr_name, attr_properties, context=None):
        """
        SDI (Semantic Discovery Inference) — 
        This discovers fuzzy/emergent semantic concepts unconstrained by taxonomy.
        """

        return self.build_value_semantics_prompt(entity_name, attr_name, attr_properties, context=context)

    
    
    def build_value_semantics_prompt(self, entity_name, attr_name, attr_properties, context=None):
        """
        Build a generalized and production-grade prompt for Value Semantics Inference (VST).
        This design supports: open-world semantic categories, linguistic and structural inference,
        fuzzy categories, ranges, thresholds, and dynamic concept generation without relying on
        enumerated domain lists. Suitable for agentic systems and evolving datasets.
        """

        attr_stats = attr_properties.get("stats", {})
        sample_values = attr_stats.get("sample_values", [])[:10]
        if not sample_values:
            sample_values = ["<NO SAMPLE VALUES AVAILABLE>"]

        attr_type = attr_properties.get("info", {}).get("type", "unknown")

        prompt = f"""
        You are an advanced VALUE SEMANTICS inference engine designed for enterprise-scale,
        heterogeneous data. Your goal is to infer the **intrinsic semantic meaning** of the VALUES
        in a database attribute—based only on the values themselves, not business rules.

        ──────────────────────────────────────────────
        VALUE SEMANTICS (VST) — CORE PRINCIPLES
        ──────────────────────────────────────────────
        You operate under an OPEN-WORLD semantic model:

        1. VST is NOT a closed taxonomy.
        2. You may generate new semantic types if supported by patterns in the values.
        3. You infer meaning by analyzing:
        • linguistic patterns
        • structural patterns
        • categorical signals
        • statistical regularities
        • latent real-world semantics

        Never restrict yourself to predefined categories.

        ──────────────────────────────────────────────
        THE THREE-LAYER SEMANTIC MODEL
        ──────────────────────────────────────────────

        You infer semantics across three conceptual layers:

        LAYER 1 — STRUCTURAL SEMANTICS
            What *shape* do the values have?
            Examples: STRING, NUMBER, INTEGER, DATE, URL, EMAIL, ID_STRING, BOOLEAN, CODE

        LAYER 2 — LINGUISTIC / ENTITY SEMANTICS
            What *type of entity or label* do the values resemble?
            Examples (not exhaustive):
            - person names
            - job titles
            - certification names
            - skills or competencies
            - locations (city/state/country)
            - product names
            - organizational entities
            These categories are open-world: you may create new ones.

        LAYER 3 — CONCEPTUAL / CATEGORY SEMANTICS
            What *semantic class or conceptual grouping* do the values imply?
            This includes:
            - demographic groups (teenagers, seniors)
            - vehicle classes (heavy truck, light truck)
            - risk/quality tiers
            - product tiers (premium, basic)
            - salary or value levels (high/low/medium)
            - measurement categories (speed, volume, weight)
            - domain-relevant categories emerging from patterns
            Again, this is open-world: you may generate new conceptual classes.

        IMPORTANT:
            These layers are not mutually exclusive — you produce the *most informative*
            semantic type that best describes the values.

        ──────────────────────────────────────────────
        GENERALIZED DETECTION PATTERNS
        ──────────────────────────────────────────────
        Use the following reasoning strategies:

        • STRUCTURAL SIGNALS:
            - formats (dates, codes, emails, numbers)
            - token patterns
            - length consistency
            - character composition

        • LINGUISTIC SIGNALS:
            - multi-word phrases
            - professional titles
            - credential-like structures (“Certified…”, “Diploma in…”)
            - named entities (locations, organizations)
            - labels with standardized wording (hazard class, tier labels)

        • CATEGORY SIGNALS:
            - group names (“teenagers”, “seniors”)
            - categorical adjectives (high, low, premium, hazardous)
            - domain-like clusters (“heavy truck”, “backup technologies certifications”)
            - ordinal or tiered values

        • NUMERIC SEMANTICS:
            If values *represent* categories (not numbers), infer:
                – ranges (age group, tier)
                – thresholds (heavy truck → payload > X)
                – levels (risk, salary, quality)

        ──────────────────────────────────────────────
        WHEN TO USE FREE_TEXT
        ──────────────────────────────────────────────
        ONLY use FREE_TEXT if:

        1. Values show no consistent structure,
        2. No stable linguistic or categorical signals exist,
        3. Values are arbitrary human-written sentences with no common semantic class.

        This should be rare.

        ──────────────────────────────────────────────
        OUTPUT FORMAT (STRICT JSON ONLY)
        ──────────────────────────────────────────────

        {{
        "semantic_type": "string",
        "subcategory": "string or null",
        "confidence": 0.0,
        "range": {{
            "min": number or null,
            "max": number or null
        }},
        "criteria": "string or null",
        "rationale": "short explanation of the inferred semantics",
        "examples": []
        }}

        INTERPRETATION GUIDELINES:
        - semantic_type is the most informative object-level category.
        - subcategory is a refinement (e.g., HEAVY_TRUCK, TEENAGER, PREMIUM).
        - range is used only when applicable (ages, thresholds, numeric groups).
        - criteria is used for inferred thresholds or rules.
        - examples must be from the provided values.

        ──────────────────────────────────────────────
        ATTRIBUTE CONTEXT
        ──────────────────────────────────────────────
        Entity: {entity_name}
        Attribute: {attr_name}
        Declared Type: {attr_type}

        Sample Values:
        {json.dumps(sample_values, indent=2)}

        ───────────────────────────────
        CROSS-ATTRIBUTE CONTEXT (OPTIONAL EVIDENCE)
        ───────────────────────────────
        {json.dumps(context or {}, indent=2)}

        Guidelines:
        - Use this context ONLY to discover latent groupings, thresholds,
        or fuzzy categories.
        - Do NOT assign roles or enforce consistency across columns.

        Now infer the most accurate semantics and return ONLY valid JSON.
        """
        return prompt.strip()

    
    def infer_attribute_vsi(self, entity_name, attr):
        attr_name = attr.get("name")
        props = attr.get("properties", {})

        context = self.build_attribute_context(
            self.current_entity_attributes, attr_name
        )

        prompt = self.build_vsi_prompt(entity_name, attr_name, props, context=context)
        llm_output = self.execute_api_call(prompt, properties=self.properties, additional_data={})

        try:
            parsed = json_utils.safe_json_parse(llm_output)
            if not parsed:
                return None

            # unwrap
            if "value_semantics" in parsed:
                vs = parsed["value_semantics"]
            else:
                vs = parsed

            # ensure compatibility with old DCM (“semantic_type”)
            if "primary_type" in vs:
                vs["semantic_type"] = vs.get("primary_type")

            return vs

        except Exception:
            logging.warning(f"Invalid VSI JSON for {entity_name}.{attr_name}")
            return None

    
    def infer_attribute_sdi(self, entity_name, attr):
        attr_name = attr.get("name")
        props = attr.get("properties", {})

        context = self.build_attribute_context(
            self.current_entity_attributes, attr_name
        )

        prompt = self.build_sdi_prompt(entity_name, attr_name, props, context=context)
        llm_output = self.execute_api_call(prompt, properties=self.properties, additional_data={})

        try:
            parsed = json_utils.safe_json_parse(llm_output)
            return parsed
        except Exception:
            logging.warning(f"Invalid SDI JSON for {entity_name}.{attr_name}")
            return None
    
    def infer_attribute_value_semantics(self, entity_name, attr):
        attr_name = attr.get("name")
        attr_properties = attr.get("properties", {})

        # Build prompt
        prompt = self.build_value_semantics_prompt(entity_name, attr_name, attr_properties)

        # Call LLM
        llm_output = self.execute_api_call(prompt, properties=self.properties, additional_data={})

        # Parse LLM output
        try:
            semantics = json_utils.safe_json_parse(llm_output)
            if not semantics:
                logging.warning(f"Value semantics inference returned empty for {entity_name}.{attr_name}")
                return None
            return semantics
        except Exception:
            logging.warning(f"Invalid JSON from value semantics inference for {entity_name}.{attr_name}")
            return None

    def build_domain_concept_prompt(self, entity_name, attr_name, attr_properties):
        """
        Build a prompt for mapping an attribute to a domain concept.
        """
        taxonomy = self.properties.get("concept_taxonomy", [])
        taxonomy_text = "\n".join([f"- {c}" for c in taxonomy]) if taxonomy else "- CONCEPT.UNKNOWN"

        semantics = attr_properties.get("value_semantics", {})
        semantic_type = semantics.get("semantic_type", "UNKNOWN")
        
        # incorporate SDI
        sdi = attr_properties.get("semantic_discovery", {})
        sdi_text = json.dumps(sdi, indent=2) if sdi else "None"
        
        sample_values = semantics.get("examples", [])
        if not sample_values:
            sample_values = attr_properties.get("stats", {}).get("sample_values", [])[:5]

        if not sample_values:
            sample_values = ["<NO SAMPLE VALUES AVAILABLE>"]

        prompt = f"""
        You are performing domain concept mapping for a data registry.

        Map the attribute to a canonical DOMAIN CONCEPT.

        Available domain concepts:
        {taxonomy_text}

        Attribute Context:
        - Entity: {entity_name}
        - Attribute Name: {attr_name}
        - Semantic Type: {semantic_type}

        Semantic Discovery Output (SDI):
        {sdi_text}

        Sample Values:
        {json.dumps(sample_values, indent=2)}

        Output JSON ONLY:

        {{
            "concept": "CONCEPT.X.Y",
            "confidence": 0.0,
            "rationale": "explain briefly"
        }}
        """
        
        return prompt.strip()

    def infer_domain_concept(self, entity_name, attr):
        attr_name = attr.get("name")
        attr_properties = attr.get("properties", {})

        # Skip if no value semantics yet
        if "value_semantics" not in attr_properties:
            return None

        prompt = self.build_domain_concept_prompt(entity_name, attr_name, attr_properties)

        llm_output = self.execute_api_call(prompt, properties=self.properties, additional_data={})

        try:
            concept = json_utils.safe_json_parse(llm_output)
            if not concept:
                logging.warning(f"Domain concept inference empty for {entity_name}.{attr_name}")
                return None
            return concept
        except Exception:
            logging.warning(f"Invalid JSON from domain concept inference for {entity_name}.{attr_name}")
            return None


    def grouped_distribution_signal(self, group_attr, value_attr):
        """
        Detect whether grouping by group_attr produces
        meaningfully different distributions of value_attr.

        This version is calibrated for small sample_values and
        enables SEGMENTATION_DRIVER to emerge without hallucination.
        """

        g_vals = group_attr.get("properties", {}).get("stats", {}).get("sample_values", [])
        v_vals = value_attr.get("properties", {}).get("stats", {}).get("sample_values", [])

        if not g_vals or not v_vals:
            return False

        try:
            groups = {}

            for g, v in zip(g_vals, v_vals):
                try:
                    v = float(v)
                except Exception:
                    continue
                groups.setdefault(g, []).append(v)

            # Require enough groups and per-group support
            min_groups = 2   # instead of 3
            if len(groups) < min_groups:
                return False
    
            supported_groups = [vals for vals in groups.values() if len(vals) >= 2]
            if len(supported_groups) < 2:
                return False

            means = [sum(vals) / len(vals) for vals in groups.values()]

            max_mean = max(abs(m) for m in means) if means else 0.0
            if max_mean == 0:
                return False

            spread = max(means) - min(means)
            avg_mean = sum(abs(m) for m in means) / len(means)
            relative_spread = spread / avg_mean if avg_mean > 0 else 0.0

            # Two-tier acceptance:
            # 1. Absolute spread (classic signal)
            # 2. Relative spread (robust for small/noisy samples)
            return (
                spread > 0.12 * max_mean
                or relative_spread > 0.18
            )

        except Exception:
            return False

    def grouped_distribution_signal_row_aligned(self, group_attr, value_attr,row_samples):
        """
        Row-grounded version of grouped_distribution_signal.
        Uses real co-occurrence, not column samples.
        """

        g_name = group_attr["name"]
        v_name = value_attr["name"]

        g_vals = []
        v_vals = []

        for row in row_samples:
            if g_name not in row or v_name not in row:
                continue

            g = row.get(g_name)
            v = row.get(v_name)

            if g is None or v is None:
                continue

            try:
                v = float(v)
            except Exception:
                continue

            g_vals.append(g)
            v_vals.append(v)

        if len(g_vals) < 5:
            return False

        return self.grouped_distribution_signal(
            {"properties": {"stats": {"sample_values": g_vals}}},
            {"properties": {"stats": {"sample_values": v_vals}}},
        )

    def infer_semantic_links(self, attributes):
        """
        Find candidate semantic relationships between attributes.
        Returns a list of {source, target, signal}.
        """
        links = []

        for a in attributes:
            for b in attributes:
                if a["name"] == b["name"]:
                    continue

                # SEGMENTATION (distributional, data-driven)
                if self.grouped_distribution_signal(a, b):
                    links.append({
                        "source": a["name"],
                        "target": b["name"],
                        "signal": "grouped_distribution",
                        "row_support": False
                    })

                # ----------------------------------
                # FUNCTIONAL DEPENDENCY (numeric)
                # ----------------------------------
                if self.functional_dependency_signal(a, b):
                    links.append({
                        "source": a["name"],
                        "target": b["name"],
                        "signal": {
                            "type": "functional_dependency",
                            "strength": 0.7
                        }
                    })

        return links

    def validate_semantic_link(self, source, target, signal):
        """
        Validate a semantic link between two attributes.
        """
        src_props = source.get("properties", {})
        tgt_props = target.get("properties", {})

        src_vs = src_props.get("value_semantics", {})
        tgt_vs = tgt_props.get("value_semantics", {})

        src_semantic_type = src_vs.get("semantic_type", "UNKNOWN")
        tgt_semantic_type = tgt_vs.get("semantic_type", "UNKNOWN")

        # ---- Prompt ------------------------------------------------------
        prompt = f"""
    You are validating a semantic relationship between two attributes.

    Source attribute:
    - Name: {source.get('name', 'UNKNOWN')}
    - Semantic type: {src_semantic_type}

    Target attribute:
    - Name: {target.get('name', 'UNKNOWN')}
    - Semantic type: {tgt_semantic_type}

    Observed signal: {signal}

    Choose ONE relationship:
    - SEGMENTS
    - DERIVES
    - SUPPORTS
    - ASSOCIATED
    - UNRELATED

    If semantic types are UNKNOWN, rely primarily on the observed signal.

    Return JSON ONLY:
    {{
    "relationship": "...",
    "confidence": 0.0,
    "rationale": "short explanation"
    }}
    """

        out = self.execute_api_call(
            prompt,
            properties=self.properties,
            additional_data={}
        )

        return json_utils.safe_json_parse(out)


    def infer_semantic_role(self, target_attr, all_attrs, semantic_links=None):
        """
        Infer the semantic role of a target attribute based on its relationships.
        """

        semantic_links = semantic_links or []

        attr_name = target_attr["name"]
        vsi = target_attr.get("properties", {}).get("value_semantics", {})
        primary_type = vsi.get("semantic_type", "UNKNOWN")

        # -------------------------------------------------
        # 1. IDENTIFIER (hard rule)
        # -------------------------------------------------
        if vsi.get("is_identifier"):
            return {
                "primary_role": "IDENTIFIER",
                "confidence": 0.95,
                "role_arguments": {},
                "justification": {
                    "rule": "identifier_flag"
                }
            }

        outgoing = [l for l in semantic_links if l["source"] == attr_name]
        incoming = [l for l in semantic_links if l["target"] == attr_name]

        # -------------------------------------------------
        # 2. SEGMENTATION DRIVER
        # -------------------------------------------------
        #segment_links = [l for l in outgoing if l["relationship"] == "SEGMENTS"]
        
        segment_links = []
        for l in outgoing:
            if l["relationship"] != "SEGMENTS":
                continue

            target = next(
                (a for a in all_attrs if a["name"] == l["target"]),
                None
            )
            if not target:
                continue

            target_vsi = target.get("properties", {}).get("value_semantics", {})
            if target_vsi.get("is_identifier"):
                continue  

            segment_links.append(l)
        
        if segment_links:
            return {
                "primary_role": "SEGMENTATION_DRIVER",
                "confidence": min(
                    0.95,
                    sum(l.get("confidence", 0.7) for l in segment_links) / len(segment_links)
                ),
                "role_arguments": {
                    "segments": [l["target"] for l in segment_links]
                },
                "justification": {
                    "signals": ["SEGMENTS"],
                    "link_count": len(segment_links)
                }
            }

        # -------------------------------------------------
        # RELATIONSHIP-DRIVEN FALLBACK (GENERIC)
        # -------------------------------------------------
        supports = [l for l in outgoing if l["relationship"] == "SUPPORTS"]

        if supports:
            return {
                "primary_role": "EVIDENCE",
                "confidence": min(
                    0.9,
                    sum(l.get("confidence", 0.7) for l in supports) / len(supports)
                ),
                "role_arguments": {
                    "supports": [l["target"] for l in supports]
                },
                "justification": {
                    "signals": ["SUPPORTS"]
                }
            }

        # -------------------------------------------------
        # DERIVED MEASURE
        # -------------------------------------------------
        #derive_links = [l for l in incoming if l["relationship"] == "DERIVES"]
        #if derive_links:
        #    return {
        #        "primary_role": "DERIVED_MEASURE",
        #        "confidence": min(
        #            0.95,
        #            sum(l.get("confidence", 0.7) for l in derive_links) / len(derive_links)
        #        ),
        #        "role_arguments": {
        #            "derived_from": [l["source"] for l in derive_links]
        #        },
        #        "justification": {
        #            "signals": ["DERIVES"],
        #            "link_count": len(derive_links)
        #        }
        #    }

        
        # -------------------------------------------------
        # WEAK TYPE PRIOR
        # -------------------------------------------------
        if primary_type in ("DATE", "DATETIME"):
            return {
                "primary_role": "EVENT_TIME",
                "confidence": 0.55,
                "role_arguments": {},
                "justification": {
                    "type_prior": primary_type
                }
            }

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------
        return {
            "primary_role": "DESCRIPTIVE",
            "confidence": 0.4,
            "role_arguments": {},
            "justification": {
                "reason": "no causal or statistical signals detected"
            }
        }

    def infer_row_based_links(self, attributes, row_samples):
        links = []

        if not row_samples:
            return links

        for a in attributes:
            for b in attributes:
                if a["name"] == b["name"]:
                    continue

                a_type = a.get("properties", {}).get("value_semantics", {}).get("semantic_type")
                b_type = b.get("properties", {}).get("value_semantics", {}).get("semantic_type")

                # ----------------------------------
                # SEGMENTATION (row-grounded)
                # ----------------------------------
                if self.grouped_distribution_signal_row_aligned(a, b, row_samples):
                    links.append({
                        "source": a["name"],
                        "target": b["name"],
                        "signal": "grouped_distribution",
                        "row_support": True
                    })
                    logging.info(f"Row-grounded grouped_distribution link: {a['name']} -> {b['name']}")

                
                # TEMPORAL ALIGNMENT (row-grounded, generic)
                if (
                a_type in ("DATE", "DATETIME", "TIME", "DURATION")
                and b_type not in ("DATE", "DATETIME", "TIME", "DURATION")
                and self.has_row_cooccurrence(a, b, row_samples)
                ):
                    links.append({
                        "source": a["name"],
                        "target": b["name"],
                        "signal": {
                            "type": "temporal_alignment",
                            "strength": 0.6,
                            "row_support": True
                        }
                    })
                
        return links


    def is_value_axis_eligible(self, attr):
        """
        Decide whether an attribute is eligible for value-axis inference.
        This is a SEMANTIC gate, not a statistical one.
        """

        props = attr.get("properties", {})
        vsi = props.get("value_semantics", {}) or {}

        semantic_type = vsi.get("semantic_type", "UNKNOWN")

        # ---- HARD EXCLUSIONS ----------------------------------
        # Identifiers, opaque codes, labels, join keys
        if vsi.get("is_identifier"):
            return False

        if semantic_type in {
            "ID_STRING",
            "ID_NUMERIC",
            "UUID",
            "HASH",
            "CODE",
            "TAG",
            "LABEL",
            "ENUM_CATEGORY",   # default ENUMs are NOMINAL unless proven otherwise
            "TEXT_CATEGORY"
        }:
            return False

        # ---- ALLOWED NUMERIC AXES -----------------------------
        if semantic_type in {
            "CURRENCY_AMOUNT",
            "INTEGER",
            "FLOAT",
            "NUMERIC_GENERAL",
            "PERCENTAGE",
            "RATIO",
            "DURATION"
        }:
            return True

        return False

    
    def infer_numeric_value_axis(self, attr, row_samples):
        """
        Infer magnitude-based axis for numeric attributes
        """

        name = attr["name"]
        values = []

        for row in row_samples:
            try:
                values.append(float(row.get(name)))
            except Exception:
                pass

        if len(values) < 20:
            return None

        p10 = np.percentile(values, 10)
        p90 = np.percentile(values, 90)

        return {
            "axis_type": "CONTINUOUS",
            "polarity": {
                "direction": "increasing",
                "meaning": "magnitude"
            },
            "extreme_regions": {
                "small": f"< {round(p10, 2)}",
                "large": f"> {round(p90, 2)}"
            },
            "confidence": 0.7,
            "rationale": "Distributional extremes inferred via quantiles"
        }


    def infer_value_axis(self, attributes, row_samples):
        """
        Infer value axes for attributes when supported.
        Returns dict: {attr_name: axis_metadata}
        """

        axes = {}
        
        # -------------------------------------------------
        # 1. NUMERIC MAGNITUDE AXES (UNCHANGED)
        # -------------------------------------------------
        for attr in attributes:
            if not self.is_value_axis_eligible(attr):
                continue

            semantic_type = (
                attr.get("properties", {})
                    .get("value_semantics", {})
                    .get("semantic_type")
            )

            if semantic_type in (
                "CURRENCY_AMOUNT",
                "INTEGER",
                "FLOAT",
                "NUMERIC_GENERAL",
                "PERCENTAGE",
                "RATIO",
                "DURATION"
            ):
                axis = self.infer_numeric_value_axis(attr, row_samples)
                if axis:
                    axes[attr["name"]] = axis

        # -------------------------------------------------
        # 2. ORDINAL AXES FROM IVS (NEW, EXPLICIT)
        # -------------------------------------------------
        for attr in attributes:
            name = attr["name"]

            if name in axes:
                continue  # never overwrite numeric axes

            if not self.is_ivs_promotable_to_value_axis(attr):
                continue

            ivs = attr["properties"]["interpretive_semantics"]

            axis = {
                "axis_type": "ORDINAL",
                "ordering": ivs.get("ordering", []),
                "polarity": ivs.get("polarity", {}),
                "extreme_regions": {
                    "low": ivs.get("ordering", [])[:1],
                    "high": ivs.get("ordering", [])[-1:]
                },
                "confidence": ivs.get("confidence", 0.7),
                "rationale": (
                    "Promoted from interpretive semantics "
                    "after confidence and semantic eligibility checks"
                ),
                "source": "interpretive_semantics"
            }

            axes[name] = axis

            logging.info(
                f"[ValueAxis] Promoted IVS → ORDINAL axis for {name}: {axis}"
            )

        return axes

    def is_ivs_promotable_to_value_axis(self, attr):
        """
        Decide whether interpretive semantics may be promoted
        to a VALUE AXIS (ORDINAL).

        This is a STRICT gate.
        """

        props = attr.get("properties", {})
        ivs = props.get("interpretive_semantics", {})
        vsi = props.get("value_semantics", {})

        if not ivs:
            return False

        if ivs.get("interpretation_type") not in ("ORDINAL", "TIER", "SEVERITY"):
            return False

        if ivs.get("confidence", 0.0) < 0.7:
            return False

        # Identifiers never qualify
        if vsi.get("is_identifier"):
            return False

        # Only categorical value types may enter this path
        if vsi.get("semantic_type") not in (
            "ENUM_CATEGORY",
            "TEXT_CATEGORY",
            "LABEL"
        ):
            return False

        return True

    def build_interpretive_semantics_prompt(
        self,
        entity_name,
        attr_name,
        attr_properties
    ):
        stats = attr_properties.get("stats", {})
        samples = stats.get("sample_values", [])[:10]

        sdi = attr_properties.get("semantic_discovery", {})
        vsi = attr_properties.get("value_semantics", {})

        return f"""
    You are performing INTERPRETIVE VALUE SEMANTICS (IVS).

    Your task:
    Infer WHETHER the categorical values imply an ORDERING, SEVERITY, or TIER
    that an intelligent agent *might* use when reasoning.

    IMPORTANT SAFETY RULES:
    - Do NOT assume meaning unless strongly implied.
    - If ordering is ambiguous, return interpretation_type = "NONE".
    - This output is OPTIONAL and MUST NOT be treated as ground truth.
    - Use SDI and linguistic signals as evidence, not authority.

    ────────────────────────────
    ATTRIBUTE CONTEXT
    ────────────────────────────
    Entity: {entity_name}
    Attribute: {attr_name}

    Sample Values:
    {json.dumps(samples, indent=2)}

    Value Semantics (VSI):
    {json.dumps(vsi, indent=2)}

    Semantic Discovery (SDI):
    {json.dumps(sdi, indent=2)}

    ────────────────────────────
    INTERPRETATION TYPES
    ────────────────────────────
    ORDINAL   → ordered categories (A < B < C)
    SEVERITY  → worse/better progression
    TIER      → product / quality levels
    NONE      → no safe interpretation

    ────────────────────────────
    OUTPUT FORMAT (STRICT JSON)
    ────────────────────────────
    {{
    "interpretation_type": "ORDINAL | SEVERITY | TIER | NONE",
    "ordering": [],
    "polarity": {{
        "direction": "increasing | decreasing",
        "meaning": "risk | severity | quality | preference | level"
    }},
    "confidence": 0.0,
    "rationale": "short explanation",
    "evidence": {{
        "examples": [],
        "source": "labels | SDI | linguistic"
    }}
    }}
    """

    def infer_interpretive_semantics(self, entity_name, attr):
        attr_name = attr["name"]
        props = attr.get("properties", {})

        # Hard gate: numeric & identifiers NEVER qualify
        vsi = props.get("value_semantics", {})
        if vsi.get("is_identifier"):
            return None

        semantic_type = vsi.get("semantic_type")
        if semantic_type not in ("ENUM_CATEGORY", "TEXT_CATEGORY"):
            return None

        prompt = self.build_interpretive_semantics_prompt(
            entity_name, attr_name, props
        )

        out = self.execute_api_call(
            prompt,
            properties=self.properties,
            additional_data={}
        )

        try:
            parsed = json_utils.safe_json_parse(out)

            if not parsed:
                return None

            # Strong safety filter
            if parsed.get("interpretation_type") == "NONE":
                return None

            if parsed.get("confidence", 0) < 0.6:
                return None

            return parsed

        except Exception:
            logging.warning(
                f"[IVS] Invalid interpretive semantics for {entity_name}.{attr_name}"
            )
            return None

    def infer_conditional_distributions(self, group_attr, value_attr, row_samples):
        """
        Discover conditional distribution semantics:
        P(value | group)
        """

        g_name = group_attr["name"]
        v_name = value_attr["name"]

        groups = {}

        for row in row_samples:
            g = row.get(g_name)
            v = row.get(v_name)

            if g is None or v is None:
                continue

            try:
                v = float(v)
            except Exception:
                continue

            groups.setdefault(g, []).append(v)

        profiles = {}
        for g, vals in groups.items():
            if len(vals) < 10:
                continue

            p50 = np.percentile(vals, 50)
            p90 = np.percentile(vals, 90)
            p99 = np.percentile(vals, 99)

            profiles[str(g)] = {   
                "count": len(vals),
                "p50": round(p50, 2),
                "p90": round(p90, 2),
                "p99": round(p99, 2),
                "typical_range": [round(np.min(vals), 2), round(p90, 2)],
                "extreme_range": [round(p90, 2), round(np.max(vals), 2)],
            }


        if len(profiles) < 2:
            return None

        MAX_GROUPS = 10
        if len(profiles) > MAX_GROUPS:
            return None

        return {
            "group_attribute": g_name,
            "value_attribute": v_name,
            "profiles": profiles,
            "recommended_stat": "p99",
            "confidence": 0.7,
            "rationale": "Conditional distributions inferred from row-aligned numeric behavior"
        }