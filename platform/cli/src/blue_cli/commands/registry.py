import click
# from blue_cli.commands import data as data_cmd
from blue_cli.commands import agent as agent_cmd


@click.group(help="command group to interact with blue registries")
@click.pass_context
def registry(ctx):
    ctx.ensure_object(dict)  # propagate context to subcommands

# Attach the data group under registry
# registry.add_command(data_cmd.data, name="data")
# Attach the agent group under registry
registry.add_command(agent_cmd.agent, name="agent")

if __name__ == "__main__":
    registry()

