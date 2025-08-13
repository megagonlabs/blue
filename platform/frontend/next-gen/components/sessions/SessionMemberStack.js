import { useDedupStore } from "@/stores/dedup-store";
import { useSessionStore } from "@/stores/session-store";
import _ from "lodash";
import { createRef, useEffect, useMemo } from "react";
import { useToaster } from "../contexts/ToasterContext";
import { useContainerDimensions } from "../hooks/useContainerDimensions";
import UserAvatar from "./UserAvatar";
export default function SessionMemberStack({ sessionId, style }) {
    const sessions = useSessionStore((state) => state.sessions);
    const details = _.get(sessions, [sessionId, "details"], {});
    const members = useMemo(() => {
        return _.entries(_.get(details, "members", {}))
            .filter((user) => user[1])
            .map((user) => user[0]);
    }, [details]);
    const getUserProfileById = useDedupStore(
        (state) => state.getUserProfileById
    );
    const owner = _.get(details, "created_by");
    const { showAxiosErrorToast } = useToaster();
    useEffect(() => {
        getUserProfileById(owner, showAxiosErrorToast);
        for (let i = 0; i < _.size(members); i++) {
            getUserProfileById(members[i], showAxiosErrorToast);
        }
    }, [members, owner, getUserProfileById]);
    const memberStackref = createRef();
    const { width } = useContainerDimensions(memberStackref);
    const size = useMemo(() => {
        let result = _.floor((width + 5) / 45);
        return result - (result < _.size(members) ? 1 : 0);
    }, [width, members]);
    if (_.isEmpty(members)) {
        return null;
    }
    return (
        <div
            ref={memberStackref}
            className="full-parent-width"
            style={{
                display: "flex",
                gap: 5,
                alignItems: "center",
                ...style,
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
