import click
from blue_cli.commands import data as data_cmd

@click.group(help="Registry related commands")
@click.pass_context
def registry(ctx):
    ctx.ensure_object(dict)  # propagate context to subcommands

# Attach the data group under registry
registry.add_command(data_cmd.data, name="data")