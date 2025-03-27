import _ from "lodash";
export const defaultState = { data: {}, list: [] };
export default function trackerReducer(
    state = defaultState,
    { type, payload }
) {
    let { list } = state;
    switch (type) {
        case "tracker/data/add": {
            const { key, data, graph } = payload;
            return {
                ...state,
                data: { ...state.data, [key]: { data, graph } },
            };
        }
        case "tracker/add": {
            return {
                ...state,
                list: _.uniq([...list, payload]).sort(),
            };
        }
        default:
            return state;
    }
}
