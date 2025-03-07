import _ from "lodash";
import { allEnv } from "next-runtime-env";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export const defaultState = {
    registryName: NEXT_PUBLIC_AGENT_REGISTRY_NAME,
    list: [],
    search: false,
    loading: true,
    icon: {},
    systemAgents: {},
    propertyLookups: {},
    filter: {
        keywords: "",
        hybrid: false,
        approximate: true,
        type: "",
        page: 0,
        page_size: 10,
    },
    pendingAttributesRequests: {},
    agentGroupSelection: {
        available: {},
        added: {},
    },
};
export default function agentReducer(state = defaultState, { type, payload }) {
    let {
        icon,
        pendingAttributesRequests,
        propertyLookups,
        agentGroupSelection,
    } = state;
    switch (type) {
        case "agent/agent_group/selection/clear": {
            return {
                ...state,
                agentGroupSelection: { available: {}, added: {} },
            };
        }
        case "agent/agent_group/selection/set": {
            const { name, type, value } = payload;
            _.set(agentGroupSelection, [type, name], value);
            return { ...state, agentGroupSelection };
        }
        case "agent/propertyLookups/set": {
            let agentLookups = _.get(propertyLookups, payload.agent, {});
            _.set(agentLookups, payload.key, payload.value);
            _.set(propertyLookups, payload.agent, agentLookups);
            return { ...state, propertyLookups };
        }
        case "agent/pendingAttributesRequests/set": {
            _.set(pendingAttributesRequests, payload.key, payload.value);
            return { ...state, pendingAttributesRequests };
        }
        case "agent/list/set": {
            for (let i = 0; i < _.size(payload); i++) {
                let tempIcon = payload[i].icon;
                if (
                    !_.isEmpty(tempIcon) &&
                    !_.startsWith(tempIcon, "data:image/")
                ) {
                    tempIcon = _.split(tempIcon, ":");
                }
                _.set(icon, payload[i].name, tempIcon);
            }
            return {
                ...state,
                list: payload,
                icon: icon,
                filter: defaultState.filter,
                search: false,
                loading: false,
            };
        }
        case "agent/systemAgents/set": {
            return {
                ...state,
                systemAgents: {
                    ...state.systemAgents,
                    [payload.key]: payload.value,
                },
            };
        }
        case "agent/icon/set": {
            return {
                ...state,
                icon: { ...state.icon, [payload.key]: payload.value },
            };
        }
        case "agent/search/set": {
            return { ...state, ...payload, search: true, loading: false };
        }
        case "agent/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        default:
            return state;
    }
}
