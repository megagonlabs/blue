import { AppContext } from "@/components/contexts/app-context";
import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Image from "next/image";
import { useContext, useEffect, useMemo } from "react";
import { PROFILE_PICTURE_40 } from "../constant";
export default function MemberPreview() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionIdFocus, sessionDetails } = appState.session;
    const members = useMemo(() => {
        return Object.entries(
            _.get(sessionDetails, [sessionIdFocus, "members"], {})
        )
            .filter((user) => user[1])
            .map((user) => user[0]);
    }, [sessionIdFocus, sessionDetails]);
    const owner = _.get(sessionDetails, [sessionIdFocus, "created_by"]);
    useEffect(() => {
        const hasUserProfile = _.has(appState, ["app", "users", owner]);
        if (!hasUserProfile) {
            appActions.app.getUserProfile(owner);
        }
        for (let i = 0; i < 3; i++) {
            const uid = members[i];
            const hasUserProfile = _.has(appState, ["app", "users", uid]);
            if (!hasUserProfile) {
                appActions.app.getUserProfile(uid);
            }
        }
    }, [members]);
    const USER_AVATAR_STYLE = { ...PROFILE_PICTURE_40, marginLeft: -10 };
    if (_.isEmpty(sessionIdFocus)) return null;
    return (
        <div style={{ display: "flex", alignItems: "center" }}>
            {_.has(appState, ["app", "users", owner]) ? (
                <Card style={{ ...USER_AVATAR_STYLE, zIndex: 4 }}>
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
            {members.slice(0, 3).map((uid, index) => {
                const hasUserProfile = _.has(appState, ["app", "users", uid]);
                if (!hasUserProfile) {
                    return (
                        <Card
                            className={Classes.SKELETON}
                            style={USER_AVATAR_STYLE}
                        />
                    );
                }
                const user = _.get(appState, ["app", "users", uid], {});
                return (
                    <Card style={{ ...USER_AVATAR_STYLE, zIndex: 3 - index }}>
                        <Image
                            alt=""
                            src={_.get(user, "picture", "")}
                            width={40}
                            height={40}
                        />
                    </Card>
                );
            })}
            {_.size(members) > 3 ? (
                <div round minimal style={{ marginLeft: 5 }}>
                    &#43;{_.size(members) - 3}
                </div>
            ) : null}
        </div>
    );
}
