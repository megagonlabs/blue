export const defaultState = {
    registryName: "default",
    list: [],
    search: false,
};
export default function agentReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "agent/list/set":
            return { ...state, list: payload, search: false };
        case "agent/registryName/set":
            return { ...state, registryName: payload };
        case "agent/search/set":
            return { ...state, list: payload, search: true };
        default:
            return state;
    }
}
