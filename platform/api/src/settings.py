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
PROPERTIES["embeddings_model"] = os.getenv("BLUE_AGENT_REGISTRY_MODEL")
PROPERTIES["db.host"] = os.getenv("BLUE_DB_HOST", 'blue_db_redis')
PROPERTIES["rbac.config.folder"] = os.getenv("BLUE_RBAC_CONFIG_FOLDER")

##### Other Settings
DEVELOPMENT = os.getenv("BLUE_DEPLOY_DEVELOPMENT", "False").lower() == "true"
SECURE_COOKIE = os.getenv("BLUE_DEPLOY_SECURE", "True").lower() == "true"

##### RBAC
import casbin

ACL = casbin.Enforcer(os.path.join(PROPERTIES["rbac.config.folder"], "model.conf"), os.path.join(PROPERTIES["rbac.config.folder"], "policy.csv"))


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
