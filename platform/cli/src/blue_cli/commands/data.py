import click
from click import Context
from blue_cli.helper import show_output, bcolors
from blue_cli.manager import DataRegistryManager 
import json


@click.group(help="interact with registry data")
@click.option("--platform", default="PLATFORM", help="platform name")
@click.option("--registry", default="default", help="registry name")
@click.option("--output", default="table", type=str, help="output format (table|json|csv)")
@click.option("--query", default="$", required=False, type=str, help="query on output results")

@click.pass_context
def data(ctx, platform, registry, output, query):
    global data_registry_mgr
    data_registry_mgr = DataRegistryManager(platform=platform, registry=registry)
    ctx.ensure_object(dict)
    ctx.obj["platform"] = platform
    ctx.obj["registry"] = registry
    ctx.obj["output"] = output
    ctx.obj["query"] = query


@data.command(help="List registry objects: sources, databases, collections, entities, or attributes")
@click.option("--source", required=False, help="Source name (optional; lists databases under the source if provided; lists all sources if not provided)")
@click.option("--database", required=False, help="Database name (optional; lists collections under the database)")
@click.option("--collection", required=False, help="Collection name (optional; lists entities under the collection)")
@click.option("--entity", required=False, help="Entity name (optional; lists attributes under the entity)")
def ls(source, database, collection, entity):
    ctx = click.get_current_context()
    output = ctx.obj["output"]

    # Level 1: List sources
    if not source:
        sources = data_registry_mgr.get_all_sources()
        data = [[name, src.get("type", ""), src.get("scope", "")] for name, src in sources.items()] if output == "table" \
            else [{"name": k, **v} for k, v in sources.items()]
        headers = ["name", "type", "scope"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    # Fetch source
    src = data_registry_mgr.get_source(source)
    if not src:
        raise click.ClickException(f"Source '{source}' not found")
    if isinstance(src, list):  # RedisJSON returns list for path queries
        src = src[0]

    contents = src.get("contents", {})

    # Level 2: List databases
    if source and not database:
        dbs = contents.get("database", {})
        if not dbs:
            click.echo(f"No databases found under source '{source}'")
            return
        data = [[name] for name in dbs.keys()] if output == "table" \
            else [{"name": k, **v} for k, v in dbs.items()]
        headers = ["database"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    db = contents.get("database", {}).get(database)
    if not db:
        raise click.ClickException(f"Database '{database}' not found in source '{source}'")

    contents = db.get("contents", {})

    # Level 3: List collections
    if database and not collection:
        collections = contents.get("collection", {})
        
        
        if not collections:
            click.echo(f"No collections found in database '{database}'")
            return
        data = [[name] for name in collections.keys()] if output == "table" \
            else [{"name": k, **v} for k, v in collections.items()]
        headers = ["collection"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return


    coll = contents.get("collection", {}).get(collection)
    
    if not coll:
        raise click.ClickException(f"Collection '{collection}' not found in database '{database}'")

    contents = coll.get("contents", {})

    # Level 4: List entities
    if collection and not entity:
        entities = contents.get("entity", {})
        if not entities:
            click.echo(f"No entities found in collection '{collection}'")
            return
        data = [[name] for name in entities.keys()] if output == "table" \
            else [{"name": k, **v} for k, v in entities.items()]
        headers = ["entity"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    ent = contents.get("entity", {}).get(entity)
    if not ent:
        raise click.ClickException(f"Entity '{entity}' not found in collection '{collection}'")

    contents = ent.get("contents", {})

    # Level 5: List attributes
    attributes = contents.get("attribute", {})
    if not attributes:
        click.echo(f"No attributes found in entity '{entity}'")
        return
    data = [[name, str(value)] for name, value in attributes.items()] if output == "table" \
        else [{"name": k, "value": v} for k, v in attributes.items()]
    headers = ["attribute", "value"] if output == "table" else None
    show_output(data, ctx, headers=headers, tablefmt="plain")
    
    
    
@data.command(help="Show a single registry object (source, database, collection, entity, attribute)")
@click.option("--source", required=False, help="Source name, if provided alone, displays the source object")
@click.option("--database", required=False, help="Database name. Requires --source. If both provided, shows the database.")
@click.option("--collection", required=False, help="Collection name. Show details of the specified collection (requires --source and --database), unless lower-level flags are provided.")
@click.option("--entity", required=False, help="Entity name. Shows an entity (requires --source, --database, and --collection), unless lower level flags are provided")
@click.option("--attribute", required=False, help="Attribute name. To show an attribute you must also provide --source, --database, --collection, and --entity")
def show(source, database, collection, entity, attribute):
    ctx = click.get_current_context()
    data_registry_mgr = ctx.obj["data_registry_mgr"]
    output = ctx.obj["output"]

    if not source:
        raise click.ClickException("You must provide at least --source")

    # Fetch source
    src = data_registry_mgr.get_source(source)
    if not src:
        raise click.ClickException(f"Source '{source}' not found")
    if isinstance(src, list):  # RedisJSON safety
        src = src[0]

    contents = src.get("contents", {})

    # Level 1: Show source
    if source and not database:
        click.echo(f"{bcolors.OKBLUE}Source: {source}{bcolors.ENDC}")
        data = [[k, v] for k, v in src.items()] if output == "table" else src
        headers = ["key", "value"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    # Level 2: Show database
    db = contents.get("database", {}).get(database)
    if not db:
        raise click.ClickException(f"Database '{database}' not found in source '{source}'")

    contents = db.get("contents", {})

    if database and not collection:
        click.echo(f"{bcolors.OKBLUE}Database: {database}{bcolors.ENDC}")
        data = [[k, v] for k, v in db.items()] if output == "table" else db
        headers = ["key", "value"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    # Level 3: Show collection
    coll = contents.get("collection", {}).get(collection)
    if not coll:
        raise click.ClickException(f"Collection '{collection}' not found in database '{database}'")

    contents = coll.get("contents", {})

    if collection and not entity:
        click.echo(f"{bcolors.OKBLUE}Collection: {collection}{bcolors.ENDC}")
        data = [[k, v] for k, v in coll.items()] if output == "table" else coll
        headers = ["key", "value"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    # Level 4: Show entity
    ent = contents.get("entity", {}).get(entity)
    if not ent:
        raise click.ClickException(f"Entity '{entity}' not found in collection '{collection}'")

    contents = ent.get("contents", {})

    if entity and not attribute:
        click.echo(f"{bcolors.OKBLUE}Entity: {entity}{bcolors.ENDC}")
        data = [[k, v] for k, v in ent.items()] if output == "table" else ent
        headers = ["key", "value"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    # Level 5: Show attribute
    attr = contents.get("attribute", {}).get(attribute)
    if not attr:
        raise click.ClickException(f"Attribute '{attribute}' not found in entity '{entity}'")

    click.echo(f"{bcolors.OKBLUE}Attribute: {attribute}{bcolors.ENDC}")
    data = [[k, v] for k, v in attr.items()] if isinstance(attr, dict) and output == "table" else attr
    headers = ["key", "value"] if isinstance(attr, dict) and output == "table" else None
    show_output(data, ctx, headers=headers, tablefmt="plain")


# ------------------------------
# Create (hierarchical)
# ------------------------------
@click.pass_context
@data.command(help="Create a new source, database, collection, entity, or attribute")
@click.argument("name", required=True)
@click.option("--description", default="", help="Description")
@click.option("--properties", default="{}", help="JSON string of properties")
@click.option("--source", help="Parent source name (required for database or below)")
@click.option("--database", help="Parent database name (required for collection or below)")
@click.option("--collection", help="Parent collection name (required for entity or below)")
@click.option("--entity", help="Parent entity name (required for attribute)")
def create(name, description, properties, source, database, collection, entity):
    ctx = click.get_current_context()
    data_registry_mgr = ctx.obj["data_registry_mgr"]

    try:
        props = json.loads(properties)
    except json.JSONDecodeError:
        raise click.ClickException("Properties must be a valid JSON string")

    obj = {
        "name": name,
        "description": description,
        "properties": props,
    }

    # Hierarchy: source -> database -> collection -> entity -> attribute
    if not source and not database and not collection and not entity:
        # create source
        data_registry_mgr.create_source(name, obj)
        click.echo(f"Created source '{name}'")
    elif source and not database and not collection and not entity:
        # create database
        data_registry_mgr.create_database(source, name, obj)
        click.echo(f"Created database '{name}' in source '{source}'")
    elif source and database and not collection and not entity:
        # create collection
        data_registry_mgr.create_collection(source, database, name, obj)
        click.echo(f"Created collection '{name}' in database '{database}' of source '{source}'")
    elif source and database and collection and not entity:
        # create entity
        data_registry_mgr.create_entity(source, database, collection, name, obj)
        click.echo(f"Created entity '{name}' in collection '{collection}' of database '{database}' in source '{source}'")
    elif source and database and collection and entity:
        # create attribute
        data_registry_mgr.create_attribute(source, database, collection, entity, name, obj)
        click.echo(f"Created attribute '{name}' in entity '{entity}' of collection '{collection}' in database '{database}' in source '{source}'")
    else:
        raise click.ClickException("Invalid hierarchy: must specify parent flags properly.")



# ------------------------------
# Delete objects from registry (source, database, collection, entity, attribute)
# ------------------------------
@data.command(help="Delete a registry object (source, database, collection, entity, attribute)")
@click.argument("name", required=True)
@click.option("--source", required=False, help="Parent source name (required for database or below)")
@click.option("--database", required=False, help="Parent database name (required for collection or below)")
@click.option("--collection", required=False, help="Parent collection name (required for entity or below)")
@click.option("--entity", required=False, help="Parent entity name (required for attribute)")
@click.confirmation_option(prompt="Are you sure you want to delete?")
def delete(name, source, database, collection, entity):
    ctx = click.get_current_context()
    data_registry_mgr = ctx.obj["data_registry_mgr"]

    # Determine level from options
    if source and not database:
        # Level 1: delete database name
        if data_registry_mgr.delete_database(source, name):
            click.echo(f"Deleted database '{name}' from source '{source}'")
        else:
            click.echo(f"Database '{name}' not found in source '{source}'")
        return

    if source and database and not collection:
        # Level 2: delete collection name
        if data_registry_mgr.delete_collection(source, database, name):
            click.echo(f"Deleted collection '{name}' from database '{database}'")
        else:
            click.echo(f"Collection '{name}' not found in database '{database}'")
        return

    if source and database and collection and not entity:
        # Level 3: delete entity name
        if data_registry_mgr.delete_entity(source, database, collection, name):
            click.echo(f"Deleted entity '{name}' from collection '{collection}'")
        else:
            click.echo(f"Entity '{name}' not found in collection '{collection}'")
        return

    if source and database and collection and entity:
        # Level 4: delete attribute name
        if data_registry_mgr.delete_attribute(source, database, collection, entity, name):
            click.echo(f"Deleted attribute '{name}' from entity '{entity}'")
        else:
            click.echo(f"Attribute '{name}' not found in entity '{entity}'")
        return

    if name and not source:
        # Level 0: delete source
        if data_registry_mgr.delete_source(name):
            click.echo(f"Deleted source '{name}'")
        else:
            click.echo(f"Source '{name}' not found")


@data.command(help="Search registry objects by keyword at any level")
@click.option("--source", required=False, help="Parent source name (required for database or below)")
@click.option("--database", required=False, help="Parent database name (required for collection or below)")
@click.option("--collection", required=False, help="Parent collection name (required for entity or below)")
@click.option("--entity", required=False, help="Parent entity name (required for attribute)")
@click.argument("keyword", required=True)
def search(source, database, collection, entity, keyword):
    ctx = click.get_current_context()
    data_registry_mgr = ctx.obj["data_registry_mgr"]
    output = ctx.obj["output"]

    keyword_lower = keyword.lower()
    data = []
    headers = None

    # ------------------------------
    # Level 1: search sources
    # ------------------------------
    if not source:
        sources = data_registry_mgr.get_all_sources()
        matches = {
            name: src for name, src in sources.items()
            if keyword_lower in name.lower() or keyword_lower in json.dumps(src).lower()
        }
        if not matches:
            click.echo(f"{bcolors.WARNING}No sources match keyword '{keyword}'.{bcolors.ENDC}")
            return

        if output == "table":
            data = [[name, src.get("type", ""), src.get("scope", "")] for name, src in matches.items()]
            headers = ["name", "type", "scope"]
        else:
            data = [{"name": k, **v} for k, v in matches.items()]
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    # ------------------------------
    # Fetch source
    # ------------------------------
    src = data_registry_mgr.get_source(source)
    if not src:
        raise click.ClickException(f"Source '{source}' not found")
    if isinstance(src, list):
        src = src[0]

    contents = src.get("contents", {})

    # ------------------------------
    # Level 2: search databases
    # ------------------------------
    if source and not database:
        dbs = contents.get("database", {})
        
        matches = {name: db for name, db in dbs.items()
                   if keyword_lower in name.lower()}
        
        if not matches:
            click.echo(f"No databases in source '{source}' match '{keyword}'")
            return

        data = [[name] for name in matches.keys()] if output == "table" \
            else [{"name": k, **v} for k, v in matches.items()]
        headers = ["database"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    db = contents.get("database", {}).get(database)
    if not db:
        raise click.ClickException(f"Database '{database}' not found in source '{source}'")

    contents = db.get("contents", {})

    # ------------------------------
    # Level 3: search collections
    # ------------------------------
    if database and not collection:
        colls = contents.get("collection", {})
        
        matches = {name: c for name, c in colls.items()
                   if keyword_lower in name.lower()}
        
        if not matches:
            click.echo(f"No collections in database '{database}' match '{keyword}'")
            return

        data = [[name] for name in matches.keys()] if output == "table" \
            else [{"name": k, **v} for k, v in matches.items()]
        headers = ["collection"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    coll = contents.get("collection", {}).get(collection)
    if not coll:
        raise click.ClickException(f"Collection '{collection}' not found in database '{database}'")

    contents = coll.get("contents", {})

    # ------------------------------
    # Level 4: search entities
    # ------------------------------
    if collection and not entity:
        ents = contents.get("entity", {})
        
        matches = {name: e for name, e in ents.items()
                   if keyword_lower in name.lower()}
        
        if not matches:
            click.echo(f"No entities in collection '{collection}' match '{keyword}'")
            return

        data = [[name] for name in matches.keys()] if output == "table" \
            else [{"name": k, **v} for k, v in matches.items()]
        headers = ["entity"] if output == "table" else None
        show_output(data, ctx, headers=headers, tablefmt="plain")
        return

    ent = contents.get("entity", {}).get(entity)
    if not ent:
        raise click.ClickException(f"Entity '{entity}' not found in collection '{collection}'")

    contents = ent.get("contents", {})

    # ------------------------------
    # Level 5: search attributes
    # ------------------------------
    attrs = contents.get("attribute", {})
    
    matches = {name: v for name, v in attrs.items()
               if keyword_lower in name.lower()}
    
    if not matches:
        click.echo(f"No attributes in entity '{entity}' match '{keyword}'")
        return

    data = [[name, str(value)] for name, value in matches.items()] if output == "table" \
        else [{"name": k, "value": v} for k, v in matches.items()]
    headers = ["attribute", "value"] if output == "table" else None
    show_output(data, ctx, headers=headers, tablefmt="plain")

if __name__ == "__main__":
    data()  # invoke the Click group
