###### OS / Systems
import os

import pydash

##### RBAC
import casbin

##### Blue
from blue.platform import Platform
from blue.properties import PROPERTIES

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
