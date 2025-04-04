import { PROFILE_PICTURE_40, USER_ROLES_LOOKUP } from "@/components/constant";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    Card,
    Classes,
    Intent,
    Popover,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faArrowRightFromBracket } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useContext } from "react";
export default function UserAccountPanel() {
    const { user, signOut } = useContext(AuthContext);
    const userRole = _.get(user, "role", null);
    if (_.isEmpty(user)) {
        return null;
    }
    return (
        <Popover
            minimal
            placement="bottom-end"
            content={
                <div
                    className={Classes.RUNNING_TEXT}
                    style={{
                        padding: "20px 40px",
                        textAlign: "center",
                    }}
                >
                    <div style={{ fontWeight: 600 }}>
                        {_.get(user, "email", "-")}
                    </div>
                    <div
                        className={classNames(
                            Classes.TEXT_MUTED,
                            Classes.TEXT_SMALL
                        )}
                    >
                        Managed by&nbsp;
                        {_.get(user, "email_domain", "-")}
                    </div>
                    <div style={{ marginTop: 5 }}>
                        <Tag minimal intent={Intent.PRIMARY}>
                            {_.get(
                                USER_ROLES_LOOKUP,
                                [userRole, "text"],
                                userRole
                            )}
                        </Tag>
                    </div>
                    <Card
                        style={{
                            ...PROFILE_PICTURE_40,
                            height: 80,
                            width: 80,
                            marginTop: 20,
                            marginLeft: "auto",
                            marginRight: "auto",
                        }}
                    >
                        <Image
                            alt=""
                            src={_.get(user, "picture", "").replace(
                                "=s96-c",
                                "=s288-c"
                            )}
                            width={80}
                            height={80}
                        />
                    </Card>
                    <div style={{ marginTop: 20 }}>
                        <Button
                            intent={Intent.WARNING}
                            onClick={signOut}
                            icon={faIcon({
                                icon: faArrowRightFromBracket,
                            })}
                            text="Sign out"
                            variant="outlined"
                            size="large"
                        />
                    </div>
                </div>
            }
        >
            <Tooltip
                minimal
                placement="bottom-end"
                content={
                    <div className={Classes.TEXT_MUTED}>
                        {_.get(user, "name", null)}
                        <br />
                        {_.get(user, "email", null)}
                    </div>
                }
            >
                <Card
                    interactive
                    style={{
                        ...PROFILE_PICTURE_40,
                        marginLeft: 10,
                        marginTop: 4,
                    }}
                >
                    <Image
                        alt=""
                        src={_.get(user, "picture", "")}
                        width={40}
                        height={40}
                    />
                </Card>
            </Tooltip>
        </Popover>
    );
}
