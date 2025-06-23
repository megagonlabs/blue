import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Classes,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowRightFromBracket,
    faCog,
    faGlasses,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "./FAIcon";
import NerdStats from "./NerdStats";
import { USER_ROLES_LOOKUP } from "./constants";
import SettingsContainer from "./settings/SettingsContainer";
export default function AccountPanel({ isExpanded }) {
    const { user, logout } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            logout: state.logout,
        }))
    );
    const userRole = _.get(user, "role", null);
    const addContainer = useGridStore((state) => state.addContainer);
    return (
        <Card
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
                        Managed by&nbsp;
                        {_.get(user, "email_domain", "-")}
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
                    <ButtonGroup fill>
                        <Button
                            onClick={() =>
                                addContainer({
                                    icon: faCog,
                                    title: "Account Settings",
                                    content: <SettingsContainer />,
                                })
                            }
                            variant={ButtonVariant.OUTLINED}
                            icon={<FAIcon icon={faCog} />}
                            text="Settings"
                            size={Size.LARGE}
                        />
                        <Tooltip
                            placement="bottom-end"
                            content="Stats. for nerds"
                        >
                            <Button
                                onClick={() => {
                                    addContainer({
                                        icon: faGlasses,
                                        title: "Stats.",
                                        content: <NerdStats />,
                                        uniqueId: "NerdStats",
                                    });
                                }}
                                variant={ButtonVariant.MINIMAL}
                                size={Size.LARGE}
                                icon={<FAIcon icon={faGlasses} />}
                            />
                        </Tooltip>
                    </ButtonGroup>
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
