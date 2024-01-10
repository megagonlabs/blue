export const defaultState = {
    registryName: "default",
    list: [],
    search: false,
    filter: {
        keywords: "",
        hybrid: false,
        approximate: true,
        type: "source",
    },
};
export default function dataReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "data/list/set":
            return {
                ...state,
                list: payload,
                filter: defaultState.filter,
                search: false,
            };
        case "data/search/set":
            return { ...state, ...payload, search: true };
        default:
            return state;
    }
}
