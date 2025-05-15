import { EMPTY_OBJECT, USER_ROLES_LOOKUP } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { settlePromises, showAxiosErrorToast } from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import { useAppStore } from "@/stores/app-store";
import { usePlatformStore } from "@/stores/platform-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    ControlGroup,
    Divider,
    EntityTitle,
    FormGroup,
    H3,
    Intent,
    MenuItem,
    Size,
    Switch,
} from "@blueprintjs/core";
import { Select } from "@blueprintjs/select";
import {
    faIdCardClip,
    faUser,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
export default function AuthenticationConfigurations() {
    const darkMode = useAppStore((state) => state.dark_mode);
    const {
        defaultUserRoleValue,
        loading,
        updateConfigurationValues,
        defaultUserSettingValues,
    } = usePlatformStore(
        useShallow((state) => ({
            defaultUserRoleValue: _.get(
                state.configurations.values,
                "default_user_role",
                "guest"
            ),
            defaultUserSettingValues: _.get(
                state.configurations.values,
                "default_user_settings",
                EMPTY_OBJECT
            ),
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
        </div>
    );
}
