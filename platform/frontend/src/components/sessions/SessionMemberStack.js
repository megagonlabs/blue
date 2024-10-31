import { AppContext } from "@/components/contexts/app-context";
import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Image from "next/image";
import { useContext, useEffect, useMemo } from "react";
import { PROFILE_PICTURE_40 } from "../constant";
export default function SessionMemberStack({
    sessionId,
    fetchUsers = true,
    size = 3,
}) {
    const { appState, appActions } = useContext(AppContext);
    const { sessionDetails } = appState.session;
    const members = useMemo(() => {
        return Object.entries(_.get(sessionDetails, [sessionId, "members"], {}))
            .filter((user) => user[1])
            .map((user) => user[0]);
    }, [sessionId, sessionDetails]);
    const owner = _.get(sessionDetails, [sessionId, "created_by"]);
    useEffect(() => {
        if (!fetchUsers) return;
        const hasUserProfile = _.has(appState, ["app", "users", owner]);
        if (!hasUserProfile) {
            let pendingRquest = _.get(
                appState,
                ["app", "pendingRequests", `getUserProfile ${owner}`],
                false
            );
            if (!pendingRquest) {
                appActions.app.getUserProfile(owner);
            }
        }
        for (let i = 0; i < size; i++) {
            const uid = members[i];
            const hasUserProfile = _.has(appState, ["app", "users", uid]);
            if (!hasUserProfile) {
                let pendingRquest = _.get(
                    appState,
                    ["app", "pendingRequests", `getUserProfile ${uid}`],
                    false
                );
                if (!pendingRquest) {
                    appActions.app.getUserProfile(uid);
                }
            }
        }
    }, [members]); // eslint-disable-line react-hooks/exhaustive-deps
    const USER_AVATAR_STYLE = { ...PROFILE_PICTURE_40, marginLeft: -10 };
    if (_.isEmpty(sessionId)) return null;
    return (
        <div style={{ display: "flex", alignItems: "center" }}>
            {_.has(appState, ["app", "users", owner]) ? (
                <Card style={{ ...USER_AVATAR_STYLE, zIndex: size + 1 }}>
                    <Image
                        alt=""
                        src={_.get(
                            appState,
                            ["app", "users", owner, "picture"],
                            ""
                        )}
                        width={40}
                        height={40}
                    />
                </Card>
            ) : (
                <Card className={Classes.SKELETON} style={USER_AVATAR_STYLE} />
            )}
            {members.slice(0, size).map((uid, index) => {
                const hasUserProfile = _.has(appState, ["app", "users", uid]);
                if (!hasUserProfile) {
                    return (
                        <Card
                            key={uid}
                            className={Classes.SKELETON}
                            style={USER_AVATAR_STYLE}
                        />
                    );
                }
                const user = _.get(appState, ["app", "users", uid], {});
                return (
                    <Card
                        key={uid}
                        style={{ ...USER_AVATAR_STYLE, zIndex: size - index }}
                    >
                        <Image
                            alt=""
                            src={_.get(user, "picture", "")}
                            width={40}
                            height={40}
                        />
                    </Card>
                );
            })}
            {_.size(members) > size ? (
                <div style={{ marginLeft: 5 }}>
                    &#43;{_.size(members) - size}
                </div>
            ) : null}
        </div>
    );
}
