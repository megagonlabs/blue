###### OS / Systems
import os

import pydash
import copy

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
PROPERTIES["embeddings_model"] = os.getenv("BLUE_AGENT_REGISTRY_MODEL")
PROPERTIES["db.host"] = os.getenv("BLUE_DB_HOST", 'blue_db_redis')
PROPERTIES["db.port"] = os.getenv("BLUE_DB_PORT", '6379')
PROPERTIES["rbac.config.folder"] = os.getenv("BLUE_RBAC_CONFIG_FOLDER")

##### Other Settings
DEVELOPMENT = os.getenv("BLUE_DEPLOY_DEVELOPMENT", "False").lower() == "true"
SECURE_COOKIE = os.getenv("BLUE_DEPLOY_SECURE", "True").lower() == "true"
EMAIL_DOMAIN_WHITE_LIST = os.getenv("BLUE_EMAIL_DOMAIN_WHITE_LIST", "megagon.ai")
DISABLE_AUTHENTICATION = os.getenv('DISABLE_AUTHENTICATION', 'False').lower() == 'true'

##### RBAC
import casbin

##### Blue
from blueprint import Platform

ACL = casbin.Enforcer(os.path.join(PROPERTIES["rbac.config.folder"], "model.conf"), os.path.join(PROPERTIES["rbac.config.folder"], "policy.csv"))

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

# Turn on tracking, for only one instance
properties = copy.deepcopy(PROPERTIES)
properties["tracker.autostart"] = True
properties["tracker.output"] = "pubsub"

p = Platform(id=platform_id, properties=properties)


def contains(actions, action):
    return isinstance(actions, list) and action in actions


ACL.add_function('contains', contains)
roles = ACL.get_all_subjects()
ROLE_PERMISSIONS = {}
for role in roles:
    role_permissions = ACL.get_permissions_for_user(role)
    permissions = {}
    for permission in role_permissions:
        resource = permission[1]
        if pydash.objects.has(permissions, resource):
            permissions[resource].append(permission[2])
        else:
            pydash.objects.set_(permissions, resource, [permission[2]])
    pydash.objects.set_(ROLE_PERMISSIONS, role, permissions)
