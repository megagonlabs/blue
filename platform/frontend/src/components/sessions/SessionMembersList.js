import { PROFILE_PICTURE_40 } from "@/components/constant";
import { Card, Classes, InputGroup, Intent, Tag } from "@blueprintjs/core";
import { faCircleUser, faSearch } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
export default function SessionMembersList() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionIdFocus}/members`)
            .then((response) => {
                setMembers(_.get(response, "data.results", []));
                setLoading(false);
            });
    }, []);
    const LOADING_PLACEHOLDER = (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                gap: 15,
                padding: "7.5px 15px",
                borderRadius: 2,
            }}
        >
            <Card
                className={Classes.SKELETON}
                style={{
                    borderRadius: "50%",
                    padding: 0,
                    overflow: "hidden",
                    width: 40,
                    height: 40,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}
            />
            <div className={Classes.SKELETON} style={{ width: 163.56 }}>
                &nbsp;
            </div>
        </div>
    );
    return (
        <div
            style={{ minHeight: 202, height: _.isEmpty(members) ? 202 : null }}
        >
            <InputGroup
                leftIcon={faIcon({ icon: faSearch })}
                placeholder="Find members"
                large
                style={{ marginBottom: 7 }}
            />
            {loading ? (
                <>
                    {LOADING_PLACEHOLDER}
                    {LOADING_PLACEHOLDER}
                </>
            ) : (
                members.map((member) => {
                    const user = _.get(
                        appState,
                        ["app", "users", member.uid],
                        {}
                    );
                    const hasUserProfile = _.has(appState, [
                        "app",
                        "users",
                        member.uid,
                    ]);
                    if (!hasUserProfile) {
                        appActions.app.getUserProfile(member.uid);
                    }
                    return (
                        <div
                            key={member.uid}
                            className="on-hover-background-color-bp-gray-3"
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 15,
                                padding: "7.5px 15px",
                                borderRadius: 2,
                                position: "relative",
                            }}
                        >
                            {hasUserProfile ? (
                                <Card
                                    style={PROFILE_PICTURE_40}
                                    className="margin-0"
                                >
                                    <Image
                                        alt=""
                                        src={_.get(user, "picture", "")}
                                        width={40}
                                        height={40}
                                    />
                                </Card>
                            ) : (
                                <Card
                                    style={{
                                        borderRadius: "50%",
                                        padding: 0,
                                        overflow: "hidden",
                                        width: 40,
                                        height: 40,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                    }}
                                >
                                    {faIcon({
                                        icon: faCircleUser,
                                        style: { color: "#5f6b7c" },
                                    })}
                                </Card>
                            )}
                            <div>
                                <div style={{ fontWeight: 600 }}>
                                    {_.get(user, "display_name", "-")}
                                </div>
                                <div
                                    className={classNames(
                                        Classes.TEXT_DISABLED,
                                        Classes.TEXT_SMALL
                                    )}
                                >
                                    {_.get(user, "email", "-")}
                                </div>
                            </div>
                            {member.owner ? (
                                <Tag
                                    minimal
                                    intent={Intent.PRIMARY}
                                    style={{
                                        position: "absolute",
                                        right: 15,
                                    }}
                                >
                                    Owner
                                </Tag>
                            ) : null}
                        </div>
                    );
                })
            )}
        </div>
    );
}
