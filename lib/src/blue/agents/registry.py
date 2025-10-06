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
        super().register_record(agent_group, 'agent_group', '/', created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_agent_group(self, agent_group, description='', icon=None, properties={}, rebuild=False):
        super().update_record(agent_group, 'agent_group', '/', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_agent_group(self, agent_group, rebuild=False):
        record = self.get_agent_group(agent_group)
        if record:
            super().deregister(record, rebuild=rebuild)

    def get_agent_groups(self):
        return self.list_records(type='agent_group', scope='/')

    def get_agent_group(self, agent_group):
        return super().get_record(agent_group, 'agent_group', '/')

    def get_agent_group_description(self, agent_group):
        return super().get_record_description(agent_group, 'agent_group', '/')

    def set_agent_group_description(self, agent_group, description, rebuild=False):
        super().set_record_description(agent_group, 'agent_group', '/', description, rebuild=rebuild)

    def set_agent_group_property(self, agent_group, key, value, rebuild=False):
        scope = self._derive_scope_from_name(agent_group, full=False)
        super().set_record_property(agent_group, 'agent_group', scope, key, value, rebuild=rebuild)

    def get_agent_group_agents(self, agent_group):
        return super().filter_record_contents(agent_group, 'agent_group', '/', filter_type='agent')

    def get_agent_group_agent(self, agent_group, agent):
        return super().get_record(agent, 'agent', f'/agent_group/{agent_group}')

    def add_agent_to_agent_group(self, agent_group, agent, description='', properties={}, rebuild=False):
        super().register_record(agent, 'agent', f'/agent_group/{agent_group}', description=description, properties=properties, rebuild=rebuild)

    def update_agent_in_agent_group(self, agent_group, agent, description='', properties={}, rebuild=False):
        super().update_record(agent, 'agent', f'/agent_group/{agent_group}', description=description, properties=properties, rebuild=rebuild)

    def remove_agent_from_agent_group(self, agent_group, agent, rebuild=False):
        record = self.get_agent_group_agent(agent_group, agent)
        if record:
            super().deregister(record, rebuild=rebuild)

    def get_agent_group_agent_properties(self, agent_group, agent):
        return super().get_record_properties(agent, 'agent', f'/agent_group/{agent_group}')

    def get_agent_property_in_agent_group(self, agent_group, agent, key):
        return super().get_record_property(agent, 'agent', f'/agent_group/{agent_group}', key)

    def set_agent_property_in_agent_group(self, agent_group, agent, key, value, rebuild=False):
        super().set_record_property(agent, 'agent', f'/agent_group/{agent_group}', key, value, rebuild=rebuild)

    def delete_agent_property_in_agent_group(self, agent_group, agent, key, rebuild=False):
        super().delete_record_property(agent, 'agent', f'/agent_group/{agent_group}', key, rebuild=rebuild)

    ######### agent
    def add_agent(self, agent, created_by, description='', properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=False)
        super().register_record(agent, 'agent', scope, created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_agent(self, agent, description='', icon=None, properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=False)
        super().update_record(agent, 'agent', scope, description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_agent(self, agent, rebuild=False):
        record = self.get_agent(agent)
        if record:
            super().deregister(record, rebuild=rebuild)

    def get_agents(self, scope='/', recursive=False):
        return self.list_records(type='agent', scope=scope, recursive=recursive)

    def get_agent(self, agent):
        scope = self._derive_scope_from_name(agent, full=False)
        return super().get_record(agent, 'agent', scope)

    def get_agent_description(self, agent):
        scope = self._derive_scope_from_name(agent, full=False)
        return super().get_record_description(agent, 'agent', scope)

    def set_agent_description(self, agent, description, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=False)
        super().set_record_description(agent, 'agent', scope, description, rebuild=rebuild)

    def get_agent_parent(self, agent):
        agent_hierarchy = agent.split(Separator.AGENT)
        parent = Separator.AGENT.join(agent_hierarchy[:-1]) if len(agent_hierarchy) > 1 else None
        return parent

    # agent properties
    def get_agent_properties(self, agent, recursive=False, include_params=False):
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
        scope = self._derive_scope_from_name(agent, full=False)
        return super().get_record_property(agent, 'agent', scope, key)

    def set_agent_property(self, agent, key, value, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=False)
        super().set_record_property(agent, 'agent', scope, key, value, rebuild=rebuild)

    def delete_agent_property(self, agent, key, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=False)
        super().delete_record_property(agent, 'agent', scope, key, rebuild=rebuild)

    # agent image (part of properties)
    def get_agent_image(self, agent):
        return self.get_agent_property(agent, 'image')

    def set_agent_image(self, agent, image, rebuild=False):
        self.set_agent_property(agent, 'image', image, rebuild=rebuild)

    ######### agent input and output parameters
    def add_agent_input(self, agent, parameter, description='', properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, "input", scope, description=description, properties=properties, rebuild=rebuild)

    def update_agent_input(self, agent, parameter, description='', properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().update_record(parameter, "input", scope, description=description, properties=properties, rebuild=rebuild)

    def get_agent_inputs(self, agent):
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type="input")

    def get_agent_input(self, agent, parameter):
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type='input', filter_name=parameter, single=True)

    def set_agent_input(self, agent, parameter, description, properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, 'input', scope, description=description, properties=properties, rebuild=rebuild)

    def del_agent_input(self, agent, parameter, rebuild=False):
        record = self.get_agent_input(agent, parameter)
        if record:
            super().deregister(record, rebuild=rebuild)

    def add_agent_output(self, agent, parameter, description='', properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, "output", scope, description=description, properties=properties, rebuild=rebuild)

    def update_agent_output(self, agent, parameter, description='', properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().update_record(parameter, "output", scope, description=description, properties=properties, rebuild=rebuild)

    def get_agent_outputs(self, agent):
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type='output')

    def get_agent_output(self, agent, parameter):
        scope = self._derive_scope_from_name(agent, full=False)
        return super().filter_record_contents(agent, 'agent', scope, filter_type='output', filter_name=parameter, single=True)

    def set_agent_output(self, agent, parameter, description, properties={}, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().register_record(parameter, 'output', scope, description=description, properties=properties, rebuild=rebuild)

    def del_agent_output(self, agent, parameter, rebuild=False):
        record = self.get_agent_output(agent, parameter)
        if record:
            super().deregister(record, rebuild=rebuild)

    # agent input properties
    def get_agent_input_properties(self, agent, input):
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_properties(input, 'input', scope)

    def get_agent_input_property(self, agent, input, key):
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_property(input, 'input', scope, key)

    def set_agent_input_property(self, agent, input, key, value, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().set_record_property(input, 'input', scope, key, value, rebuild=rebuild)

    def delete_agent_input_property(self, agent, input, key, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().delete_record_property(input, 'input', scope, key, rebuild=rebuild)

    # agent output properties
    def get_agent_output_properties(self, agent, output):
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_properties(output, 'output', scope)

    def get_agent_output_property(self, agent, output, key):
        scope = self._derive_scope_from_name(agent, full=True)
        return super().get_record_property(output, 'output', scope, key)

    def set_agent_output_property(self, agent, output, key, value, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().set_record_property(output, 'output', scope, key, value, rebuild=rebuild)

    def delete_agent_output_property(self, agent, output, key, rebuild=False):
        scope = self._derive_scope_from_name(agent, full=True)
        super().delete_record_property(output, 'output', scope, key, rebuild=rebuild)

    # agent derived agents
    def get_agent_derived_agents(self, agent):
        scope = self._derive_scope_from_name(agent, full=True)
        return self.list_records(type='agent', scope=scope, recursive=False)
