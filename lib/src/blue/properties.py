###### OS / Systems
import os

import pydash

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
PROPERTIES["model_registry.name"] = os.getenv("BLUE_MODEL_REGISTRY")
PROPERTIES["operator_registry.name"] = os.getenv("BLUE_OPERATOR_REGISTRY")
PROPERTIES["tool_registry.name"] = os.getenv("BLUE_TOOL_REGISTRY")
PROPERTIES["embeddings_model"] = os.getenv("BLUE_AGENT_REGISTRY_MODEL")
PROPERTIES["services.openai.service_url"] = os.getenv("BLUE_SERVICE_OPENAI_URL")
PROPERTIES["db.host"] = 'blue_db_redis'  # private network ip never changes
PROPERTIES["db.port"] = '6379'
PROPERTIES["rbac.config.folder"] = os.getenv("BLUE_RBAC_CONFIG_FOLDER")

#####
DEVELOPMENT = os.getenv("BLUE_DEPLOY_DEVELOPMENT", "False").lower() == "true"
SECURE_COOKIE = os.getenv("BLUE_DEPLOY_SECURE", "True").lower() == "true"
EMAIL_DOMAIN_WHITE_LIST = os.getenv("BLUE_EMAIL_DOMAIN_WHITE_LIST", "")
DISABLE_AUTHENTICATION = os.getenv('DISABLE_AUTHENTICATION', 'False').lower() == 'true'
FIREBASE_SERVICE_CRED = os.getenv("BLUE_FIREBASE_SERVICE_CRED", "").strip()
FIREBASE_CLIENT_ID = os.getenv("BLUE_FIREBASE_CLIENT_ID", "").strip()
