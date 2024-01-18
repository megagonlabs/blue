export const defaultState = {
    registryName: "default",
    list: [],
    search: false,
    loading: true,
    filter: {
        keywords: "",
        hybrid: false,
        approximate: true,
        type: "",
        page: 0,
        page_size: 10,
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
                loading: false,
            };
        case "agent/search/set":
            return { ...state, ...payload, search: true, loading: false };
        case "agent/state/set":
            return { ...state, [payload.key]: payload.value };
        default:
            return state;
    }
}
