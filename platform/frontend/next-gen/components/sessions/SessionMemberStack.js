import { useDedupStore } from "@/stores/dedup-store";
import { useSessionStore } from "@/stores/session-store";
import _ from "lodash";
import { useEffect, useMemo } from "react";
import withAutoSizer from "../hocs/withAutoSizer";
import UserAvatar from "./UserAvatar";
function SessionMemberStack({ width, height, sessionId }) {
    const sessions = useSessionStore((state) => state.sessions);
    const details = _.get(sessions, [sessionId, "details"], {});
    const members = useMemo(() => {
        return [
            "5WgRzdacRdOEvj8JBmCXFZSvWmH3",
            "I98zotQIhShIbOBlefGuY6L4tT42",
            "5WgRzdacRdOEvj8JBmCXFZSvWmH3",
            "I98zotQIhShIbOBlefGuY6L4tT42",
            "5WgRzdacRdOEvj8JBmCXFZSvWmH3",
            "I98zotQIhShIbOBlefGuY6L4tT42",
            "5WgRzdacRdOEvj8JBmCXFZSvWmH3",
            "I98zotQIhShIbOBlefGuY6L4tT42",
        ];
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
    const size = useMemo(() => {
        let result = _.floor((width + 5) / 45) - 1;
        return result - (result < _.size(members) ? 1 : 0);
    }, [width]);
    return (
        <div
            style={{
                width,
                height,
                display: "flex",
                gap: 5,
                alignItems: "center",
            }}
        >
            <UserAvatar userId={owner} />
            {_.slice(members, 0, size).map((uid) => {
                return <UserAvatar userId={uid} />;
            })}
            {size < _.size(members) && (
                <div style={{ marginLeft: 5 }}>
                    &#43;{_.size(members) - size}
                </div>
            )}
        </div>
    );
}
export default withAutoSizer(SessionMemberStack);
