###### Blue
from blue.agent import Agent
from blue.registry import Registry

###############
### AgentRegistry
#
class AgentRegistry(Registry):
    SEPARATOR = Agent.SEPARATOR
    
    def __init__(self, name="AGENT_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization

    def _initialize_properties(self):
        super()._initialize_properties()

    ######### agent groups
    def add_agent_group(self, agent_group, created_by, description="", properties={}, rebuild=False):
        super().register_record(agent_group, "agent_group", "/", created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_agent_group(self, agent_group, description="", icon=None, properties={}, rebuild=False):
        super().update_record(agent_group, "agent_group", "/", description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_agent_group(self, agent_group, rebuild=False):
        record = self.get_agent_group(agent_group)
        super().deregister(record, rebuild=rebuild)

    def get_agent_groups(self):
        return self.list_records(type="agent_group", scope="/")

    def get_agent_group(self, agent_group):
        return super().get_record(agent_group, type='agent_group', scope='/')

    def get_agent_group_description(self, agent_group):
        return super().get_record_description(agent_group, '/')

    def set_agent_group_description(self, agent_group, description, rebuild=False):
        super().set_record_description(agent_group, '/', description, rebuild=rebuild)

    def get_agent_group_agents(self, agent_group):
        return super().get_record_contents(agent_group, '/', type='agent')

    def get_agent_group_agent(self, agent_group, agent):
        return super().get_record_content(agent_group, '/', agent, type='agent')

    def add_agent_to_agent_group(self, agent_group, agent, description="", properties={}, rebuild=False):
        super().register_record(agent, 'agent', '/' + agent_group, description=description, properties=properties, rebuild=rebuild)

    def update_agent_in_agent_group(self, agent_group, agent, description="", properties={}, rebuild=False):
        super().update_record(agent, "agent", "/" + agent_group, description=description, properties=properties, rebuild=rebuild)

    def remove_agent_from_agent_group(self, agent_group, agent, rebuild=False):
        record = self.get_agent_group_agent(agent_group, agent)
        super().deregister(record, rebuild=rebuild)

    def get_agent_group_agent_properties(self, agent_group, agent):
        return super().get_record_properties(agent, f'/{agent_group}')

    def get_agent_property_in_agent_group(self, agent_group, agent, key):
        return super().get_record_property(agent, f'/{agent_group}', key)

    def set_agent_property_in_agent_group(self, agent_group, agent, key, value, rebuild=False):
        super().set_record_property(agent, f'/{agent_group}', key, value, rebuild=rebuild)

    def delete_agent_property_in_agent_group(self, agent_group, agent, key, rebuild=False):
        super().delete_record_property(agent, f'/{agent_group}', key, rebuild=rebuild)

    ######### agent
    def add_agent(self, agent, created_by, description="", properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=False)
        super().register_record(agent, "agent", scope, created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_agent(self, agent, description="", icon=None, properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=False)
        super().update_record(agent, "agent", scope, description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_agent(self, agent, rebuild=False):
        record = self.get_agent(agent)
        super().deregister(record, rebuild=rebuild)

    def get_agents(self, scope="/", recursive=False):
        return self.list_records(type="agent", scope=scope, recursive=recursive)

    def get_agent(self, agent):
        return super().get_record(agent, type='agent', scope=None)

    def get_agent_description(self, agent):
        return super().get_record_description(agent, None)

    def set_agent_description(self, agent, description, rebuild=False):
        super().set_record_description(agent, None, description, rebuild=rebuild)

    # agent properties
    def get_agent_properties(self, agent):
        return super().get_record_properties(agent, None)

    def get_agent_property(self, agent, key):
        return super().get_record_property(agent, None, key)

    def set_agent_property(self, agent, key, value, rebuild=False):
        super().set_record_property(agent, None, key, value, rebuild=rebuild)

    def delete_agent_property(self, agent, key, rebuild=False):
        super().delete_record_property(agent, None, key, rebuild=rebuild)

    # agent image (part of properties)
    def get_agent_image(self, agent):
        return self.get_agent_property(agent, 'image')

    def set_agent_image(self, agent, image, rebuild=False):
        self.set_agent_property(agent, 'image', image, rebuild=rebuild)

    ######### agent input and output parameters
    def add_agent_input(self, agent, parameter, description="", properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=True)
        super().register_record(parameter, "input", scope, description=description, properties=properties, rebuild=rebuild)

    def update_agent_input(self, agent, parameter, description="", properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=True)
        super().update_record(parameter, "input", scope, description=description, properties=properties, rebuild=rebuild)

    def remove_agent_input(self, agent, parameter, rebuild=False):
        record = self.get_agent_input(agent, parameter)
        super().deregister(record, rebuild=rebuild)

    def get_agent_inputs(self, agent):
        return super().get_record_contents(agent, None, type='input')

    def get_agent_input(self, agent, parameter):
        return super().get_record_content(agent, None, parameter, type='input')

    def set_agent_input(self, agent, parameter, description, properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=True)
        super().register_record(parameter, 'input', scope, description=description, properties=properties, rebuild=rebuild)

    def del_agent_input(self, agent, parameter, rebuild=False):
        record = self.get_agent_input(agent, parameter)
        super().deregister(record, rebuild=rebuild)

    def add_agent_output(self, agent, parameter, description="", properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=True)
        super().register_record(parameter, "output", scope, description=description, properties=properties, rebuild=rebuild)

    def update_agent_output(self, agent, parameter, description="", properties={}, rebuild=False):
        scope = self._identify_scope(agent, full=True)
        super().update_record(parameter, "output", scope, description=description, properties=properties, rebuild=rebuild)

    def remove_agent_output(self, agent, parameter, rebuild=False):
        record = self.get_agent_output(agent, parameter)
        super().deregister(record, rebuild=rebuild)

    def get_agent_outputs(self, agent):
        return super().get_record_contents(agent, None, type='output')

    def get_agent_output(self, agent, parameter):
        return super().get_record_content(agent, None, parameter, type='output')

    def set_agent_output(self, agent, parameter, description, rebuild=False):
        scope = self._identify_scope(agent, full=True)
        super().register_record(parameter, 'output', scope, description=description, properties=properties, rebuild=rebuild)

    def del_agent_output(self, agent, parameter, rebuild=False):
        record = self.get_agent_output(agent, parameter)
        super().deregister(record, rebuild=rebuild)

    # agent input properties
    def get_agent_input_properties(self, agent, input):
        return super().get_record_properties(input, f'/{agent}')

    def get_agent_input_property(self, agent, input, key):
        return super().get_record_property(input, f'/{agent}', key)

    def set_agent_input_property(self, agent, input, key, value, rebuild=False):
        super().set_record_property(input, f'/{agent}', key, value, rebuild=rebuild)

    def delete_agent_input_property(self, agent, input, key, rebuild=False):
        super().delete_record_property(input, f'/{agent}', key, rebuild=rebuild)

    # agent output properties
    def get_agent_output_properties(self, agent, output):
        return super().get_record_properties(output, f'/{agent}')

    def get_agent_output_property(self, agent, output, key):
        return super().get_record_property(output, f'/{agent}', key)

    def set_agent_output_property(self, agent, output, key, value, rebuild=False):
        super().set_record_property(output, f'/{agent}', key, value, rebuild=rebuild)

    def delete_agent_output_property(self, agent, output, key, rebuild=False):
        super().delete_record_property(output, f'/{agent}', key, rebuild=rebuild)

    # agent derived agents
    def get_agent_derived_agents(self, agent):
        scope = self._identify_scope(agent, full=True)
        return self.list_records(type="agent", scope=scope, recursive=False)
        
