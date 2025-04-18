import { useDedupStore } from "@/stores/dedup-store";
import { useSessionStore } from "@/stores/session-store";
import _ from "lodash";
import { createRef, useEffect, useMemo } from "react";
import { useRefDimensions } from "../hooks/useRefDimensions";
import UserAvatar from "./UserAvatar";
export default function SessionMemberStack({ sessionId, style }) {
    const sessions = useSessionStore((state) => state.sessions);
    const details = _.get(sessions, [sessionId, "details"], {});
    const members = useMemo(() => {
        return Object.entries(_.get(details, "members", {}))
            .filter((user) => user[1])
            .map((user) => user[0]);
    }, [sessionId, details]);
    const getUserProfile = useDedupStore((state) => state.getUserProfile);
    const owner = _.get(details, "created_by");
    useEffect(() => {
        getUserProfile(owner);
        for (let i = 0; i < _.size(members); i++) {
            getUserProfile(members[i]);
        }
    }, [members]);
    const memberStackref = createRef();
    const { width } = useRefDimensions(memberStackref);
    const size = useMemo(() => {
        let result = _.floor((width + 5) / 45);
        return result - (result < _.size(members) ? 1 : 0);
    }, [width]);
    if (_.isEmpty(members)) {
        return null;
    }
    return (
        <div
            ref={memberStackref}
            className="full-parent-width"
            style={{
                ...style,
                display: "flex",
                gap: 5,
                alignItems: "center",
            }}
        >
            {_.slice(members, 0, size).map((uid) => {
                return <UserAvatar key={uid} userId={uid} />;
            })}
            {size < _.size(members) && (
                <div style={{ marginLeft: 5 }}>
                    &#43;{_.size(members) - size}
                </div>
            )}
        </div>
    );
}
