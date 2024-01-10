export const defaultState = {
    registryName: "default",
    list: [],
    search: false,
    filter: {
        keywords: "",
        hybrid: false,
        approximate: true,
        type: "agent",
    },
};
export default function agentReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "agent/list/set":
            return {
                ...state,
                list: payload,
                filter: defaultState.filter,
                search: false,
            };
        case "agent/search/set":
            return { ...state, ...payload, search: true };
        default:
            return state;
    }
}
