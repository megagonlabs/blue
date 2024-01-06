export const defaultState = {
    registryName: "default",
    list: [],
};
export default function agentReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "agent/list/set":
            return { ...state, list: payload };
        case "agent/registryName/set":
            return { ...state, registryName: payload };
        default:
            return state;
    }
}
