export const defaultState = {
    registryName: "default",
    list: [],
};
export default function dataReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "data/list/set":
            return { ...state, list: payload };
        case "data/registryName/set":
            return { ...state, registryName: payload };
        default:
            return state;
    }
}
