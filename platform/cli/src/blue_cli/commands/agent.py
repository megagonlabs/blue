import click
from click import Context
from blue_cli.helper import show_output, bcolors
from blue_cli.manager import AgentRegistryManager  
import json



@click.group(help="Interact with agent registry")
@click.option("--profile_name", default=None, required=False, help="name of the profile, default is selected profile")
@click.option("--output", default="table", type=str, help="Output format (table|json|csv)")
@click.option("--query", default="$", required=False, type=str, help="Query on output results")
@click.pass_context
def agent(ctx, profile_name, output, query):
    """Initialize agent CLI context"""
    global agent_registry_mgr
    agent_registry_mgr = AgentRegistryManager(profile_name=profile_name)
    ctx.ensure_object(dict)
    ctx.obj["profile_name"] = profile_name
    ctx.obj["output"] = output
    ctx.obj["query"] = query


def flatten_agents(agent_dict, parent_path=""):
    """
    Flatten only agent entries (type == 'agent').
    Recurses into nested contents to find nested agents.
    Yields dicts: {"path": path, "data": data}
    """
    flat = []
    for name, data in (agent_dict or {}).items():
        if not isinstance(data, dict):
            continue
        path = f"{parent_path}/{name}" if parent_path else name

        if data.get("type") == "agent":
            flat.append({"path": path, "data": data})

        contents = data.get("contents", {})
        if isinstance(contents, dict):
            if "agent" in contents and isinstance(contents["agent"], dict):
                flat.extend(flatten_agents(contents["agent"], path))
            else:
                for subkey, subval in contents.items():
                    if isinstance(subval, dict):
                        if subval.get("type") == "agent":
                            flat.extend(flatten_agents({subkey: subval}, path))
                        else:
                            sub_contents = subval.get("contents", {})
                            if isinstance(sub_contents, dict) and "agent" in sub_contents:
                                flat.extend(flatten_agents(sub_contents["agent"], f"{path}/{subkey}"))
    
    return flat


def flatten_groups(group_dict, parent_path=""):
    """
    Flatten only agent_group entries (type == 'agent_group').
    Recurse into nested groups (agent_group under contents).
    """
    flat = []
    for name, data in (group_dict or {}).items():
        if not isinstance(data, dict):
            continue
        path = f"{parent_path}/{name}" if parent_path else name

        if data.get("type") == "agent_group":
            flat.append({"path": path, "data": data})

        contents = data.get("contents", {})
        if isinstance(contents, dict):
            if "agent_group" in contents and isinstance(contents["agent_group"], dict):
                flat.extend(flatten_groups(contents["agent_group"], path))
            else:
                # If agent_group nested under arbitrary keys
                for subkey, subval in contents.items():
                    if isinstance(subval, dict) and subval.get("type") == "agent_group":
                        flat.extend(flatten_groups({subkey: subval}, path))
    return flat

def collect_agents_and_groups(data):
    
    agents, agent_groups = {}, {}
    if not isinstance(data, dict):
        return agents, agent_groups

    if "agent" in data and isinstance(data["agent"], dict):
        agents.update(data["agent"])
    if "agent_group" in data and isinstance(data["agent_group"], dict):
        agent_groups.update(data["agent_group"])
    if "agents" in data and isinstance(data["agents"], dict):
        agents.update(data["agents"])

    for value in data.values():
        if isinstance(value, dict):
            sub_agents, sub_groups = collect_agents_and_groups(value)
            agents.update(sub_agents)
            agent_groups.update(sub_groups)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    sub_agents, sub_groups = collect_agents_and_groups(item)
                    agents.update(sub_agents)
                    agent_groups.update(sub_groups)

    return agents, agent_groups

