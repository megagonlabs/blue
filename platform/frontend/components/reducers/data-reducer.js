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
export default function dataReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "data/list/set": {
            return {
                ...state,
                list: payload,
                filter: defaultState.filter,
                search: false,
                loading: false,
            };
        }
        case "data/search/set": {
            return { ...state, ...payload, search: true, loading: false };
        }
        case "data/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        default:
            return state;
    }
}
