import _ from "lodash";
export const defaultState = {
    registryName: process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME,
    list: [],
    search: false,
    loading: true,
    icon: {},
    systemAgents: {},
    filter: {
        keywords: "",
        hybrid: false,
        approximate: true,
        type: "",
        page: 0,
        page_size: 10,
    },
    pendingAttributesRequests: {},
};
export default function agentReducer(state = defaultState, { type, payload }) {
    let { icon, pendingAttributesRequests } = state;
    switch (type) {
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
