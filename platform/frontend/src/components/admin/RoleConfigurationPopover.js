import { USER_ROLES_LOOKUP } from "@/components/constant";
import {
    Button,
    Classes,
    Dialog,
    DialogBody,
    DialogFooter,
    HTMLTable,
    Intent,
    Radio,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
const READ_TAG = (
    <Tag minimal intent={Intent.SUCCESS}>
        Read
    </Tag>
);
const WRITE_TAG = (
    <Tag minimal intent={Intent.PRIMARY}>
        Write
    </Tag>
);
const ROLE_PERMISSIONS = {
    admin: (
        <>
            <ul className={Classes.LIST}>
                <li>
                    {READ_TAG}
                    {WRITE_TAG}
                    operations in agent registry for any agent
                </li>
                <li>
                    {READ_TAG}
                    {WRITE_TAG}
                    operations in data registry for any data
                </li>
                <li>
                    administrator tools
                    <ul className={Classes.LIST}>
                        <li>deploy and stop agents</li>
                        <li>update user roles</li>
                    </ul>
                </li>
                <li>
                    development tools
                    <ul className={Classes.LIST}>
                        <li>form designer</li>
                    </ul>
                </li>
                <li>
                    {READ_TAG}
                    {WRITE_TAG}
                    any sessions
                </li>
            </ul>
        </>
    ),
    member: (
        <>
            <ul className={Classes.LIST}>
                <li>
                    {READ_TAG}
                    operations in agent registry for any agent
                </li>
                <li>
                    {READ_TAG}
                    operations in data registry for any data
                </li>
                <li>
                    {READ_TAG}
                    {WRITE_TAG}
                    any sessions that they own / participate
                    <ul>
                        <li>
                            add and modify agent properties for sessions only
                        </li>
                    </ul>
                </li>
            </ul>
        </>
    ),
    developer: (
        <>
            <ul className={Classes.LIST}>
                <li>
                    {READ_TAG}
                    operations in agent registry for any agent
                </li>
                <li>
                    {READ_TAG}
                    operations in data registry for any data
                </li>
                <li>
                    {WRITE_TAG}
                    operations in agent / data registries for any agent / data
                    they created
                    <ul className={Classes.LIST}>
                        <li>deploy and stop agents</li>
                    </ul>
                </li>
                <li>
                    development tools
                    <ul className={Classes.LIST}>
                        <li>form designer</li>
                    </ul>
                </li>
                <li>
                    {READ_TAG}
                    {WRITE_TAG}
                    any sessions that they own / participate
                    <ul>
                        <li>
                            add and modify agent properties for sessions only
                        </li>
                    </ul>
                </li>
            </ul>
        </>
    ),
    demo: (
        <>
            <ul className={Classes.LIST}>
                <li>
                    {READ_TAG}
                    operations in agent registry for any agent
                </li>
                <li>
                    {READ_TAG}
                    any sessions that they participate
                </li>
                <li>
                    {READ_TAG}
                    {WRITE_TAG}
                    any sessions that they own
                </li>
            </ul>
        </>
    ),
    guest: (
        <>
            <ul className={Classes.LIST}>
                <li>
                    {READ_TAG}
                    operations in agent registry for any agent
                </li>
                <li>
                    {READ_TAG}
                    operations in data registry for any data
                </li>
                <li>
                    {READ_TAG}
                    any sessions that they participate
                </li>
            </ul>
        </>
    ),
};
export default function RoleConfigurationPopover({
    isRoleConfigOpen,
    setIsRoleConfigOpen,
}) {
    const [selectedRole, setSelectedRole] = useState(null);
    const [loading, setLoading] = useState(false);
    const { appState } = useContext(AppContext);
    const [updated, setUpdated] = useState(new Set());
    const selectedUsers = appState.admin.selectedUsers;
    const [saved, setSaved] = useState(false);
    const usersMap = appState.admin.usersMap;
    const handleUpdateUserRole = () => {
        setLoading(true);
        let promises = [];
        const selectedUsersArray = _.toArray(selectedUsers);
        for (let i = 0; i < _.size(selectedUsersArray); i++) {
            const uid = selectedUsersArray[i];
            if (updated.has(uid)) {
                continue;
            }
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .put(`/accounts/users/${uid}/role/${selectedRole}`)
                        .then(() => {
                            resolve(uid);
                        })
                        .catch((error) => {
                            AppToaster.show({
                                intent: Intent.DANGER,
                                message: `${error.name}: ${error.message}`,
                            });
                            reject(uid);
                        });
                })
            );
        }
        Promise.allSettled(promises).then((results) => {
            let newUpdated = _.clone(updated);
            for (let i = 0; i < _.size(results); i++) {
                if (!_.isEqual("fulfilled", results[i].status)) continue;
                newUpdated.add(results[i].value);
            }
            if (_.isEqual(_.size(newUpdated), _.size(selectedUsers))) {
                onClose();
            } else {
                setSaved(true);
                setLoading(false);
                setUpdated(newUpdated);
            }
        });
    };
    const onClose = () => {
        if (loading) return;
        setUpdated(new Set());
        setSaved(false);
        setLoading(false);
        setIsRoleConfigOpen(false);
        setSelectedRole(null);
    };
    const handleRadioChange = (event) => {
        setSelectedRole(event.currentTarget.value);
    };
    return (
        <Dialog
            onClose={onClose}
            title="Role Configuration"
            isOpen={isRoleConfigOpen}
        >
            <DialogBody>
                <p>Select a new role</p>
                {["admin", "developer", "member", "demo", "guest"].map(
                    (role) => (
                        <div style={{ display: "flex" }} key={role}>
                            <Radio
                                onChange={handleRadioChange}
                                value={role}
                                style={{ marginTop: 10 }}
                                large
                                checked={_.isEqual(role, selectedRole)}
                            />
                            <Section
                                style={{ marginBottom: 15 }}
                                title={_.get(
                                    USER_ROLES_LOOKUP,
                                    [role, "text"],
                                    role
                                )}
                                compact
                                icon={faIcon({
                                    icon: _.get(
                                        USER_ROLES_LOOKUP,
                                        [role, "icon"],
                                        null
                                    ),
                                })}
                                collapsible
                                collapseProps={{ defaultIsOpen: false }}
                            >
                                <SectionCard
                                    className="role-configuration-permission-list"
                                    padded={false}
                                    style={{ paddingRight: 16.5 }}
                                >
                                    {_.get(
                                        ROLE_PERMISSIONS,
                                        role,
                                        <div style={{ padding: "10px 16.5px" }}>
                                            -
                                        </div>
                                    )}
                                </SectionCard>
                            </Section>
                        </div>
                    )
                )}
                <p>Affected users</p>
                <HTMLTable style={{ width: "100%" }} compact bordered>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Current role</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_.toArray(selectedUsers).map((uid) => {
                            if (updated.has(uid)) {
                                return null;
                            }
                            const user = _.get(usersMap, uid, {});
                            return (
                                <tr key={uid}>
                                    <td>{_.get(user, "name", "-")}</td>
                                    <td>{_.get(user, "email", "-")}</td>
                                    <td>
                                        {_.get(
                                            USER_ROLES_LOOKUP,
                                            [user.role, "text"],
                                            user.role
                                        )}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </HTMLTable>
            </DialogBody>
            <DialogFooter className="position-relative">
                <Button
                    disabled={_.isEmpty(selectedRole)}
                    loading={loading}
                    text="Assign"
                    large
                    onClick={handleUpdateUserRole}
                    intent={Intent.SUCCESS}
                    icon={faIcon({ icon: faCheck })}
                />
                {saved && _.size(updated) < _.size(selectedUsers) ? (
                    <Tag
                        large
                        style={{ position: "absolute", right: 15, top: 15 }}
                        minimal
                        intent={Intent.DANGER}
                    >
                        {Math.abs(_.size(updated) - _.size(selectedUsers))}
                        &nbsp; failed to save
                    </Tag>
                ) : null}
            </DialogFooter>
        </Dialog>
    );
}
