import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonVariant,
    Card,
    Classes,
    hideContextMenu,
    Intent,
    Menu,
    MenuItem,
    showContextMenu,
    Size,
    Tag,
} from "@blueprintjs/core";
import {
    faArrowRightFromBracket,
    faBrowsers,
    faSlidersSimple,
    faSquareBinary,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useCallback, useMemo } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "./FAIcon";
import NerdStatsContainer from "./NerdStatsContainer";
import { USER_ROLES_LOOKUP } from "./constants";
import SettingsContainer from "./settings/SettingsContainer";
export default function AccountPanel({ isExpanded }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { user, logout } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            logout: state.logout,
        }))
    );
    const userRole = _.get(user, "role", null);
    const addContainer = useGridStore((state) => state.addContainer);
    const handleClose = useCallback(() => {
        hideContextMenu();
    }, []);
    const menu = useMemo(
        () => (
            <Menu size={Size.LARGE} onClick={handleClose}>
                <MenuItem
                    icon={<FAIcon icon={faSquareBinary} />}
                    labelElement={<FAIcon icon={faBrowsers} />}
                    text="Stats. for nerds"
                    onClick={() => {
                        addContainer({
                            icon: faSquareBinary,
                            title: "Stats. for nerds",
                            content: <NerdStatsContainer />,
                            uniqueId: "NerdStatsContainer",
                        });
                    }}
                />
            </Menu>
        ),
        [handleClose, addContainer]
    );
    const handleContextMenu = useCallback(
        (event) => {
            // ensure `preventDefault` is called just before `showContextMenu` and in the same event handler to prevent the
            // default browser context menu from hiding your custom context menu
            event.preventDefault();
            showContextMenu({
                isDarkTheme: darkMode,
                content: menu,
                onClose: handleClose,
                targetOffset: {
                    left: event.clientX,
                    top: event.clientY,
                },
            });
        },
        [handleClose, darkMode, menu]
    );
    return (
        <Card
            onContextMenu={handleContextMenu}
            interactive
            className={classNames(
                "border-radius-10",
                "full-parent-dimension",
                "overflow-hidden",
                { "padding-0": !isExpanded }
            )}
        >
            {!isExpanded && (
                <Image
                    alt=""
                    src={_.get(user, "picture", "").replace(
                        "=s96-c",
                        "=s288-c"
                    )}
                    width={65}
                    height={65}
                />
            )}
            <div style={{ display: "flex", gap: 40, alignItems: "center" }}>
                <div style={{ width: 140 }}>
                    <div style={{ fontWeight: 600 }}>
                        {_.get(user, "name", null)}
                    </div>
                    <div style={{ fontWeight: 600 }}>
                        {_.get(user, "email", "-")}
                    </div>
                    <div
                        style={{ marginTop: 10 }}
                        className={classNames(
                            Classes.TEXT_MUTED,
                            Classes.TEXT_SMALL
                        )}
                    >
                        Managed by {_.get(user, "email_domain", "-")}
                    </div>
                    <div style={{ marginTop: 10 }}>
                        <Tag size={Size.LARGE} minimal intent={Intent.PRIMARY}>
                            {_.get(
                                USER_ROLES_LOOKUP,
                                [userRole, "text"],
                                userRole
                            )}
                        </Tag>
                    </div>
                </div>
                <div
                    style={{
                        width: 150,
                        height: 101.43,
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between",
                    }}
                >
                    <Button
                        onClick={() =>
                            addContainer({
                                icon: faSlidersSimple,
                                title: "Account Settings",
                                content: <SettingsContainer />,
                                uniqueId: "SettingsContainer",
                            })
                        }
                        variant={ButtonVariant.OUTLINED}
                        icon={<FAIcon icon={faSlidersSimple} />}
                        text="Settings"
                        size={Size.LARGE}
                    />
                    <Button
                        intent={Intent.WARNING}
                        icon={<FAIcon icon={faArrowRightFromBracket} />}
                        variant={ButtonVariant.OUTLINED}
                        onClick={logout}
                        text="Sign out"
                        size={Size.LARGE}
                    />
                </div>
            </div>
        </Card>
    );
}
