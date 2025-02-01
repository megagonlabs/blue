import {
    Button,
    Classes,
    Dialog,
    DialogBody,
    DialogFooter,
    HTMLSelect,
    Intent,
    Menu,
    MenuItem,
    Section,
    SectionCard,
    Switch,
} from "@blueprintjs/core";
import {
    faCheck,
    faComments,
    faSidebar,
    faTableColumns,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useState } from "react";
import { axiosErrorToast, settlePromises } from "../helper";
import { faIcon } from "../icon";
const EXPLANATION_TEXT = {
    style: {
        marginTop: 5,
        whiteSpace: "initial",
        lineHeight: "initial",
    },
    className: classNames(Classes.TEXT_SMALL, Classes.TEXT_MUTED),
};
const SECTION_LABEL_STYLE = { marginBottom: 5 };
const DEFAULT_SETTINGS = {
    compact_sidebar: {
        title: "Compact sidebar",
        description: "Use minimal style for navigation menu",
        icon: faSidebar,
    },
    show_workspace: {
        title: "Show workspace",
        description: "Default show session workspace",
        icon: faTableColumns,
    },
    conversation_view: {
        title: "Conversation view",
        description: "Whether messages should appear on opposite sides",
        icon: faComments,
    },
};
export default function AuthConfigurationPopover({
    isAuthConfigOpen,
    setIsAuthConfigOpen,
}) {
    const [loading, setLoading] = useState(false);
    const [defaultRole, setDefaultRole] = useState("guest");
    const [defaultSettings, setDefaultSettings] = useState({
        compact_sidebar: false,
        show_workspace: false,
        conversation_view: false,
    });
    const getPlatformSettings = () => {
        setLoading(true);
        axios.get("/platform/settings").then((response) => {
            setDefaultRole(
                _.get(response, "data.settings.default_user_role", "guest")
            );
            setDefaultSettings({
                compact_sidebar: _.get(
                    response,
                    "data.settings.default_user_settings.compact_sidebar",
                    false
                ),
                show_workspace: _.get(
                    response,
                    "data.settings.default_user_settings.show_workspace",
                    false
                ),
                conversation_view: _.get(
                    response,
                    "data.settings.default_user_settings.conversation_view",
                    false
                ),
            });
            setLoading(false);
        });
    };
    useEffect(() => {
        if (isAuthConfigOpen) getPlatformSettings();
    }, [isAuthConfigOpen]);
    const savePlatformDefaultUserRole = () => {
        setLoading(true);
        const tasks = [
            new Promise((resolve, reject) => {
                axios
                    .put("/platform/settings/default_user_role", {
                        value: defaultRole,
                    })
                    .then(() => resolve(true))
                    .catch((error) => {
                        axiosErrorToast(error);
                        reject(false);
                    });
            }),
            new Promise((resolve, reject) => {
                axios
                    .put("/platform/settings/default_user_settings", {
                        value: defaultSettings,
                    })
                    .then(() => resolve(true))
                    .catch((error) => {
                        axiosErrorToast(error);
                        reject(false);
                    });
            }),
        ];
        settlePromises(tasks, () => setLoading(false));
    };
    const onClose = () => {
        if (loading) return;
        setIsAuthConfigOpen(false);
    };
    const updateDefaultSettings = (key, value) =>
        setDefaultSettings({ ...defaultSettings, [key]: value });
    return (
        <Dialog
            onClose={onClose}
            title="Auth. Configuration"
            isOpen={isAuthConfigOpen}
        >
            <DialogBody>
                <Section compact>
                    <SectionCard>
                        <div
                            style={{
                                display: "flex",
                                gap: 15,
                                alignItems: "center",
                                justifyContent: "space-between",
                            }}
                        >
                            <div
                                style={{
                                    maxWidth: "calc(100% - 134px)",
                                }}
                            >
                                <div style={SECTION_LABEL_STYLE}>
                                    Default User Role
                                </div>
                                <div
                                    className={classNames(
                                        Classes.TEXT_SMALL,
                                        Classes.TEXT_MUTED
                                    )}
                                >
                                    This role will be assigned to those
                                    first-time users signning in on the
                                    platform.
                                </div>
                            </div>
                            <HTMLSelect
                                className={loading ? Classes.SKELETON : null}
                                large
                                value={defaultRole}
                                onChange={(event) =>
                                    setDefaultRole(event.target.value)
                                }
                            >
                                {[
                                    "admin",
                                    "developer",
                                    "member",
                                    "demo",
                                    "guest",
                                ].map((role) => (
                                    <option
                                        key={role}
                                        label={_.capitalize(role)}
                                        value={role}
                                    />
                                ))}
                            </HTMLSelect>
                        </div>
                    </SectionCard>
                    <SectionCard>
                        <div style={SECTION_LABEL_STYLE}>
                            Default User Settings
                        </div>
                        <Menu large style={{ padding: 0 }}>
                            {[
                                "compact_sidebar",
                                "show_workspace",
                                "conversation_view",
                            ].map((key) => (
                                <MenuItem
                                    key={key}
                                    text={
                                        <div style={{ marginLeft: 3 }}>
                                            <div>
                                                {_.get(
                                                    DEFAULT_SETTINGS,
                                                    [key, "title"],
                                                    "-"
                                                )}
                                            </div>
                                            <div {...EXPLANATION_TEXT}>
                                                {_.get(
                                                    DEFAULT_SETTINGS,
                                                    [key, "description"],
                                                    "-"
                                                )}
                                            </div>
                                        </div>
                                    }
                                    icon={faIcon({
                                        icon: _.get(
                                            DEFAULT_SETTINGS,
                                            [key, "icon"],
                                            null
                                        ),
                                    })}
                                    labelElement={
                                        <Switch
                                            checked={_.get(
                                                defaultSettings,
                                                key,
                                                false
                                            )}
                                            className={
                                                loading
                                                    ? Classes.SKELETON
                                                    : null
                                            }
                                            onChange={(event) =>
                                                updateDefaultSettings(
                                                    key,
                                                    event.target.checked
                                                )
                                            }
                                            large
                                        />
                                    }
                                />
                            ))}
                        </Menu>
                    </SectionCard>
                </Section>
            </DialogBody>
            <DialogFooter>
                <Button
                    loading={loading}
                    text="Save"
                    large
                    onClick={savePlatformDefaultUserRole}
                    intent={Intent.SUCCESS}
                    icon={faIcon({ icon: faCheck })}
                />
            </DialogFooter>
        </Dialog>
    );
}
