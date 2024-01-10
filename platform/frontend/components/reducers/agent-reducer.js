export const defaultState = {
    registryName: "default",
    list: [],
    search: false,
    filter: {
        keywords: "",
        hybrid: true,
        approximate: false,
        type: "agent",
    },
};
export default function agentReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "agent/list/set":
            return { ...state, list: payload, search: false };
        case "agent/search/set":
            return { ...state, ...payload, search: true };
        default:
            return state;
    }
}
