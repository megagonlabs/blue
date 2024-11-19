import {
    Button,
    Card,
    Classes,
    Dialog,
    DialogBody,
    DialogFooter,
    HTMLSelect,
    Intent,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
import { faIcon } from "../icon";
export default function AuthConfigurationPopover({
    isAuthConfigOpen,
    setIsAuthConfigOpen,
}) {
    const [loading, setLoading] = useState(false);
    const [defaultRole, setDefaultRole] = useState("guest");
    const getPlatformSettings = () => {
        setLoading(true);
        axios.get("/platform/settings").then((response) => {
            setDefaultRole(
                _.get(response, "data.settings.default_user_role", "guest")
            );
            setLoading(false);
        });
    };
    useEffect(() => {
        if (isAuthConfigOpen) getPlatformSettings();
    }, [isAuthConfigOpen]);
    const savePlatformDefaultUserRole = () => {
        setLoading(true);
        axios
            .put("/platform/settings/default_user_role", { value: defaultRole })
            .then(() => {
                setLoading(false);
            });
    };
    const onClose = () => {
        if (loading) return;
        setIsAuthConfigOpen(false);
    };
    return (
        <Dialog
            onClose={onClose}
            title="Auth. Configuration"
            isOpen={isAuthConfigOpen}
        >
            <DialogBody>
                <Card compact>
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
                                maxWidth: "calc(100% - 156.57px)",
                            }}
                        >
                            <label style={{ fontWeight: 600 }}>
                                Default User Role
                            </label>
                            <div>
                                This role is assigned to the first-time users
                                signning in on the platform.
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
                </Card>
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
