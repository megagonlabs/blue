import {
    EMPTY_ARRAY,
    EMPTY_OBJECT,
    MESSAGE_OVERFLOW_THRESHOLD,
    TABLE_CELL_HEIGHT,
    USER_ROLES_LOOKUP,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { settlePromises, showAxiosErrorToast } from "@/components/helper";
import UserAvatar from "@/components/sessions/UserAvatar";
import { AppToaster } from "@/components/toaster";
import { useAppStore } from "@/stores/app-store";
import { useDedupStore } from "@/stores/dedup-store";
import { usePlatformStore } from "@/stores/platform-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    ControlGroup,
    Divider,
    EntityTitle,
    FormGroup,
    H3,
    InputGroup,
    Intent,
    MenuItem,
    Size,
    Switch,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { Select } from "@blueprintjs/select";
import {
    Cell,
    Column,
    ColumnHeaderCell,
    RowHeaderCell,
    Table2,
} from "@blueprintjs/table";
import {
    faAt,
    faIdCardClip,
    faTrash,
    faUser,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useMemo, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import EmailCheckbox from "./EmailCheckbox";
export default function AuthenticationConfigurations() {
    const darkMode = useAppStore((state) => state.dark_mode);
    const {
        defaultUserRoleValue,
        loading,
        updateConfigurationValues,
        defaultUserSettingValues,
        allowedDomains,
        allowedEmails,
        addAllowedEmail,
        selectedEmails,
        updateEmailTableSelected,
        removeAllowedEmail,
    } = usePlatformStore(
        useShallow((state) => ({
            defaultUserRoleValue: _.get(
                state.configurations.values,
                "default_user_role",
                "guest"
            ),
            allowedDomains: _.get(
                state.configurations.values,
                "allowed_domains",
                EMPTY_ARRAY
            ),
            allowedEmails: _.get(
                state.configurations.values,
                "allowed_emails",
                EMPTY_ARRAY
            ),
            defaultUserSettingValues: _.get(
                state.configurations.values,
                "default_user_settings",
                EMPTY_OBJECT
            ),
            updateEmailTableSelected: state.updateEmailTableSelected,
            addAllowedEmail: state.addAllowedEmail,
            selectedEmails: state.configurations.selectedEmails,
            removeAllowedEmail: state.removeAllowedEmail,
            updateConfigurationValues: state.updateConfigurationValues,
            loading: state.configurations.loading,
        }))
    );
    const [defaultUserRole, setDefaultUserRole] =
        useState(defaultUserRoleValue);
    const [defaultUserSettings, setDefaultUserSettings] = useState(
        defaultUserSettingValues
    );
    const updateDefaultUserSettings = (key, value) =>
        setDefaultUserSettings({ ...defaultUserSettings, [key]: value });
    useEffect(() => {
        setDefaultUserRole(defaultUserRoleValue);
        setDefaultUserSettings(defaultUserSettingValues);
    }, [defaultUserRoleValue, defaultUserSettingValues]);
    const [saving, setSaving] = useState(false);
    const handleSave = () => {
        setSaving(true);
        const promises = [
            new Promise((resolve, reject) => {
                axios
                    .put("/platform/settings/default_user_role", {
                        value: defaultUserRole,
                    })
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        showAxiosErrorToast(error);
                        reject(false);
                    });
            }),
            new Promise((resolve, reject) => {
                axios
                    .put("/platform/settings/default_user_settings", {
                        value: defaultUserSettings,
                    })
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        showAxiosErrorToast(error);
                        reject(false);
                    });
            }),
        ];
        settlePromises(promises, ({ error }) => {
            if (!error) {
                AppToaster.show({
                    message: "Default user settings & role have been updated.",
                    intent: Intent.SUCCESS,
                });
                updateConfigurationValues({
                    key: "default_user_settings",
                    value: defaultUserSettings,
                });
                updateConfigurationValues({
                    key: "default_user_role",
                    value: defaultUserRole,
                });
            }
            setSaving(false);
        });
    };
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const domainsFiltered = allowedDomains.filter((str) => !_.isEmpty(str));
    const emailsSorted = useMemo(
        () =>
            _.entries(allowedEmails)
                .filter((email) => _.get(email, [1, "allow"], false))
                .map((email) => ({ email: _.get(email, [1, "email"]) })),
        [allowedEmails]
    );
    const users = useDedupStore((state) => state.users);
    const getUserProfileByEmail = useDedupStore(
        (state) => state.getUserProfileByEmail
    );
    const [deleting, setDeleting] = useState(false);
    const onEmailRemove = () => {
        const emails = _.toArray(selectedEmails);
        let promises = [];
        for (let i = 0; i < _.size(emails); i++) {
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(
                            `/platform/settings/allowed_emails/${emails[i]}`
                        )
                        .then(() => {
                            resolve(emails[i]);
                        })
                        .catch(() => {
                            reject(emails[i]);
                        });
                })
            );
        }
        setDeleting(true);
        Promise.allSettled(promises)
            .then((results) => {
                let removed = new Set();
                for (let i = 0; i < _.size(results); i++) {
                    if (_.isEqual("fulfilled", results[i].status)) {
                        removed.add(results[i].value);
                    }
                }
                removed = _.toArray(removed);
                for (let i = 0; i < _.size(removed); i++) {
                    updateEmailTableSelected({
                        email: removed[i],
                        checked: false,
                    });
                    removeAllowedEmail(removed[i]);
                }
            })
            .finally(() => {
                setDeleting(false);
            });
    };
    const emailTableColumns = useMemo(() => {
        return [
            {
                name: <div>&nbsp;</div>,
                key: "checkbox",
                cellRenderer: (rowIndex) => (
                    <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                        <EmailCheckbox
                            email={_.get(
                                emailsSorted,
                                [rowIndex, "email"],
                                null
                            )}
                        />
                    </Cell>
                ),
            },
            {
                name: "UID",
                key: "uid",
                cellRenderer: (rowIndex) => {
                    const email = _.get(
                        emailsSorted,
                        [rowIndex, "email"],
                        null
                    );
                    return (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            {_.get(users, [email, "uid"], "-")}
                        </Cell>
                    );
                },
            },
            {
                name: "Name",
                key: "name",
                cellRenderer: (rowIndex) => {
                    const email = _.get(
                        emailsSorted,
                        [rowIndex, "email"],
                        null
                    );
                    getUserProfileByEmail(email);
                    const uid = _.get(users, [email, "uid"], null);
                    return (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            <div
                                className="full-parent-width"
                                style={{
                                    display: "flex",
                                    gap: 10,
                                    alignItems: "center",
                                }}
                            >
                                <div style={{ width: 25 }}>
                                    <UserAvatar userId={uid} size={25} />
                                </div>
                                <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                                    {_.get(users, [email, "name"], "-")}
                                </div>
                            </div>
                        </Cell>
                    );
                },
            },
            { name: "Email", key: "email" },
        ];
    }, [emailsSorted, users]);
    const [tableKey, setTableKey] = useState(Date.now());
    useEffect(() => {
        setTableKey(Date.now());
    }, [emailTableColumns]);
    const [adding, setAdding] = useState(false);
    const [emailAddress, setEmailAddress] = useState("");
    const whitelistEmail = () => {
        setAdding(true);
        axios
            .put(`/platform/settings/allowed_emails/${emailAddress}`)
            .then(() => {
                getUserProfileByEmail(emailAddress);
                addAllowedEmail(emailAddress);
            })
            .finally(() => {
                setEmailAddress("");
                setAdding(false);
            });
    };
    return (
        <div ref={elementRef} className="setting-container-section-2">
            <EntityTitle
                icon={<FAIcon icon={faIdCardClip} size={20} />}
                heading={H3}
                title="Authentication"
            />
            <Divider style={{ margin: "10px 0px 10px 0px" }} />
            <div
                style={{
                    borderRadius: 2,
                    padding: 15,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY2
                        : Colors.LIGHT_GRAY5,
                }}
            >
                <FormGroup
                    className="margin-0"
                    label="Default user settings & role"
                    subLabel="First-time users are granted these settings and this role when they
                            sign in."
                >
                    <div
                        style={{ marginTop: 10 }}
                        className={loading ? Classes.SKELETON : null}
                    >
                        <FormGroup
                            helperText="Default show session workspace"
                            style={{ marginBottom: 10, marginTop: 10 }}
                        >
                            <Switch
                                checked={_.get(
                                    defaultUserSettings,
                                    "show_workspace",
                                    false
                                )}
                                onChange={(event) =>
                                    updateDefaultUserSettings(
                                        "show_workspace",
                                        event.target.checked
                                    )
                                }
                                size={Size.LARGE}
                                style={{ margin: "0px 0px 5px 0px" }}
                                label="Show workspace"
                            />
                        </FormGroup>
                        <FormGroup
                            helperText="Automatically expand session messages to
                                    show full content"
                            style={{ marginBottom: 10 }}
                        >
                            <Switch
                                checked={_.get(
                                    defaultUserSettings,
                                    "expand_message",
                                    false
                                )}
                                onChange={(event) =>
                                    updateDefaultUserSettings(
                                        "expand_message",
                                        event.target.checked
                                    )
                                }
                                size={Size.LARGE}
                                style={{ margin: "0px 0px 5px 0px" }}
                                label="Expand message"
                            />
                        </FormGroup>
                        <ControlGroup>
                            <Select
                                popoverProps={{
                                    minimal: true,
                                    boundary: popoverBoundary,
                                }}
                                menuProps={{ size: Size.LARGE }}
                                filterable={false}
                                itemRenderer={(item) => (
                                    <MenuItem
                                        text={_.get(
                                            USER_ROLES_LOOKUP,
                                            [item, "text"],
                                            item
                                        )}
                                        onClick={() => {
                                            setDefaultUserRole(item);
                                        }}
                                    />
                                )}
                                items={["developer", "member", "guest"]}
                            >
                                <Button
                                    icon={<FAIcon icon={faUser} />}
                                    text={_.get(
                                        USER_ROLES_LOOKUP,
                                        [defaultUserRole, "text"],
                                        defaultUserRole
                                    )}
                                    variant={ButtonVariant.OUTLINED}
                                    size={Size.LARGE}
                                />
                            </Select>
                            <Button
                                onClick={handleSave}
                                loading={saving}
                                size={Size.LARGE}
                                variant={ButtonVariant.MINIMAL}
                                intent={Intent.SUCCESS}
                                text="Save"
                            />
                        </ControlGroup>
                    </div>
                </FormGroup>
            </div>
            <div
                style={{
                    borderRadius: 2,
                    marginTop: 10,
                    padding: 15,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY2
                        : Colors.LIGHT_GRAY5,
                }}
            >
                <FormGroup
                    className="margin-0"
                    label="Allowed email domains"
                    subLabel='Email domains can only be configured through server environment variable "BLUE_EMAIL_DOMAIN_WHITE_LIST".'
                >
                    <div style={{ marginTop: 10 }}>
                        {_.isEmpty(domainsFiltered) && "-"}
                        {domainsFiltered.map((domain) => (
                            <Tag size="large" minimal>
                                {domain}
                            </Tag>
                        ))}
                    </div>
                </FormGroup>
            </div>
            <div
                style={{
                    borderRadius: 2,
                    marginTop: 10,
                    padding: 15,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY2
                        : Colors.LIGHT_GRAY5,
                }}
            >
                <FormGroup
                    className="margin-0"
                    label="Allowed emails"
                    subLabel="Google account with email address
                    whitelisted below can sign in on the platform regardless of its domain."
                >
                    <div style={{ marginTop: 10 }}>
                        <ControlGroup>
                            <InputGroup
                                leftIcon={<FAIcon icon={faAt} />}
                                size={Size.LARGE}
                                value={emailAddress}
                                onValueChange={(value) => {
                                    setEmailAddress(_.trim(value));
                                }}
                            />
                            <Button
                                onClick={whitelistEmail}
                                disabled={_.isEmpty(emailAddress)}
                                loading={adding}
                                size={Size.LARGE}
                                intent={Intent.SUCCESS}
                                variant={ButtonVariant.MINIMAL}
                                text="Add"
                            />
                        </ControlGroup>
                        <div
                            className="custom-card overflow-hidden"
                            style={{
                                marginTop: 10,
                                height: MESSAGE_OVERFLOW_THRESHOLD + 60,
                            }}
                        >
                            <div style={{ padding: 10 }}>
                                <ButtonGroup
                                    size={Size.LARGE}
                                    variant={ButtonVariant.MINIMAL}
                                >
                                    <Tooltip
                                        content="Remove"
                                        placement="bottom-start"
                                    >
                                        <Button
                                            disabled={_.isEmpty(selectedEmails)}
                                            onClick={onEmailRemove}
                                            intent={Intent.DANGER}
                                            icon={<FAIcon icon={faTrash} />}
                                        />
                                    </Tooltip>
                                </ButtonGroup>
                            </div>
                            <div style={{ height: MESSAGE_OVERFLOW_THRESHOLD }}>
                                <Table2
                                    key={tableKey}
                                    enableRowResizing={false}
                                    numRows={_.size(emailsSorted)}
                                    enableColumnReordering={false}
                                    defaultRowHeight={TABLE_CELL_HEIGHT}
                                    rowHeaderCellRenderer={(rowIndex) => (
                                        <RowHeaderCell
                                            name={
                                                <div
                                                    style={{
                                                        textAlign: "center",
                                                        lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                                    }}
                                                >
                                                    {rowIndex + 1}
                                                </div>
                                            }
                                        />
                                    )}
                                >
                                    {emailTableColumns.map((column, index) => {
                                        const { name, key, cellRenderer } =
                                            column;
                                        const defaultCellRenderer = (
                                            rowIndex
                                        ) => (
                                            <Cell
                                                style={{
                                                    lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                                }}
                                            >
                                                {_.get(
                                                    emailsSorted,
                                                    [rowIndex, key],
                                                    "-"
                                                )}
                                            </Cell>
                                        );
                                        const columnHeaderCellRenderer = () => (
                                            <ColumnHeaderCell
                                                name={name}
                                                menuRenderer={null}
                                            />
                                        );
                                        return (
                                            <Column
                                                key={index}
                                                name={name}
                                                cellRenderer={
                                                    _.isFunction(cellRenderer)
                                                        ? cellRenderer
                                                        : defaultCellRenderer
                                                }
                                                columnHeaderCellRenderer={
                                                    columnHeaderCellRenderer
                                                }
                                            />
                                        );
                                    })}
                                </Table2>
                            </div>
                        </div>
                    </div>
                </FormGroup>
            </div>
        </div>
    );
}