def collect_agents_io(data):
    """
    Recursively collect agents, agent_groups, inputs, outputs from JSON
    """
    agents, agent_groups, inputs, outputs = {}, {}, {}, {}

    if isinstance(data, dict):
        t = data.get("type")
        name = data.get("name")
        scope = data.get("scope", "/")

        if t == "agent" and name:
            path = f"{scope.rstrip('/')}/agent/{name}"
            agents[path] = data
        elif t == "agent_group" and name:
            path = f"{scope.rstrip('/')}/agent_group/{name}"
            agent_groups[path] = data
        elif t == "input" and name:
            inputs.setdefault(data.get("scope", ""), {})[name] = data
        elif t == "output" and name:
            outputs.setdefault(data.get("scope", ""), {})[name] = data

        for v in data.values():
            sub_agents, sub_groups, sub_inputs, sub_outputs = collect_agents_io(v)
            agents.update(sub_agents)
            agent_groups.update(sub_groups)
            for k, d in sub_inputs.items():
                inputs.setdefault(k, {}).update(d)
            for k, d in sub_outputs.items():
                outputs.setdefault(k, {}).update(d)

    elif isinstance(data, list):
        for item in data:
            sub_agents, sub_groups, sub_inputs, sub_outputs = collect_agents_io(item)
            agents.update(sub_agents)
            agent_groups.update(sub_groups)
            for k, d in sub_inputs.items():
                inputs.setdefault(k, {}).update(d)
            for k, d in sub_outputs.items():
                outputs.setdefault(k, {}).update(d)

    return agents, agent_groups, inputs, outputs


def make_key(entity):
    scope = entity.get("scope", "/") or "/"
    name = entity.get("name")
    return f"{scope.rstrip('/')}/{name}" if name else None

def normalize_io(io_list_or_dict):
    """
    Convert the registry input/output to a dict keyed by 'name'.
    Accepts a list of items or a dict.
    """
    if isinstance(io_list_or_dict, dict):
        # Could be empty dict {}
        return {item["name"]: item for item in io_list_or_dict.values()} if io_list_or_dict else {}
    elif isinstance(io_list_or_dict, list):
        return {item["name"]: item for item in io_list_or_dict}
    return {}

def compute_properties_diff(local_props, reg_props):
    """
    Compare local vs registry properties, return dict of changed properties.
    """
    changes = {}
    
    for prop_name, prop_value in local_props.items():
        if reg_props.get(prop_name) != prop_value:
            changes[prop_name] = prop_value
    return changes

def compute_io_diff(local_io, registry_io):
    """Compare input/output sections (dicts) and return diff with added/updated"""
    added, updated = {}, {}
    registry_io = normalize_io(registry_io)  # normalize first
    for name, local_item in local_io.items():
        reg_item = registry_io.get(name)
        if not reg_item:
            added[name] = local_item
        elif local_item.get("description") != reg_item.get("description") or local_item.get("properties") != reg_item.get("properties"):
            updated[name] = local_item

    return {"added": added, "updated": updated}

def compute_simple_diff(old_obj, new_obj, keys=None):
    """
    Compare only relevant fields of two agent or group dictionaries.
    Returns a dict of changes (old vs new) or empty dict if no difference.
    """
    if keys is None:
        keys = ["description", "properties"]

    diff = {}
    for k in keys:
        old_val = old_obj.get(k)
        new_val = new_obj.get(k)
        if old_val != new_val:
            diff[k] = {"old": old_val, "new": new_val}
    return diff


def build_registry_map(entities):
    """Build a map of registry entities keyed by scope/name"""
    reg_map = {}
    for e in entities:
        if not isinstance(e, dict):
            continue
        key = make_key(e)
        if key:
            reg_map[key] = e
    return reg_map

def build_io_map(io_list):
    """Convert list of inputs/outputs to dict keyed by 'name'"""
    io_map = {}
    if not io_list:
        return io_map
    for item in io_list:
        if isinstance(item, dict) and "name" in item:
            io_map[item["name"]] = item
    return io_map

