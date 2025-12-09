import json
import os
from pathlib import Path

import networkx as nx
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.readwrite import BIFReader, BIFWriter


""" Utility functions for saving Bayesian Network models. """
def save_pgmpy_model(model, model_dir_path):
    """Save a pgmpy model to a file with node and state mappings.
    
    This function handles models with special characters in node/state names
    by creating safe UID mappings before saving, then storing the mappings
    for later restoration.
    
    Parameters:
        model: pgmpy DiscreteBayesianNetwork model
        model_dir_path (str): Directory path where model and mappings will be saved
    
    Files created:
        - model.bif: The Bayesian network in BIF format (with safe UIDs)
        - node_mapping.json: Mapping from original node names to safe UIDs
        - state_mapping.json: Mapping from original state names to safe UIDs
    """
    # Ensure the directory exists
    Path(model_dir_path).mkdir(parents=True, exist_ok=True)
    
    # File paths
    model_path = os.path.join(model_dir_path, 'model.bif')
    node_mapping_path = os.path.join(model_dir_path, 'node_mapping.json')
    state_mapping_path = os.path.join(model_dir_path, 'state_mapping.json')
    
    # Generate node and state mappings
    node_mapping, state_mapping = generate_node_mapping(model)

    # Apply mapping to create a model suitable for saving
    model_with_mapping = apply_mapping_to_model_for_saving(model, node_mapping, state_mapping)
    
    # Save the model and the mappings
    save_model(model_with_mapping, model_path)
    save_mapping(node_mapping, node_mapping_path)
    save_mapping(state_mapping, state_mapping_path)

def generate_node_mapping(model):
    """Generate mappings for node names and state names.
    
    Creates mappings from original names (which may contain special characters
    that cause issues with pgmpy BIF format) to safe UIDs like 'node_0', 'state_0'.
    
    Parameters:
        model: pgmpy DiscreteBayesianNetwork model
    
    Returns:
        tuple: (node_mapping, state_mapping) dictionaries
            - node_mapping: {original_node_name: safe_uid, ...}
            - state_mapping: {original_state_name: safe_uid, ...}
    
    Note:
        State mapping is global across all nodes. If the same state name appears
        in different nodes, it will map to the same UID, which is typically desired.
    """
    # Generate node mapping: original name -> safe UID (node_0, node_1, ...)
    node_mapping = {node: f"node_{i}" for i, node in enumerate(sorted(model.nodes()))}
    
    # Collect all unique state names across all CPDs
    state_set = set()
    for cpd in model.get_cpds():
        for var_name in cpd.state_names:
            states = cpd.state_names[var_name]
            state_set.update(states)
    
    # Generate state mapping: original state name -> safe UID (state_0, state_1, ...)
    state_mapping = {state_name: f"state_{i}" for i, state_name in enumerate(sorted(state_set))}
    
    return node_mapping, state_mapping

def apply_mapping_to_model_for_saving(model, node_mapping, state_mapping):
    """Apply node and state mappings to model for safe saving.
    
    Creates a new model with safe UIDs replacing original names that may
    contain special characters incompatible with BIF format.
    
    Parameters:
        model: Original pgmpy DiscreteBayesianNetwork model
        node_mapping (dict): Mapping from original node names to safe UIDs
        state_mapping (dict): Mapping from original state names to safe UIDs
    
    Returns:
        DiscreteBayesianNetwork: New model with mapped names
    """
    relabeled_graph = nx.relabel_nodes(model, node_mapping, copy=True)
    relabeled_model = DiscreteBayesianNetwork(relabeled_graph.edges())
    new_cpds = []

    for cpd in model.get_cpds():
        new_variable = node_mapping.get(cpd.variable, cpd.variable)
        new_evidence = [node_mapping.get(var, var) for var in cpd.variables if var != cpd.variable]
        new_cpd = cpd.copy()
        new_cpd.variable = new_variable
        new_cpd.variables = [new_variable] + new_evidence

        # Update state names for the new variable mapping
        new_state_names = {node_mapping.get(k, k): [state_mapping.get(x, x) for x in v] for k, v in cpd.state_names.items()}
        new_cpd.state_names = new_state_names

        # Also update name_to_no and no_to_name to reflect the new variable names
        new_name_to_no = {}
        new_no_to_name = {}
        
        for var in cpd.variables:
            mapped_var = node_mapping.get(var, var)
            if var in cpd.name_to_no:
                new_name_to_no[mapped_var] = {state_mapping.get(k, k): v for k, v in cpd.name_to_no[var].items()}
            if var in cpd.no_to_name:
                new_no_to_name[mapped_var] = {k: state_mapping.get(v, v) for k, v in cpd.no_to_name[var].items()}

        new_cpd.name_to_no = new_name_to_no
        new_cpd.no_to_name = new_no_to_name

        new_cpds.append(new_cpd)

    # Add updated CPDs to the new model
    for new_cpd in new_cpds:
        relabeled_model.add_cpds(new_cpd)
        if not new_cpd.is_valid_cpd():
            raise ValueError(f"Invalid CPD for {new_cpd.variable}. Check state names and probabilities.")

    assert relabeled_model.check_model(), "The relabeled model is invalid"
    return relabeled_model


