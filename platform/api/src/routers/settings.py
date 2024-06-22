###### OS / Systems
import os
import sys


###### Properties
PROPERTIES = {}
PROPERTIES["platform.name"] = os.getenv("BLUE_DEPLOY_PLATFORM")
PROPERTIES["platform.deploy.version"] = os.getenv("BLUE_DEPLOY_VERSION")
PROPERTIES["platform.deploy.target"] = os.getenv("BLUE_DEPLOY_TARGET")
PROPERTIES["platform.deploy.secure"] = os.getenv("BLUE_DEPLOY_SECURE")
PROPERTIES["api.server"] = os.getenv("BLUE_PUBLIC_API_SERVER")
PROPERTIES["api.server.port"] = os.getenv("BLUE_PUBLIC_API_SERVER_PORT")
PROPERTIES["web.server"] = os.getenv("BLUE_PUBLIC_WEB_SERVER")
PROPERTIES["web.server.port"] = os.getenv("BLUE_PUBLIC_WEB_SERVER_PORT")
PROPERTIES["agent_registry.name"] = os.getenv("BLUE_AGENT_REGISTRY")
PROPERTIES["data_registry.name"] = os.getenv("BLUE_DATA_REGISTRY")
PROPERTIES["embeddings_model"] = os.getenv("BLUE_AGENT_REGISTRY_MODEL")

PROPERTIES["db.host"] = "blue_db_redis"

##### Other Settings
DEVELOPMENT = os.getenv("BLUE_DEPLOY_DEVELOPMENT", "False").lower() == "true"
SECURE_COOKIE = os.getenv("BLUE_DEPLOY_SECURE", "True").lower() == "true"