def check_fatal_error(err, context=""):
    """
    Detect fatal registry errors and signal the caller to break.
    Returns True if a fatal error was found.
    """
    if not err:
        return False

    err_str = str(err).lower()
    if "internal server error" in err_str or "500" in err_str:
        click.echo(f"\n Fatal error encountered during {context}: {err}")
        click.echo("Stopping further updates to avoid inconsistent registry state.\n")
        return True  
    return False

@agent.command(help="Update agent registry from JSON file. Input JSON file contains list of registry entries.")
@click.argument("json_file", type=click.Path(exists=True))
@click.option("--auto", is_flag=True, help="Auto import all changes without interactive verification")
@click.pass_context
def update(ctx, json_file, auto):
    """
    Update agents and agent groups from a JSON file with the live agent registry.
    Compares scope-aware entities and shows detailed diffs.
    """
    with open(json_file) as f:
        input_data = json.load(f)

    raw_agents, raw_agent_groups, raw_inputs, raw_outputs = collect_agents_io(input_data)

    input_flat_agents = flatten_agents(raw_agents)
    input_flat_groups = flatten_groups(raw_agent_groups)

    # ------------------------------
    # Build type-separated maps
    # ------------------------------
    input_agent_map = {a["path"]: a["data"] for a in input_flat_agents}
    input_group_map = {g["path"]: g["data"] for g in input_flat_groups}

    input_agents = {}
    input_groups = {}
    
    for data in input_agent_map.values():
        key = make_key(data)
        if key:
            input_agents[key] = data
    
    for data in input_group_map.values():
        key = make_key(data)
        if key:
            input_groups[key] = data

    # ------------------------------
    # Build agent -> IO mapping
    # ------------------------------
    agent_io_map = {}
    for scope, input_dict in raw_inputs.items():
        if scope.startswith("/agent/"):
            agent_name = scope.split("/agent/")[-1].split("/")[0]
            agent_io_map.setdefault(agent_name, {})["inputs"] = input_dict

    for scope, output_dict in raw_outputs.items():
        if scope.startswith("/agent/"):
            agent_name = scope.split("/agent/")[-1].split("/")[0]
            agent_io_map.setdefault(agent_name, {})["outputs"] = output_dict
    

    # ------------------------------
    # Fetch registry entries
    # ------------------------------
    agents, err = agent_registry_mgr.get_agents(recursive=True)
    if err:
        click.echo(f"Error fetching agents: {err}")
        return

    agent_groups, err2 = agent_registry_mgr.get_agent_groups()
    if err2:
        click.echo(f"Error fetching agent groups: {err2}")
        return

    # Fetch agents under each agent group 
    group_agents = []
    for group in agent_groups:
        g_name = group.get("name")
        if not g_name:
            continue
        group_data, group_err = agent_registry_mgr.get_agent_group(g_name)

        if group_err:
            print(f"Warning: could not fetch group {g_name}: {group_err}")
            continue

        collected_agents, _, _, _ = collect_agents_io(group_data)
        for a in collected_agents.values():
            if isinstance(a, dict):
                a_scope = f"/agent_group/{g_name}"
                if "scope" not in a or not a["scope"]:
                    a["scope"] = a_scope
                group_agents.append(a)
        
        
    # Merge top-level and group agents
    all_registry_agents = agents + group_agents

    registry_agents = build_registry_map(all_registry_agents)
    registry_groups = build_registry_map(agent_groups)

    # ------------------------------
    # Compare input vs registry (agents)
    # ------------------------------
    mismatches_agents = []
    for key, input_agent in input_agents.items():
        reg_agent = registry_agents.get(key)
        if not reg_agent:
            mismatches_agents.append({"key": key, "input": input_agent, "registry": None})
        else:
            diff = compute_simple_diff(reg_agent, input_agent)
            if diff:
                mismatches_agents.append({"key": key, "input": input_agent, "registry": reg_agent, "diff": diff})

    # ------------------------------
    # Compare input vs registry (agent groups)
    # ------------------------------
    mismatches_groups = []
    for key, input_group in input_groups.items():
        reg_group = registry_groups.get(key)
        if not reg_group:
            mismatches_groups.append({"key": key, "input": input_group, "registry": None})
        else:
            diff = compute_simple_diff(reg_group, input_group)
            if diff:
                mismatches_groups.append({"key": key, "input": input_group, "registry": reg_group, "diff": diff})

    # ------------------------------
    # Summarize differences
    # ------------------------------
    new_agents = [m for m in mismatches_agents if m["registry"] is None]
    modified_agents = [m for m in mismatches_agents if m["registry"] is not None]

    new_groups = [m for m in mismatches_groups if m["registry"] is None]
    modified_groups = [m for m in mismatches_groups if m["registry"] is not None]

    print("\nStarting interactive update for agent groups...")

    for mm in new_groups + modified_groups:
        key = mm["key"]
        input_group = mm["input"]
        reg_group = mm.get("registry")
        diff = mm.get("diff", {})

        click.echo("\n---------------------------")
        click.echo(f"Key: {key}")
        click.echo(f"Input Group:\n{json.dumps(input_group, indent=2)}")
        click.echo(f"Registry Group:\n{json.dumps(reg_group, indent=2) if reg_group else 'MISSING'}")

        if diff:
            click.echo(f"Diff:\n{json.dumps(diff, indent=2)}")

        # Auto-apply if --auto, otherwise prompt
        if auto:
            do_update = True
        else:
            do_update = click.prompt("Apply this change? [y/n]", default="n").lower() == "y"

        if not do_update:
            continue

        name = input_group.get("name")

        try:
            if reg_group is None:
                msg, err = agent_registry_mgr.add_agent_group(
                    name,
                    description=input_group.get("description"),
                    icon=input_group.get("icon"),
                    properties=input_group.get("properties")
                )
                if err:
                    click.echo(f" Failed to add group {name}: {err}")
                else:
                    click.echo(f" Added group {name}: {msg}")
                
                input_props = input_group.get("properties", {})
                for prop_name, prop_value in input_props.items():
                    msg, err = agent_registry_mgr.set_agent_group_property(name, prop_name, prop_value)
                    if check_fatal_error(err, f"adding agent group property for {name}"):
                        return  
                    if err:
                        click.echo(f" Failed to add property '{prop_name}' for {name}: {err}")
                    else:
                        click.echo(f"Added property '{prop_name}' for {name}")

            else:
                # Selectively update fields based on diff
                update_fields = {}
                for field in ["description", "icon", "properties"]:
                    if field in diff:
                        update_fields[field] = input_group.get(field)

                if update_fields:
                    msg, err = agent_registry_mgr.update_agent_group(
                        name,
                        description=update_fields.get("description"),
                        icon=update_fields.get("icon"),
                        properties=update_fields.get("properties")
                    )
                    if check_fatal_error(err, f"updating agent group {name}"):
                        return  
                    
                    if err:
                        click.echo(f" Failed to update group {name}: {err}")
                    else:
                        click.echo(f" Updated group {name}: {msg}")

                # Update changed properties individually
                if "properties" in diff:
                    input_props = input_group.get("properties", {})
                    reg_props = reg_group.get("properties", {})
                    for prop_name, prop_value in input_props.items():
                        if prop_name not in reg_props or reg_props[prop_name] != prop_value:
                            msg, err = agent_registry_mgr.set_agent_group_property(name, prop_name, prop_value)
                            if check_fatal_error(err, f"updating agent group property for {name}"):
                                return  
                            
                            if err:
                                click.echo(f" Failed to update property '{prop_name}' for {name}: {err}")
                            else:
                                click.echo(f"Updated property '{prop_name}' for {name}")

        except Exception as e:
            click.echo(f" Error updating group {name}: {e}")

    print("\nStarting interactive update for agents ...")

    for mm in new_agents + modified_agents:
        key = mm["key"]
        input_agent = mm["input"]
        reg_agent = mm.get("registry")
        diff = mm.get("diff", {})

        click.echo("\n---------------------------")
        click.echo(f"Key: {key}")
        click.echo(f"Input Agent:\n{json.dumps(input_agent, indent=2)}")
        click.echo(f"Registry Agent:\n{json.dumps(reg_agent, indent=2) if reg_agent else 'MISSING'}")

        if diff:
            click.echo(f"Diff:\n{json.dumps(diff, indent=2)}")
        
        # If --auto flag provided, auto-apply; otherwise prompt
        if auto:
            do_update_agent = True
        else:
            do_update_agent = click.prompt("Apply this change? [y/n]", default="n").lower() == "y"

        name = input_agent.get("name")
        agent_scope = input_agent.get("scope", "")

        try:
            if do_update_agent:
                if "/agent_group/" in agent_scope:
                    group_name = agent_scope.split("/agent_group/")[-1].split("/")[0]
                    if reg_agent is None:
                        msg, err = agent_registry_mgr.add_agent_to_agent_group(
                            group_name,
                            name,
                            description=input_agent.get("description"),
                            properties=input_agent.get("properties"),
                            rebuild=True
                        )
                        input_props = input_agent.get("properties", {})
                        for prop_name, prop_value in input_props.items():
                            msg, err = agent_registry_mgr.set_agent_property_in_agent_group(group_name, name, prop_name, prop_value)
                            if check_fatal_error(err, f"adding property for agent {name}"):
                                return
                            if err:
                                click.echo(f" Failed to add property '{prop_name}' for {name}: {err}")
                                
                            else:
                                click.echo(f" Adding property '{prop_name}' for {name}")
                    
                    
                    else:
                        update_fields = {}
                        for field in ["description", "icon", "properties"]:
                            if field in diff:
                                update_fields[field] = input_agent.get(field)

                        if update_fields:
                            msg, err = agent_registry_mgr.update_agent_in_agent_group(
                            group_name,
                            name,
                            description=update_fields.get("description"),
                            properties=None
                            )        
                            if check_fatal_error(err, f"updating agent {name}"):
                                return
                            if err:
                                click.echo(f" Failed to update {name}: {err}")
                            else:
                                click.echo(f" Updated {name}: {msg}")

                        # Update changed properties individually
                        if "properties" in diff:
                            input_props = input_agent.get("properties", {})
                            reg_props = reg_agent.get("properties", {})
                            for prop_name, prop_value in input_props.items():
                                if prop_name not in reg_props or reg_props[prop_name] != prop_value:
                                    msg, err = agent_registry_mgr.set_agent_property_in_agent_group(group_name, name, prop_name, prop_value)
                                    
                                    if check_fatal_error(err, f"updating property for agent {name}"):
                                        return
                            
                                    if err:
                                        click.echo(f" Failed to update property '{prop_name}' for {name}: {err}")
                                    else:
                                        click.echo(f" Updated property '{prop_name}' for {name}")

                else:
                    if reg_agent is None:
                        msg, err = agent_registry_mgr.add_agent(
                            name,
                            description=input_agent.get("description"),
                            icon=input_agent.get("icon"),
                            properties=input_agent.get("properties")
                        )
                        if err:
                            click.echo(f" Failed to add {name}: {err}")
                        else:
                            click.echo(f" Added {name}: {msg}")
                    
                        input_props = input_agent.get("properties", {})
                        for prop_name, prop_value in input_props.items():
                            msg, err = agent_registry_mgr.set_agent_property(name, prop_name, prop_value)
                            if check_fatal_error(err, f"adding property for agent {name}"):
                                return
                            if err:
                                click.echo(f" Failed to add property '{prop_name}' for {name}: {err}")
                            else:
                                click.echo(f" Added property '{prop_name}' for {name}")
                    
                    else:
                        update_fields = {}
                        for field in ["description", "icon", "properties"]:
                            if field in diff:
                                update_fields[field] = input_agent.get(field)
                    
                        if update_fields:
                            msg, err = agent_registry_mgr.update_agent(
                                name,
                                description=update_fields.get("description"),
                                icon=update_fields.get("icon"),
                                properties=None  
                            )
                            if check_fatal_error(err, f"updating agent {name}"):
                                return  
                            
                            if err:
                                click.echo(f" Failed to update {name}: {err}")
                            else:
                                click.echo(f" Updated {name}: {msg}")
                        
                        # Update changed properties individually
                        if "properties" in diff:
                            input_props = input_agent.get("properties", {})
                            reg_props = reg_agent.get("properties", {})
                            for prop_name, prop_value in input_props.items():
                                if prop_name not in reg_props or reg_props[prop_name] != prop_value:
                                    msg, err = agent_registry_mgr.set_agent_property(name, prop_name, prop_value)
                            
                                    if check_fatal_error(err, f"updating property for agent {name}"):
                                        return
                            
                                    if err:
                                        click.echo(f" Failed to update property '{prop_name}' for {name}: {err}")
                                    else:
                                        click.echo(f" Updated property '{prop_name}' for {name}")

            if "/agent_group/" in agent_scope:
                continue

            inputs_local = agent_io_map.get(name, {}).get("inputs", {})
            outputs_local = agent_io_map.get(name, {}).get("outputs", {})

            # --- Get current registry state ---
            reg_inputs, err_in = agent_registry_mgr.get_agent_inputs(name)
            reg_outputs, err_out = agent_registry_mgr.get_agent_outputs(name)

            if err_in or err_out:
                click.echo(f"Skipping IO update for {name} due to fetch error.")
                continue

            # Compare I/O
            if reg_inputs is None:
                reg_inputs = {}
            if reg_outputs is None:
                reg_outputs = {}

            input_diff = compute_io_diff(inputs_local, reg_inputs)
            click.echo(f"Input diff: {json.dumps(input_diff, indent=2)}")
            output_diff = compute_io_diff(outputs_local, reg_outputs)
            click.echo(f"Output diff: {json.dumps(output_diff, indent=2)}")

            # --- Apply input diffs ---
            for iname, data in input_diff["added"].items():
                click.echo(f"\n Input to add: {iname}")
                click.echo(json.dumps(data, indent=2))
                
                if auto:
                    apply_change = True
                else:
                    apply_change = click.prompt("Apply this input addition? [y/n]", default="n").lower() in ("y", "yes")

                if not apply_change:
                    continue
                
                
                msg, err = agent_registry_mgr.add_agent_input(name, param_name=iname, description=data.get("description"))
                if check_fatal_error(err, f"adding agent input for agent {name}"):
                    return  
                
                click.echo(f"Added input {iname}" if not err else f"Input add failed {iname}: {err}")

                # Apply properties individually
                for prop_name, prop_value in data.get("properties", {}).items():
                    msg, err = agent_registry_mgr.set_agent_input_property(name, iname, prop_name, prop_value)
                    if check_fatal_error(err, f"adding input property for agent {name}"):
                        return  
                
                    click.echo(f"Set input property '{prop_name}' for {iname}" if not err else f"Failed to set input property '{prop_name}' for {iname}: {err}")

            

            for iname, data in input_diff["updated"].items():
                click.echo(f"\nInput to update: {iname}")
                
                reg_inputs = build_io_map(reg_inputs)
                reg_item = reg_inputs.get(iname, {})
                reg_props = reg_item.get("properties", {}) if reg_item else {}
                local_props = data.get("properties", {})
                
                full_diff = {}
                for field in ["description"]:
                    if reg_item.get(field) != data.get(field):
                        full_diff[field] = {"old": reg_item.get(field), "new": data.get(field)}

                # Add property changes
                prop_changes = compute_properties_diff(local_props, reg_props)
                if prop_changes:
                    full_diff["properties"] = prop_changes

                click.echo("Diff:")
                click.echo(json.dumps(full_diff, indent=2))
                            
                if auto:
                    apply_change = True
                else:
                    apply_change = click.prompt("Apply this input update? [y/n]", default="n").lower() in ("y", "yes")

                if not apply_change:
                    continue
                
                
                msg, err = agent_registry_mgr.update_agent_input(name, param_name=iname, description=data.get("description"))
                if check_fatal_error(err, f"updating agent input for agent {name}"):
                    return  
                
                click.echo(f"Updated input {iname}" if not err else f"Input update failed {iname}: {err}")

                for prop_name, prop_value in prop_changes.items():
                    msg, err = agent_registry_mgr.set_agent_input_property(name, iname, prop_name, prop_value)
                    if check_fatal_error(err, f"updating agent input property for agent {name}"):
                        return  
                
                    click.echo(f"Updated input property '{prop_name}' for {iname}" if not err else f"Failed to update input property '{prop_name}' for {iname}: {err}")
                
            # --- Apply output diffs ---
            for oname, data in output_diff["added"].items():
                click.echo(f"\nOutput to add: {oname}")
                click.echo(json.dumps(data, indent=2))
                
                if auto:
                    apply_change = True
                else:
                    apply_change = click.prompt("Apply this output addition? [y/n]", default="n").lower() in ("y", "yes")

                if not apply_change:
                    continue
                
                msg, err = agent_registry_mgr.add_agent_output(name, param_name=oname, description=data.get("description"), properties=data.get("properties"))
                if check_fatal_error(err, f"adding agent output for agent {name}"):
                    return  
                
                click.echo(f"Added output {oname}" if not err else f"Output add failed {oname}: {err}")

                # Apply properties individually
                for prop_name, prop_value in data.get("properties", {}).items():
                    msg, err = agent_registry_mgr.set_agent_output_property(name, oname, prop_name, prop_value)
                    if check_fatal_error(err, f"adding agent output property for agent {name}"):
                        return  
                
                    click.echo(f"Set output property '{prop_name}' for {oname}" if not err else f"Failed to set output property '{prop_name}' for {oname}: {err}")

            
            for oname, data in output_diff["updated"].items():
                click.echo(f"\nOutput to update: {oname}")
                reg_outputs = build_io_map(reg_outputs)
                reg_item = reg_outputs.get(oname, {})
                reg_props = reg_item.get("properties", {}) if reg_item else {}
                local_props = data.get("properties", {})

                full_diff = {}
                for field in ["description"]:
                    if reg_item.get(field) != data.get(field):
                        full_diff[field] = {"old": reg_item.get(field), "new": data.get(field)}

                # Add property changes
                prop_changes = compute_properties_diff(local_props, reg_props)
                if prop_changes:
                    full_diff["properties"] = prop_changes

                click.echo("Diff:")
                click.echo(json.dumps(full_diff, indent=2))
                
                if auto:
                    apply_change = True
                else:
                    apply_change = click.prompt("Apply this output update? [y/n]", default="n").lower() in ("y", "yes")

                if not apply_change:
                    continue
                
                
                msg, err = agent_registry_mgr.update_agent_output(name, param_name=oname, description=data.get("description"))
                if check_fatal_error(err, f"updating agent output for agent {name}"):
                    return  
                
                click.echo(f"Updated output {oname}" if not err else f"Output update failed {oname}: {err}")

                for prop_name, prop_value in prop_changes.items():
                    msg, err = agent_registry_mgr.set_agent_output_property(name, oname, prop_name, prop_value)
                    if check_fatal_error(err, f"updating agent output property for agent {name}"):
                        return  
                
                    click.echo(f"Updated output property '{prop_name}' for {oname}" if not err else f"Failed to update output property '{prop_name}' for {oname}: {err}")

        except Exception as e:
            click.echo(f" Error updating {name}: {e}")

        click.echo("\n Update complete!")

if __name__ == "__main__":
    agent()  