def save_model(model, model_path):
    """Save the Bayesian Network model to a BIF file.
    
    Parameters:
        model: pgmpy DiscreteBayesianNetwork model (with safe UIDs)
        model_path (str): Path where the BIF file will be saved
    """
    writer = BIFWriter(model)
    writer.write_bif(model_path)

def save_mapping(mapping, mapping_path):
    """Save a mapping dictionary to a JSON file.
    
    Parameters:
        mapping (dict): Mapping dictionary to save
        mapping_path (str): Path where the JSON file will be saved
    """
    with open(mapping_path, 'w') as file:
        json.dump(mapping, file, indent=4)



""" Utility functions for loading Bayesian Network models. """

def load_model(model_path):
    """Load a Bayesian Network model from a BIF file."""
    reader = BIFReader(model_path)
    model = reader.get_model()
    return model

def load_mapping(mapping_path):
    """Load a mapping dictionary from a JSON file.
    
    Parameters:
        mapping_path (str): Path to the JSON mapping file
    
    Returns:
        dict: The loaded mapping dictionary
    """
    with open(mapping_path, 'r') as file:
        mapping = json.load(file)
    return mapping

def translate_model(model, node_mapping, state_mapping):
    """Translate model node names and state names from safe UIDs back to original names.
    
    This reverses the mapping applied during saving, restoring the original
    node and state names (which may contain special characters).
    
    Parameters:
        model: pgmpy DiscreteBayesianNetwork model (with safe UIDs)
        node_mapping (dict): Original mapping {original_name: safe_uid}
        state_mapping (dict): Original mapping {original_state: safe_uid}
    
    Returns:
        DiscreteBayesianNetwork: Model with original names restored
    """
    reverse_node_mapping = {v: k for k, v in node_mapping.items()}
    reverse_state_mapping = {v: k for k, v in state_mapping.items()}
    relabeled_model = DiscreteBayesianNetwork([(reverse_node_mapping[x], reverse_node_mapping[y]) for x, y in model.edges()])
    
    for cpd in model.get_cpds():
        new_variable = reverse_node_mapping.get(cpd.variable, cpd.variable)
        new_evidence = [reverse_node_mapping.get(var, var) for var in cpd.variables if var != cpd.variable]
        new_cpd = cpd.copy()
        new_cpd.variable = new_variable
        new_cpd.variables = [new_variable] + new_evidence
        
        # Update state names, name_to_no, and no_to_name for the new variable mapping
        new_state_names = {reverse_node_mapping.get(var, var): [reverse_state_mapping.get(state, state) for state in cpd.state_names[var]] for var in cpd.state_names}
        new_cpd.state_names = new_state_names

        new_name_to_no = {reverse_node_mapping.get(var, var): {reverse_state_mapping.get(state, state): idx for state, idx in cpd.name_to_no[var].items()} for var in cpd.name_to_no}
        new_no_to_name = {reverse_node_mapping.get(var, var): {idx: reverse_state_mapping.get(state, state) for idx, state in cpd.no_to_name[var].items()} for var in cpd.no_to_name}

        new_cpd.name_to_no = new_name_to_no
        new_cpd.no_to_name = new_no_to_name

        relabeled_model.add_cpds(new_cpd)
    
    assert relabeled_model.check_model(), "The relabeled model is invalid after translation."
    return relabeled_model

def load_pgmpy_model(model_dir_path):
    """Load a pgmpy model from files along with its mappings and restore original names.
    
    Loads the model saved with safe UIDs and the corresponding mappings,
    then translates back to original node and state names.
    
    Parameters:
        model_dir_path (str): Directory path containing:
            - model.bif: The Bayesian network in BIF format
            - node_mapping.json: Mapping from original node names to safe UIDs
            - state_mapping.json: Mapping from original state names to safe UIDs
    
    Returns:
        DiscreteBayesianNetwork: Model with original names restored
    """
    model_path = os.path.join(model_dir_path, 'model.bif')
    node_mapping_path = os.path.join(model_dir_path, 'node_mapping.json')
    state_mapping_path = os.path.join(model_dir_path, 'state_mapping.json')

    model = load_model(model_path)
    node_mapping = load_mapping(node_mapping_path)
    state_mapping = load_mapping(state_mapping_path)
    print(f"# nodes: {len(model.nodes())}")
    print(f"# edges: {len(model.edges())}")
    print(f"# states: {len(state_mapping)}")

    return translate_model(model, node_mapping, state_mapping)
