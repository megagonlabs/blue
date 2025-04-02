import { useAuthStore } from "@/stores/auth-store";
import {
    Button,
    ButtonVariant,
    Card,
    Classes,
    Intent,
    Size,
    Tag,
} from "@blueprintjs/core";
import {
    faArrowRightFromBracket,
    faCog,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import Image from "next/image";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "./FAIcon";
import { USER_ROLES_LOOKUP } from "./constants";

export default function AccountPanel({ isExpanded }) {
    const { user } = useAuthStore(
        useShallow((state) => ({ user: state.user }))
    );
    const logout = useAuthStore((state) => state.logout);
    const userRole = _.get(user, "role", null);
    return (
        <Card
            interactive
            className={classNames({
                "full-parent-dimension": true,
                "overflow-hidden": true,
                "padding-0": !isExpanded,
            })}
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
                        width: 120,
                        height: 101.43,
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between",
                    }}
                >
                    <Button
                        variant={ButtonVariant.OUTLINED}
                        icon={<FAIcon icon={faCog} />}
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
