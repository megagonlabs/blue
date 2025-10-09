###### Blue
from blue.constant import Separator
from blue.agent import Agent
from blue.registry import Registry
from blue.utils import json_utils
from blue.constant import Separator


###############
### AgentRegistry
#
class AgentRegistry(Registry):
    SEPARATOR = Separator.AGENT

    def __init__(self, name="AGENT_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, type='agent', id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization

    def _initialize_properties(self):
        super()._initialize_properties()

    ######### agent groups
    def add_agent_group(self, agent_group, created_by, description='', properties={}, rebuild=False):
        """
        Register a new agent group in the registry.

        Parameters:
            agent_group (str): Name of the agent group.
            created_by (str): Creator identifier.
            description (str, optional): Description for the group.
            properties (dict, optional): Additional metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """

        super().register_record(agent_group, 'agent_group', '/', created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_agent_group(self, agent_group, description='', icon=None, properties={}, rebuild=False):
        """
        Update metadata for an existing agent group.

        Parameters:
            agent_group (str): Name of the agent group.
            description (str, optional): New description.
            icon (optional): Icon reference for the group.
            properties (dict, optional): Updated metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        super().update_record(agent_group, 'agent_group', '/', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_agent_group(self, agent_group, rebuild=False):
        """
        Remove an agent group from the registry.

        Parameters:
            agent_group (str): Name of the agent group to remove.
            rebuild (bool, optional): Whether to rebuild dependent indexes after deletion.
        """
        record = self.get_agent_group(agent_group)
        if record:
            super().deregister(record, rebuild=rebuild)

    def get_agent_groups(self):
        """
        List all registered agent groups.

        Returns:
            list[dict]: All agent group records with metadata.
        """
        return self.list_records(type='agent_group', scope='/')

    def get_agent_group(self, agent_group):
        """
        Retrieve a single agent group record by name.

        Parameters:
            agent_group (str): Name of the agent group.

        Returns:
            dict: Metadata of the agent group, or None if not found.
        """

        return super().get_record(agent_group, 'agent_group', '/')

    def get_agent_group_description(self, agent_group):
        """
        Get the description of a specific agent group.

        Parameters:
            agent_group (str): Name of the agent group.

        Returns:
            str: Description of the agent group.
        """
        return super().get_record_description(agent_group, 'agent_group', '/')

    def set_agent_group_description(self, agent_group, description, rebuild=False):
        """
        Set or update the description for a specific agent group.

        Parameters:
            agent_group (str): Name of the agent group.
            description (str): New description.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        super().set_record_description(agent_group, 'agent_group', '/', description, rebuild=rebuild)

    def set_agent_group_property(self, agent_group, key, value, rebuild=False):
        """
        Set a custom property for an agent group.

        Parameters:
            agent_group (str): Name of the agent group.
            key (str): Property name.
            value: Property value.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent_group, full=False)
        super().set_record_property(agent_group, 'agent_group', scope, key, value, rebuild=rebuild)

    def get_agent_group_agents(self, agent_group):
        """
        Retrieve all agents belonging to a specific agent group.

        Parameters:
            agent_group (str): Name of the agent group.

        Returns:
            list[dict]: Agent records within the group.
        """
        return super().filter_record_contents(agent_group, 'agent_group', '/', filter_type='agent')

    def get_agent_group_agent(self, agent_group, agent):
        """
        Retrieve a specific agent from an agent group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.

        Returns:
            dict: Metadata of the agent, or None if not found.
        """
        return super().get_record(agent, 'agent', f'/agent_group/{agent_group}')

    def add_agent_to_agent_group(self, agent_group, agent, description='', properties={}, rebuild=False):
        """
        Register a new agent under a specific agent group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.
            description (str, optional): Description of the agent.
            properties (dict, optional): Metadata for the agent.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        super().register_record(agent, 'agent', f'/agent_group/{agent_group}', description=description, properties=properties, rebuild=rebuild)

    def update_agent_in_agent_group(self, agent_group, agent, description='', properties={}, rebuild=False):
        """
        Update metadata for an existing agent within a group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.
            description (str, optional): New description.
            properties (dict, optional): Updated metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        super().update_record(agent, 'agent', f'/agent_group/{agent_group}', description=description, properties=properties, rebuild=rebuild)

    def remove_agent_from_agent_group(self, agent_group, agent, rebuild=False):
        """
        Remove a specific agent from an agent group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent to remove.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        record = self.get_agent_group_agent(agent_group, agent)
        if record:
            super().deregister(record, rebuild=rebuild)

    def get_agent_group_agent_properties(self, agent_group, agent):
        """
        Get all properties of a specific agent in a group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.

        Returns:
            dict: Agent properties.
        """
        return super().get_record_properties(agent, 'agent', f'/agent_group/{agent_group}')

    def get_agent_property_in_agent_group(self, agent_group, agent, key):
        """
        Retrieve a single property value of an agent within a group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.
            key (str): Property key.

        Returns:
            Value of the property.
        """
        return super().get_record_property(agent, 'agent', f'/agent_group/{agent_group}', key)

    def set_agent_property_in_agent_group(self, agent_group, agent, key, value, rebuild=False):
        """
        Set or update a property for an agent in a group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.
            key (str): Property name.
            value: Property value.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        super().set_record_property(agent, 'agent', f'/agent_group/{agent_group}', key, value, rebuild=rebuild)

    def delete_agent_property_in_agent_group(self, agent_group, agent, key, rebuild=False):
        """
        Delete a property for an agent within a group.

        Parameters:
            agent_group (str): Name of the agent group.
            agent (str): Name of the agent.
            key (str): Property name to delete.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        super().delete_record_property(agent, 'agent', f'/agent_group/{agent_group}', key, rebuild=rebuild)

    ######### agent
    def add_agent(self, agent, created_by, description='', properties={}, rebuild=False):
        """
        Register a new agent in the registry.

        Parameters:
            agent (str): Name of the agent.
            created_by (str): Identifier of the creator.
            description (str, optional): Description of the agent.
            properties (dict, optional): Additional metadata for the agent.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        super().register_record(agent, 'agent', scope, created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_agent(self, agent, description='', icon=None, properties={}, rebuild=False):
        """
        Update metadata for an existing agent.

        Parameters:
            agent (str): Name of the agent.
            description (str, optional): Updated description.
            icon (optional): Icon associated with the agent.
            properties (dict, optional): Updated metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        super().update_record(agent, 'agent', scope, description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_agent(self, agent, rebuild=False):
        """
        Remove an existing agent from the registry.

        Parameters:
            agent (str): Name of the agent to remove.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        record = self.get_agent(agent)
        if record:
            super().deregister(record, rebuild=rebuild)

    def get_agents(self, scope='/', recursive=False):
        """
        List all registered agents under a given scope.

        Parameters:
            scope (str, optional): Registry scope path. Defaults to root ('/').
            recursive (bool, optional): Whether to include nested agents.

        Returns:
            list[dict]: List of agent records.
        """
        return self.list_records(type='agent', scope=scope, recursive=recursive)

    def get_agent(self, agent):
        """
        Retrieve a specific agent record.

        Parameters:
            agent (str): Name of the agent.

        Returns:
            dict: Agent metadata, or None if not found.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        return super().get_record(agent, 'agent', scope)

    def get_agent_description(self, agent):
        """
        Get the description of a specific agent.

        Parameters:
            agent (str): Name of the agent.

        Returns:
            str: Description of the agent.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        return super().get_record_description(agent, 'agent', scope)

    def set_agent_description(self, agent, description, rebuild=False):
        """
        Set or update the description of an agent.

        Parameters:
            agent (str): Name of the agent.
            description (str): Description text.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        super().set_record_description(agent, 'agent', scope, description, rebuild=rebuild)

    def get_agent_parent(self, agent):
        """
        Get the parent agent (if any) from the hierarchical name.

        Parameters:
            agent (str): Hierarchical agent name.

        Returns:
            str | None: Parent agent name, or None if it’s a top-level agent.
        """

        agent_hierarchy = agent.split(Separator.AGENT)
        parent = Separator.AGENT.join(agent_hierarchy[:-1]) if len(agent_hierarchy) > 1 else None
        return parent

    # agent properties
    def get_agent_properties(self, agent, recursive=False, include_params=False):
        """
        Retrieve all properties of an agent, optionally including parent and I/O params.

        Parameters:
            agent (str): Name of the agent.
            recursive (bool, optional): Whether to include inherited parent properties.
            include_params (bool, optional): Whether to include input/output parameters.

        Returns:
            dict: Agent properties and optionally inputs/outputs.
        """
        if recursive:
            parent = self.get_agent_parent(agent)
            parent_properties = {}
            if parent:
                parent_properties = self.get_agent_properties(parent, recursive=recursive, include_params=include_params)

            agent_properties = self.get_agent_properties(agent, recursive=False, include_params=include_params)
            # merge agents properties into parents, overriding when overlap
            return json_utils.merge_json(parent_properties, agent_properties)
        else:
            scope = self._derive_scope_from_name(agent, full=False)
            agent_properties = super().get_record_properties(agent, 'agent', scope)

            if agent_properties is None:
                return {}

            if include_params:
                inputs = {}
                outputs = {}
                agent_properties['inputs'] = inputs
                agent_properties['outputs'] = outputs

                # inputs
                ri = self.get_agent_inputs(agent)
                if ri is None:
                    ri = []
                for input in ri:
                    n = input['name'] if 'name' in input else None
                    if n is None:
                        continue
                    d = input['description'] if 'description' in input else ""
                    props = input['properties']
                    inputs[n] = {'name': n, 'description': d, 'properties': props}

                # outputs
                ro = self.get_agent_outputs(agent)
                if ro is None:
                    ro = []
                for output in ro:
                    n = output['name'] if 'name' in output else None
                    if n is None:
                        continue
                    d = output['description'] if 'description' in output else ""
                    props = output['properties']
                    outputs[n] = {'name': n, 'description': d, 'properties': props}

            return agent_properties

    def get_agent_property(self, agent, key):
        """
        Get a specific property of an agent.

        Parameters:
            agent (str): Name of the agent.
            key (str): Property key.

        Returns:
            Any: Property value, or None if not found.
        """

        scope = self._derive_scope_from_name(agent, full=False)
        return super().get_record_property(agent, 'agent', scope, key)

    def set_agent_property(self, agent, key, value, rebuild=False):
        """
        Set or update a property for an agent.

        Parameters:
            agent (str): Name of the agent.
            key (str): Property key.
            value: Property value.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        super().set_record_property(agent, 'agent', scope, key, value, rebuild=rebuild)

    def delete_agent_property(self, agent, key, rebuild=False):
        """
        Delete a property from an agent.

        Parameters:
            agent (str): Name of the agent.
            key (str): Property key to delete.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        super().delete_record_property(agent, 'agent', scope, key, rebuild=rebuild)

    # agent image (part of properties)
    def get_agent_image(self, agent):
        """
        Get the image reference associated with an agent.

        Parameters:
            agent (str): Name of the agent.

        Returns:
            str | None: Image reference if available.
        """

        return self.get_agent_property(agent, 'image')

    def set_agent_image(self, agent, image, rebuild=False):
        """
        Set or update the image reference for an agent.

        Parameters:
            agent (str): Name of the agent.
            image (str): Image reference or URL.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        self.set_agent_property(agent, 'image', image, rebuild=rebuild)

    ######### agent input and output parameters
    def add_agent_input(self, agent, parameter, description='', properties={}, rebuild=False):
        """
        Register a new input parameter for an agent.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Input parameter name.
            description (str, optional): Description of the parameter.
            properties (dict, optional): Metadata for the input.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, "input", scope, description=description, properties=properties, rebuild=rebuild)

    def update_agent_input(self, agent, parameter, description='', properties={}, rebuild=False):
        """
        Update metadata for an existing agent input parameter.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Input parameter name.
            description (str, optional): Updated description.
            properties (dict, optional): Updated properties.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().update_record(parameter, "input", scope, description=description, properties=properties, rebuild=rebuild)

    def get_agent_inputs(self, agent):
        """
        Retrieve all input parameters for an agent.

        Parameters:
            agent (str): Name of the agent.

        Returns:
            list[dict]: List of input parameter metadata.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type="input")

    def get_agent_input(self, agent, parameter):
        """
        Retrieve a single input parameter definition.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Input parameter name.

        Returns:
            dict | None: Input parameter metadata if found.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type='input', filter_name=parameter, single=True)

    def set_agent_input(self, agent, parameter, description, properties={}, rebuild=False):
        """
        Set or overwrite a specific input parameter for an agent.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Input parameter name.
            description (str): Parameter description.
            properties (dict, optional): Parameter metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, 'input', scope, description=description, properties=properties, rebuild=rebuild)

    def del_agent_input(self, agent, parameter, rebuild=False):
        """
        Delete a specific input parameter from an agent.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Input parameter name.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        record = self.get_agent_input(agent, parameter)
        if record:
            super().deregister(record, rebuild=rebuild)

    def add_agent_output(self, agent, parameter, description='', properties={}, rebuild=False):
        """
        Register a new output parameter for an agent.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Output parameter name.
            description (str, optional): Description of the parameter.
            properties (dict, optional): Metadata for the output.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, "output", scope, description=description, properties=properties, rebuild=rebuild)

    def update_agent_output(self, agent, parameter, description='', properties={}, rebuild=False):
        """
        Update metadata for an existing output parameter.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Output parameter name.
            description (str, optional): Updated description.
            properties (dict, optional): Updated metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().update_record(parameter, "output", scope, description=description, properties=properties, rebuild=rebuild)

    def get_agent_outputs(self, agent):
        """
        Retrieve all output parameters for an agent.

        Parameters:
            agent (str): Name of the agent.

        Returns:
            list[dict]: List of output parameter metadata.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type='output')

    def get_agent_output(self, agent, parameter):
        """
        Retrieve a single output parameter definition.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Output parameter name.

        Returns:
            dict | None: Output parameter metadata if found.
        """
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type='output', filter_name=parameter, single=True)

    def set_agent_output(self, agent, parameter, description, properties={}, rebuild=False):
        """
        Set or overwrite a specific output parameter for an agent.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Output parameter name.
            description (str): Parameter description.
            properties (dict, optional): Parameter metadata.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, 'output', scope, description=description, properties=properties, rebuild=rebuild)

    def del_agent_output(self, agent, parameter, rebuild=False):
        """
        Delete a specific output parameter from an agent.

        Parameters:
            agent (str): Name of the agent.
            parameter (str): Output parameter name.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        record = self.get_agent_output(agent, parameter)
        if record:
            super().deregister(record, rebuild=rebuild)

    # agent input properties
    def get_agent_input_properties(self, agent, input):
        """
        Retrieve all properties of a specific input parameter.

        Parameters:
            agent (str): Name of the agent.
            input (str): Input parameter name.

        Returns:
            dict: Input parameter properties.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_properties(input, 'input', scope)

    def get_agent_input_property(self, agent, input, key):
        """
        Get a single property of a specific input parameter.

        Parameters:
            agent (str): Name of the agent.
            input (str): Input parameter name.
            key (str): Property key.

        Returns:
            Any: Property value.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_property(input, 'input', scope, key)

    def set_agent_input_property(self, agent, input, key, value, rebuild=False):
        """
        Set or update a property for an input parameter.

        Parameters:
            agent (str): Name of the agent.
            input (str): Input parameter name.
            key (str): Property name.
            value: Property value.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """

        scope = self._derive_scope_from_name(agent, full=True)
        super().set_record_property(input, 'input', scope, key, value, rebuild=rebuild)

    def delete_agent_input_property(self, agent, input, key, rebuild=False):
        """
        Delete a property from an input parameter.

        Parameters:
            agent (str): Name of the agent.
            input (str): Input parameter name.
            key (str): Property name to delete.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """

        scope = self._derive_scope_from_name(agent, full=True)
        super().delete_record_property(input, 'input', scope, key, rebuild=rebuild)

    # agent output properties
    def get_agent_output_properties(self, agent, output):
        """
        Retrieve all properties of a specific output parameter.

        Parameters:
            agent (str): Name of the agent.
            output (str): Output parameter name.

        Returns:
            dict: Output parameter properties.
        """

        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_properties(output, 'output', scope)

    def get_agent_output_property(self, agent, output, key):
        """
        Get a single property of a specific output parameter.

        Parameters:
            agent (str): Name of the agent.
            output (str): Output parameter name.
            key (str): Property name.

        Returns:
            Any: Property value.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_property(output, 'output', scope, key)

    def set_agent_output_property(self, agent, output, key, value, rebuild=False):
        """
        Set or update a property for an output parameter.

        Parameters:
            agent (str): Name of the agent.
            output (str): Output parameter name.
            key (str): Property name.
            value: Property value.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        super().set_record_property(output, 'output', scope, key, value, rebuild=rebuild)

    def delete_agent_output_property(self, agent, output, key, rebuild=False):
        """
        Delete a property from an output parameter.

        Parameters:
            agent (str): Name of the agent.
            output (str): Output parameter name.
            key (str): Property name to delete.
            rebuild (bool, optional): Whether to rebuild dependent indexes.
        """

        scope = self._derive_scope_from_name(agent, full=True)
        super().delete_record_property(output, 'output', scope, key, rebuild=rebuild)

    # agent derived agents
    def get_agent_derived_agents(self, agent):
        """
        List agents derived from a given agent.

        Parameters:
            agent (str): Name of the base agent.

        Returns:
            list[dict]: Derived agent records.
        """
        scope = self._derive_scope_from_name(agent, full=True)
        return self.list_records(type='agent', scope=scope, recursive=False)
