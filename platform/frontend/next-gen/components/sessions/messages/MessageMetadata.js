import Timestamp from "@/components/Timestamp";
import { useAgentStore } from "@/stores/agent-store";
import { useDedupStore } from "@/stores/dedup-store";
import { Classes } from "@blueprintjs/core";
import _ from "lodash";
import { memo, useEffect } from "react";
import { useShallow } from "zustand/react/shallow";
function MessageMetadata({ message }) {
    const agentMetadata = useAgentStore((state) => state.metadata);
    const id = _.get(message, "metadata.id", null);
    const createdBy = _.get(message, "metadata.created_by", null);
    const isUser = _.isEqual(createdBy, "USER");
    const { getUserProfileById, getAgentMetadata, users } = useDedupStore(
        useShallow((state) => ({
            getUserProfileById: state.getUserProfileById,
            getAgentMetadata: state.getAgentMetadata,
            users: state.users,
        }))
    );
    useEffect(() => {
        if (isUser) {
            getUserProfileById(id);
        } else {
            getAgentMetadata(createdBy);
        }
    }, [createdBy, getAgentMetadata, getUserProfileById, id, isUser]);
    return (
        <div style={{ lineHeight: "20px", display: "flex", gap: 10 }}>
            <div className={Classes.TEXT_MUTED}>
                <Timestamp placement="bottom" epoch={message.timestamp} />
            </div>
            <div>
                {isUser
                    ? _.get(users, [id, "name"], id)
                    : _.get(agentMetadata, [id, "displayName"], id)}
            </div>
        </div>
    );
}
export default memo(MessageMetadata);
