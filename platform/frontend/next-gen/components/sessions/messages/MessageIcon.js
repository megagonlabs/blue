import { REGISTRY_ENTITY_ICON_WRAPPER_STYLES } from "@/components/constants";
import RegistryEntityIcon from "@/components/registries/RegistryEntityIcon";
import { useAgentStore } from "@/stores/agent-store";
import { useDedupStore } from "@/stores/dedup-store";
import _ from "lodash";
import { useEffect } from "react";
import { useShallow } from "zustand/react/shallow";
import UserAvatar from "../UserAvatar";
export default function MessageIcon({ metadata }) {
    const createdBy = _.get(metadata, "created_by", null);
    const id = _.get(metadata, "id", null);
    const isUser = _.isEqual(createdBy, "USER");
    const { getUserProfile, getAgentMetadata } = useDedupStore(
        useShallow((state) => ({
            getUserProfile: state.getUserProfile,
            getAgentMetadata: state.getAgentMetadata,
        }))
    );
    const agentMetadata = useAgentStore((state) => state.metadata);
    useEffect(() => {
        if (isUser) {
            getUserProfile(id);
        } else {
            getAgentMetadata(createdBy);
        }
    }, [createdBy]);
    if (isUser) {
        return <UserAvatar userId={id} />;
    }
    return (
        <div
            className="padding-0 overflow-hidden custom-card"
            style={REGISTRY_ENTITY_ICON_WRAPPER_STYLES}
        >
            <RegistryEntityIcon
                content={_.get(agentMetadata, [agent.name, "icon"], null)}
            />
        </div>
    );
}
