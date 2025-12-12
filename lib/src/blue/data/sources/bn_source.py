import os

###### Parsers, Formats, Utils
import json
import copy

###### Source specific libs
from pgmpy.inference import VariableElimination
import networkx as nx

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema
from blue.data.sources.bn_utils import load_pgmpy_model


###############
### BNSource
#
class BNSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        self._cache = {}

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 0 # not used
        self.properties['connection']['protocol'] = 'bn'
        self.properties['connection']['variant'] = 'pgmpy'
        self.properties['connection']['source_directory'] = '.'

    def _connect(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        if 'database' in connection:
            database = connection['database']
            database_path = self._get_database_path(database)
            
            # Load collections from database path
            collections = self._get_database_collections(database)
            
            return {
                'database': database,
                'database_path': database_path,
                'collections': collections
            }
        else:
            return {}

    def _disconnect(self):
        self._cache.clear()
        return None

    def _get_source_directory(self):
        """
        Get the root directory containing database subdirectories.
        This is the source root directory.
        """
        connection_properties = self.properties['connection']
        source_directory = connection_properties.get('source_directory', '.') 
        absolute_source_directory = os.path.abspath(source_directory)
        # make sure it exists, create if not
        os.makedirs(absolute_source_directory, exist_ok=True)
        return absolute_source_directory

    def _get_database_path(self, database):
        """Get path to database directory. Uses 'default' if database is None."""
        if database is None:
            database = 'default'
        source_directory = self._get_source_directory()
        return os.path.join(source_directory, database)

    def _get_database_collections(self, database):
        """Scan database directory for BN model collections."""
        database_path = self._get_database_path(database)
        collections = []
        if os.path.exists(database_path):
            for item in os.listdir(database_path):
                item_path = os.path.join(database_path, item)
                if os.path.isdir(item_path):
                    model_bif_path = os.path.join(item_path, 'model.bif')
                    if os.path.exists(model_bif_path):
                        collections.append(item)
        return sorted(collections)

    def _get_collection_path(self, database, collection):
        database_path = self._get_database_path(database)
        return os.path.join(database_path, collection)

    def _load_model(self, database, collection):
        """Load BN model for a collection, using cache if available."""
        if database not in self._cache:
            self._cache[database] = {}
        
        if collection in self._cache[database]:
            return self._cache[database][collection]['model']
        
        collection_path = self._get_collection_path(database, collection)
        
        if not os.path.exists(collection_path):
            raise FileNotFoundError(f"BN model not found: {collection_path}")
        
        # Load model
        model = load_pgmpy_model(collection_path)
        
        # Load graph_structure
        graph_structure_path = os.path.join(collection_path, 'graph_structure.json')
        graph_structure = None
        if os.path.exists(graph_structure_path):
            with open(graph_structure_path, 'r') as f:
                graph_structure = json.load(f)
        
        # Cache both model and graph_structure together
        self._cache[database][collection] = {
            'model': model,
            'graph_structure': graph_structure
        }
        
        return model

    def _build_graph_structure_from_model(self, model):
        """Build graph_structure dictionary from a pgmpy model.
        
        Args:
            model: A pgmpy BayesianNetwork model instance.
            
        Returns:
            dict: Graph structure with nodes, edges, markov_blanket, and descriptions.
        """
        graph_structure = {
            "description": "",
            "nodes": {},
            "edges": {},
            "markov_blanket": {}
        }
        
        # Extract nodes and their states
        for node in model.nodes():
            cpd = model.get_cpds(node)
            node_states = cpd.state_names.get(node, [])
            # Build states_description dict with empty strings
            states_description = {state: "" for state in node_states}
            graph_structure["nodes"][node] = {
                "name": node,
                "states": node_states,
                "description": "",
                "states_description": states_description
            }
        
        # Extract edges from model
        for edge in model.edges():
            parent, child = edge
            if parent not in graph_structure["edges"]:
                graph_structure["edges"][parent] = []
            graph_structure["edges"][parent].append(child)
        
        # Extract markov blankets from model
        for node in model.nodes():
            markov_blanket = model.get_markov_blanket(node)
            # Convert set to list for JSON serialization
            graph_structure["markov_blanket"][node] = list(markov_blanket) if markov_blanket else []
        
        return graph_structure

    def _load_graph_structure(self, database, collection):
        """Load graph_structure.json for a collection, using cache if available.
        If graph_structure.json doesn't exist, builds it from the model."""
        if database not in self._cache:
            self._cache[database] = {}
        
        if collection in self._cache[database]:
            graph_structure = self._cache[database][collection].get('graph_structure')
            if graph_structure:
                return graph_structure
        
        # If not cached, load model (which will also load and cache graph_structure if file exists)
        model = self._load_model(database, collection)
        
        # Check if graph_structure was loaded from file
        graph_structure = self._cache[database][collection].get('graph_structure')
        
        # If graph_structure not available, build it from model
        if not graph_structure:
            graph_structure = self._build_graph_structure_from_model(model)
            # Cache the built graph_structure
            self._cache[database][collection]['graph_structure'] = graph_structure
        
        return graph_structure

    ######### source
    def fetch_metadata(self):
        """
        Fetch metadata for the BN source.

        Returns:
            dict: Metadata about the source.
        """
        return {}

    def fetch_schema(self):
        """
        Fetch schema for source.

        Returns:
            dict: Schema dictionary
        """
        return {}

    ######### database
    def fetch_databases(self):
        """
        List all BN databases in the configured source directory.

        Returns:
            list[str]: Names of database directories, including 'default'.
        """
        source_directory = self._get_source_directory()
        
        
        dbs = []
        if not os.path.exists(source_directory):
            return dbs
        
        for item in os.listdir(source_directory):
            item_path = os.path.join(source_directory, item)
            if os.path.isdir(item_path):
                dbs.append(item)
        
        # Ensure 'default' is in the list
        if 'default' not in dbs:
            dbs.append('default')
        
        return sorted(dbs)

    def fetch_database_metadata(self, database):
        """
        Fetch metadata for a specific database.

        Parameters:
            database (str): Database name.

        Returns:
            dict: Metadata dictionary containing database name, collection count, database path, and description.
        """
        database_path = self._get_database_path(database)
        
        if not os.path.exists(database_path):
            return {}
        
        collections = self.fetch_database_collections(database)
        
        return {
            "database": database,
            "collection_count": len(collections),
            "database_path": database_path,
            "description": f"Bayesian Network database '{database}' containing {len(collections)} BN model collection(s): {', '.join(collections)} for causal/probabilistic reasoning"
        }

    def fetch_database_schema(self, database):
        """
        Fetch schema for a specific database.

        Parameters:
            database (str): Database name.

        Returns:
            dict: Schema dictionary (currently empty for BN source).
        """
        return {}

    def create_database(self, database, properties={}, overwrite=False):
        """
        Create a new BN database directory.
        Uses 'default' if database is None.

        Parameters:
            database (str): Name of the database to create. If None, uses 'default'.
            properties (dict, optional): Additional properties (unused).
            overwrite (bool, optional): If True, overwrite existing database directory.

        Returns:
            dict: Status of the operation with "status" and "message" keys.
        """
        if database is None:
            database = 'default'
        
        database_path = self._get_database_path(database)
        
        if os.path.exists(database_path):
            if overwrite:
                import shutil
                shutil.rmtree(database_path)
                # Invalidate cache when overwriting
                if database in self._cache:
                    del self._cache[database]
            else:
                return {"status": "skipped", "message": f"Database '{database}' already exists"}
        
        os.makedirs(database_path, exist_ok=True)
        return {"status": "success", "message": f"Database '{database}' created"}

    ######### database/collection
    def fetch_database_collections(self, database):
        """
        Fetch the list of BN model collections in the specified database.
        Uses 'default' if database is None.

        Parameters:
            database (str): The name of the database. If None, uses 'default'.

        Returns:
            list[str]: Names of BN model collections (directories containing model.bif).
        """
        if database is None:
            database = 'default'
        
        # Get collections from cache (already loaded) and directory scan (all collections)
        cached_collections = set()
        if database in self._cache:
            cached_collections = set(self._cache[database].keys())
        
        # Scan directory for all collections (including unloaded ones)
        all_collections = set(self._get_database_collections(database))
        
        # Return union of cached and scanned collections, sorted
        return sorted(cached_collections | all_collections)

    def create_database_collection(self, database, collection, properties={}, overwrite=False):
        """
        Create a new BN model collection.
        Not supported in current version - collections must be created manually.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection (BN model) to create.
            properties (dict, optional): Additional properties (unused).
            overwrite (bool, optional): Overwrite flag (unused).

        Returns:
            dict: Status indicating that collection creation is not supported.
        """
        return {"status": "not_applicable"}

    def fetch_database_collection_metadata(self, database, collection):
        """
        Fetch metadata for a given BN model collection.
        Uses 'default' if database is None.

        Parameters:
            database (str): The name of the database. If None, uses 'default'.
            collection (str): The name of the collection (BN model).

        Returns:
            dict: Metadata dictionary containing collection name, node count, edge count, and graph structure.
        """
        if database is None:
            database = 'default'
        graph_structure = self._load_graph_structure(database, collection)
        
        if graph_structure:
            nodes = graph_structure.get("nodes", {})
            edges = graph_structure.get("edges", {})
            node_count = len(nodes)
            edge_count = sum(len(children) for children in edges.values())
            description = graph_structure.pop("description", None)
            if not description:
                description = f"Bayesian Network collection '{collection}' with {node_count} nodes and {edge_count} edges for causal/probabilistic reasoning"
            metadata = {
                "description": description,
                "collection": collection,
                "node_count": node_count,
                "edge_count": edge_count,
                "graph_structure": graph_structure,
            }
            return metadata
        
        try:
            model = self._load_model(database, collection)
            return {
                "collection": collection,
                "node_count": len(model.nodes()),
                "edge_count": len(model.edges())
            }
        except Exception:
            return {}

    def fetch_database_collection_entities(self, database, collection):
        """
        Fetch entities (BN nodes) for a collection.

        Parameters:
            database (str): Name of the database. If None, uses 'default'.
            collection (str): Name of the collection (BN model).

        Returns:
            dict: Entity schema dictionary mapping node names to their properties and states,
                  including graph structure knowledge.
        """
        if database is None:
            database = 'default'
        
        # Load graph_structure (will build from model if needed)
        graph_structure = self._load_graph_structure(database, collection)
        
        # Fallback: if _load_graph_structure somehow returns None, try to build from model
        if not graph_structure:
            # load model and build graph_structure
            if database in self._cache and collection in self._cache[database]:
                model = self._cache[database][collection].get('model')
            else:
                try:
                    model = self._load_model(database, collection)
                except Exception as e:
                    self.logger.warning(f"Failed to load model for {collection}: {e}")
                    return {}
            
            if model:
                # Build graph_structure from model using shared method
                graph_structure = self._build_graph_structure_from_model(model)
                # Cache the graph_structure
                if database not in self._cache:
                    self._cache[database] = {}
                if collection not in self._cache[database]:
                    self._cache[database][collection] = {}
                self._cache[database][collection]['graph_structure'] = graph_structure
            else:
                self.logger.warning(f"Model not available for {collection}")
                return {}
        
        schema = DataSchema()
        nodes = graph_structure.get("nodes", {})
        edges = graph_structure.get("edges", {})
        markov_blankets = graph_structure.get("markov_blanket", {})
        
        for node_name, node_info in nodes.items():
            if not schema.has_entity(node_name):
                schema.add_entity(node_name)
            
            entity_obj = schema.entities[node_name]
            
            if "description" in node_info:
                entity_obj["description"] = node_info["description"]
            
            # Add graph structure knowledge to entity properties
            graph_knowledge = {}
            
            # Add parent nodes
            parents = [parent for parent, children in edges.items() if node_name in children]
            if parents:
                graph_knowledge["parents"] = parents
            
            # Add child nodes
            if node_name in edges:
                graph_knowledge["children"] = edges[node_name]
            
            # Add Markov blanket
            if node_name in markov_blankets:
                graph_knowledge["markov_blanket"] = markov_blankets[node_name]
            
            # Store graph knowledge in properties
            if graph_knowledge:
                entity_obj["properties"]["graph_structure"] = graph_knowledge
            
            # Attributes (states) are not exposed in this version
        
        return schema.get_entities()

    def fetch_database_collection_relations(self, database, collection):
        """
        Fetch relationships for a database collection.
        Not applicable for BN source - graph structure is included in entity properties.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.

        Returns:
            dict: Empty dict - relations not used for BN source.
        """
        return {}

    def fetch_database_collection_entity_metadata(self, database, collection, entity):
        """
        Fetch metadata for a specific entity (BN node).
        Uses 'default' if database is None.

        Parameters:
            database (str): Name of the database. If None, uses 'default'.
            collection (str): Name of the collection.
            entity (str): Name of the entity (node).

        Returns:
            dict: Metadata dictionary containing node name, state count, and description.
        """
        if database is None:
            database = 'default'
        graph_structure = self._load_graph_structure(database, collection)
        
        if graph_structure:
            nodes = graph_structure.get("nodes", {})
            if entity in nodes:
                node_info = nodes[entity]
                states = node_info.get("states", [])
                metadata = {
                    "description": node_info.get("description", ""),
                    "state_count": len(states),
                    "states": states,
                }
                if "states_description" in node_info:
                    metadata["states_description"] = node_info["states_description"]
                return metadata
        
        return {}

    def fetch_database_collection_entity_attributes(self, database, collection, entity):
        """
        Fetch attributes (states) for a specific entity (BN node).
        Uses 'default' if database is None.

        Parameters:
            database (str): Name of the database. If None, uses 'default'.
            collection (str): Name of the collection.
            entity (str): Name of the entity (node).

        Returns:
            dict: Dictionary mapping state names to their attribute definitions.
        """
        # Attributes (states) are not exposed in this version
        return {}

    def fetch_database_collection_relation_metadata(self, database, collection, relation):
        """
        Fetch metadata for a specific relation.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.

        Returns:
            dict: Relation metadata (currently empty for BN source).
        """
        return {}

    def fetch_database_collection_relation_attributes(self, database, collection, relation):
        """
        Fetch attributes for a specific relation.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.

        Returns:
            dict: Relation attributes (currently empty for BN source).
        """
        return {}

    ######### source/database/collection/entity
    def create_database_collection_entity(self, database, collection, entity, properties={}, overwrite=False):
        """
        Create a new entity (BN node).

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.
            entity (str): Name of the entity (node).
            properties (dict, optional): Additional properties (unused).
            overwrite (bool, optional): Overwrite flag (unused).

        Returns:
            dict: Status indicating that entities are derived from the model.
        """
        return {"status": "not_applicable"}

    ######### source/database/collection/relation
    def create_database_collection_relation(self, database, collection, relation, properties={}, overwrite=False):
        """
        Create a new relation.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            properties (dict, optional): Additional properties (unused).
            overwrite (bool, optional): Overwrite flag (unused).

        Returns:
            dict: Status indicating that relations are derived from the model.
        """
        return {"status": "not_applicable"}

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """
        Execute a probability inference query on a BN model.

        Query format:
        {
            "target_node": <target node name>,
            "target_state": <target state name>,
            "context": {
                <context node 1 name>: <context node 1 state>,
                <context node 2 name>: <context node 2 state>,
                ...
            }
        }

        Parameters:
            query (str): JSON-formatted query string.
            database (str, optional): Database name. If None, uses 'default'.
            collection (str, optional): BN model name (collection). Must be provided.
            optional_properties (dict, optional): Additional query options (unused).

        Returns:
            list[dict]: List containing a single result dictionary with probability information.

        Raises:
            Exception: If collection is not provided.
            ValueError: If query format is invalid or nodes/states are not found.
        """
        if database is None:
            database = 'default'
        
        if collection is None:
            raise Exception("No collection (BN model) provided")
        
        try:
            query_dict = json.loads(query) if isinstance(query, str) else query
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid query JSON: {e}")
        
        target_node = query_dict.get("target_node")
        target_state = query_dict.get("target_state")
        context = query_dict.get("context", {})
        
        if not target_node:
            raise ValueError("Query must include 'target_node'")
        if not target_state:
            raise ValueError("Query must include 'target_state'")
        
        try:
            model = self._load_model(database, collection)
        except FileNotFoundError as e:
            raise Exception(f"BN model not found: {e}")
        
        model_nodes = set(model.nodes())
        if target_node not in model_nodes:
            raise ValueError(f"Target node '{target_node}' not found in model. Available nodes: {sorted(model_nodes)}")
        
        evidence = {}
        
        for node_name, state_name in context.items():
            if node_name not in model_nodes:
                raise ValueError(f"Context node '{node_name}' not found in model. Available nodes: {sorted(model_nodes)}")
            
            cpd = model.get_cpds(node_name)
            node_states = cpd.state_names.get(node_name, [])
            if state_name not in node_states:
                raise ValueError(f"State '{state_name}' not found in node '{node_name}'. Available states: {node_states}")
            
            evidence[node_name] = state_name
        
        try:
            inference = VariableElimination(model)
            query_result = inference.query(
                variables=[target_node],
                evidence=evidence if evidence else None
            )
            
            state_names = list(query_result.state_names[target_node])
            
            if target_state not in state_names:
                raise ValueError(f"State '{target_state}' not found in node '{target_node}'. Available states: {state_names}")
            
            state_index = state_names.index(target_state)
            probability = float(query_result.values[state_index])
            
            result = {
                "target_node": target_node,
                "target_state": target_state,
                "probability": probability,
                "probability_percent": round(probability * 100, 2),
                "context": context
            }
            
            state_probs = {}
            for i, state in enumerate(state_names):
                state_probs[state] = float(query_result.values[i])
            result["all_state_probabilities"] = state_probs
            
            # Add explanation if requested
            explanation_requested = optional_properties.get('explanation', False)
            if explanation_requested:
                explanation = self._generate_explanation(
                    database, collection, target_node, target_state, context,
                    structured=optional_properties.get('structured_explanation', False),
                    max_num_paths=optional_properties.get('max_num_paths', 50),
                    probability=probability
                )
                result["explanation"] = explanation
            
            return [result]
            
        except Exception as e:
            self.logger.error(f"Error during inference: {e}")
            raise Exception(f"Inference failed: {e}")

    def _generate_explanation(self, database, collection, target_node, target_state, context, structured=False, max_num_paths=50, probability=None):
        """Generate explanation by traversing graph structure to find reasoning paths.
        
        Parameters:
            database (str): Database name.
            collection (str): Collection name.
            target_node (str): Target node being queried.
            target_state (str): Target state.
            context (dict): Context/evidence nodes and their states.
            structured (bool): Whether to return structured explanation.
            max_num_paths (int): Maximum number of reasoning paths to include (default: 50).
            probability (float, optional): The calculated probability value to include in explanation.
        
        Returns:
            str or dict: Natural language explanation or structured explanation.
        """
        graph_structure = self._load_graph_structure(database, collection)
        if not graph_structure:
            return "Explanation not available: graph structure not found."
        
        nodes = graph_structure.get("nodes", {})
        edges = graph_structure.get("edges", {})
        
        # Build NetworkX directed graph from edges
        G = nx.DiGraph()
        for parent, children in edges.items():
            for child in children:
                G.add_edge(parent, child)
        
        # Find all reasoning paths from context nodes to target node using networkx
        reasoning_paths = []
        for context_node, context_state in context.items():
            if context_node in G and target_node in G:
                try:
                    # Find all simple paths from context_node to target_node
                    # Limit paths per context node to avoid explosion, but collect up to max_num_paths total
                    paths = list(nx.all_simple_paths(G, context_node, target_node, cutoff=10))
                    for path in paths:
                        if len(reasoning_paths) >= max_num_paths:
                            break
                        reasoning_paths.append({
                            "start_node": context_node,
                            "start_state": context_state,
                            "path": path,
                            "target_node": target_node,
                            "target_state": target_state
                        })
                    if len(reasoning_paths) >= max_num_paths:
                        break
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    # No path found or node not in graph
                    pass
        
        if structured:
            result = {
                "reasoning_paths": reasoning_paths,
                "target_node": target_node,
                "target_state": target_state,
                "context": context
            }
            if probability is not None:
                result["probability"] = probability
                result["probability_percent"] = round(probability * 100, 2)
            return result
        else:
            # Generate natural language explanation, currently template filling is used. In the future, we can use LLM to generate the explanation.
            explanation_parts = []
            
            if context:
                explanation_parts.append(f"Given the evidence:")
                for ctx_node, ctx_state in context.items():
                    node_desc = nodes.get(ctx_node, {}).get("description", ctx_node)
                    explanation_parts.append(f"  - {ctx_node} ({node_desc}) is {ctx_state}")
            
            if reasoning_paths:
                explanation_parts.append(f"\nThe probability of {target_node} being {target_state} is influenced through the following reasoning paths:")
                # Limit displayed paths to max_num_paths (already limited during collection)
                for i, path_info in enumerate(reasoning_paths[:max_num_paths], 1):
                    path = path_info["path"]
                    path_str = " → ".join(path)
                    explanation_parts.append(f"  Path {i}: {path_str}")
            
            target_desc = nodes.get(target_node, {}).get("description", target_node)
            if probability is not None:
                prob_percent = round(probability * 100, 2)
                explanation_parts.append(f"\nBased on the Bayesian Network structure and the provided evidence, the probability of {target_node} ({target_desc}) being {target_state} is {prob_percent}% ({probability:.6f}).")
            else:
                explanation_parts.append(f"\nBased on the Bayesian Network structure and the provided evidence, the probability of {target_node} ({target_desc}) being {target_state} is calculated.")
            
            return "\n".join(explanation_parts) if explanation_parts else "Explanation not available."
    

    ######### stats
    def fetch_source_stats(self):
        """
        Fetch source-level statistics for the BN source.

        Returns:
            dict: Empty dict - stats not applicable for BN source.
        """
        return {}

    def fetch_database_stats(self, database):
        """
        Fetch statistics for a specific database.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: Empty dict - stats not applicable for BN source.
        """
        return {}

    def fetch_collection_stats(self, database, collection_name, entities, relations):
        """
        Collect statistics for a database collection (BN model).

        Parameters:
            database (str): Name of the database.
            collection_name (str): Name of the collection.
            entities (dict): Entity schema dictionary.
            relations (dict): Relation schema dictionary.

        Returns:
            dict: Empty dict - stats not applicable for BN source.
        """
        return {}

    def fetch_entity_stats(self, database, collection, entity):
        """
        Fetch statistics for a specific entity (BN node).

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.
            entity (str): Name of the entity (node).

        Returns:
            dict: Empty dict - stats not applicable for BN source.
        """
        return {}

    def fetch_property_stats(self, database, collection, entity, property_name, sample_limit=None):
        """
        Fetch statistics for a specific property (state) of an entity.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.
            entity (str): Name of the entity (node).
            property_name (str): Name of the property (state).
            sample_limit (int, optional): Sample limit (unused for BN source).

        Returns:
            dict: Empty dict - stats not applicable for BN source.
        """
        return {}

