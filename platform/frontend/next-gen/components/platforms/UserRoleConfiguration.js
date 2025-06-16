import { useDedupStore } from "@/stores/dedup-store";
import { usePlatformStore } from "@/stores/platform-store";
import {
    Alignment,
    Button,
    ButtonVariant,
    Card,
    CardList,
    Classes,
    Collapse,
    H3,
    Intent,
    RadioCard,
    Size,
    Tag,
    Tooltip,
    UL,
} from "@blueprintjs/core";
import { faCheck, faIdBadge } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { USER_ROLES_LOOKUP } from "../constants";
import { FAIcon } from "../FAIcon";
import { showAxiosErrorToast } from "../helper";
import UserAvatar from "../sessions/UserAvatar";
const READ = (
    <Tag minimal intent={Intent.SUCCESS}>
        Read
    </Tag>
);
const WRITE = (
    <Tag minimal intent={Intent.PRIMARY}>
        Write
    </Tag>
);
const ROLE_PERMISSIONS = {
    administrator: (
        <UL style={{ paddingLeft: 11 }}>
            <li>
                {READ}
                {WRITE}any session
            </li>
            <li>
                {READ}
                {WRITE}agent registry for any agent
            </li>
            <li>
                {READ}
                {WRITE}data registry for any source
            </li>
            <li>
                {READ}
                {WRITE}operator registry for any operator
            </li>
            <li>
                {READ}
                {WRITE}model registry for any model
            </li>
            <li>
                Tools
                <UL>
                    <li>Form Designer</li>
                </UL>
            </li>
            <li>
                Platform
                <UL>
                    <li>View, deploy, update and stop any agent</li>
                    <li>Update user role(s)</li>
                </UL>
            </li>
        </UL>
    ),
    developer: (
        <UL style={{ paddingLeft: 11 }}>
            <li>
                {READ}
                {WRITE}any session that they own / participate
            </li>
            <li>{READ}agent registry for any agent</li>
            <UL>
                <li>{WRITE}for any agent that they own</li>
            </UL>
            <li>{READ}data registry for any source</li>
            <UL>
                <li>{WRITE}for any source that they own</li>
            </UL>
            <li>{READ}operator registry for any operator</li>
            <UL>
                <li>{WRITE}for any operator that they own</li>
            </UL>
            <li>{READ}model registry for any model</li>
            <UL>
                <li>{WRITE}for any model that they own</li>
            </UL>
            <li>
                Tools
                <UL>
                    <li>Form Designer</li>
                </UL>
            </li>
            <li>
                Platform
                <UL>
                    <li>View any agent</li>
                    <li>Deploy, update and stop any agent that they own</li>
                </UL>
            </li>
        </UL>
    ),
    member: (
        <UL style={{ paddingLeft: 11 }}>
            <li>
                {READ}
                {WRITE}any session that they own / participate
            </li>
            <li>{READ}agent registry for any agent</li>
            <li>{READ}data registry for any source</li>
            <li>{READ}operator registry for any operator</li>
            <li>{READ}model registry for any model</li>
        </UL>
    ),
    guest: (
        <UL style={{ paddingLeft: 11 }}>
            <li>{READ}any session that they participate</li>
            <li>{READ}agent registry for any agent</li>
            <li>{READ}data registry for any source</li>
            <li>{READ}operator registry for any operator</li>
            <li>{READ}model registry for any model</li>
        </UL>
    ),
};
export default function UserRoleConfiguration({
    setShowUserRoleConfiguration,
}) {
    const { selected, updateUserTableSelected, updateUserTableRole } =
        usePlatformStore(
            useShallow((state) => ({
                selected: state.users.selected,
                updateUserTableRole: state.updateUserTableRole,
                updateUserTableSelected: state.updateUserTableSelected,
            }))
        );
    const [selectedRole, setSelectedRole] = useState(null);
    const users = useDedupStore((state) => state.users);
    const handleRoleChange = (event) => {
        setSelectedRole(event.currentTarget.value);
    };
    const [permissionVisibility, setPermissionVisibility] = useState({});
    const togglePermissionVisibility = (role) => {
        let newVisibility = _.cloneDeep(permissionVisibility);
        _.set(newVisibility, role, !_.get(newVisibility, role, false));
        setPermissionVisibility(newVisibility);
    };
    const [loading, setLoading] = useState(false);
    const handleRoleSave = () => {
        let promises = [];
        const selectedUsers = _.toArray(selected);
        for (let i = 0; i < _.size(selectedUsers); i++) {
            const uid = selectedUsers[i];
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .put(`/accounts/users/${uid}/role/${selectedRole}`)
                        .then(() => {
                            resolve(uid);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(uid);
                        });
                })
            );
        }
        setLoading(true);
        Promise.allSettled(promises)
            .then((results) => {
                let updated = new Set();
                for (let i = 0; i < _.size(results); i++) {
                    if (_.isEqual("fulfilled", results[i].status)) {
                        updated.add(results[i].value);
                        updateUserTableSelected({
                            uid: results[i].value,
                            checked: false,
                        });
                    }
                }
                updateUserTableRole({ uids: updated, role: selectedRole });
                if (_.isEqual(_.size(updated), _.size(selected))) {
                    setShowUserRoleConfiguration(false);
                }
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <div className="full-parent-dimension" style={{ display: "flex" }}>
            <div
                className="border-right"
                style={{ padding: 20, width: 220, overflowY: "auto" }}
            >
                <H3>Selected</H3>
                <CardList bordered={false}>
                    {_.toArray(selected).map((uid) => (
                        <Card
                            key={uid}
                            style={{
                                position: "relative",
                                padding: "10px 0px",
                            }}
                        >
                            <div style={{ width: 40 }}>
                                <UserAvatar userId={uid} />
                            </div>
                            <div
                                style={{
                                    width: "calc(100% - 50px)",
                                    height: 40,
                                    marginLeft: 10,
                                    display: "flex",
                                    flexDirection: "column",
                                    justifyContent: "space-between",
                                }}
                            >
                                <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                                    {_.get(users, [uid, "name"], "-")}
                                </div>
                                <div
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        Classes.TEXT_OVERFLOW_ELLIPSIS
                                    )}
                                >
                                    {_.get(users, [uid, "email"], "-")}
                                </div>
                            </div>
                        </Card>
                    ))}
                </CardList>
            </div>
            <div
                style={{
                    padding: 20,
                    overflowY: "auto",
                    width: "calc(100% - 220px)",
                }}
            >
                <CardList>
                    {["administrator", "developer", "member", "guest"].map(
                        (role) => (
                            <RadioCard
                                key={role}
                                inputProps={{ large: true }}
                                compact
                                checked={_.isEqual(selectedRole, role)}
                                showAsSelectedWhenChecked={false}
                                value={role}
                                alignIndicator={Alignment.START}
                                onChange={handleRoleChange}
                            >
                                {_.get(USER_ROLES_LOOKUP, [role, "text"], role)}
                                <div
                                    style={{
                                        position: "absolute",
                                        right: 15,
                                        top: 13.285,
                                    }}
                                >
                                    <Tooltip
                                        content="Permissions"
                                        placement="left"
                                    >
                                        <Button
                                            intent={Intent.PRIMARY}
                                            size={Size.SMALL}
                                            icon={<FAIcon icon={faIdBadge} />}
                                            variant={ButtonVariant.MINIMAL}
                                            onClick={() => {
                                                togglePermissionVisibility(
                                                    role
                                                );
                                            }}
                                        />
                                    </Tooltip>
                                </div>
                                <Collapse
                                    isOpen={_.get(
                                        permissionVisibility,
                                        role,
                                        false
                                    )}
                                >
                                    <div
                                        style={{ paddingRight: 34 }}
                                        className={classNames(
                                            "user-role-configuration-permission-list",
                                            Classes.TEXT_MUTED,
                                            Classes.TEXT_SMALL
                                        )}
                                    >
                                        {_.get(ROLE_PERMISSIONS, role, "-")}
                                    </div>
                                </Collapse>
                            </RadioCard>
                        )
                    )}
                </CardList>
                <Button
                    disabled={_.isEmpty(selectedRole)}
                    loading={loading}
                    style={{ marginTop: 15 }}
                    size={Size.LARGE}
                    intent={Intent.SUCCESS}
                    text="Update"
                    onClick={handleRoleSave}
                    icon={<FAIcon icon={faCheck} />}
                />
            </div>
        </div>
    );
}
