import { allEnv } from "next-runtime-env";
const { NEXT_PUBLIC_MODEL_REGISTRY_NAME } = allEnv();
export const defaultState = {
    registryName: NEXT_PUBLIC_MODEL_REGISTRY_NAME,
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
export default function modelReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "model/list/set": {
            return {
                ...state,
                list: payload,
                filter: defaultState.filter,
                search: false,
                loading: false,
            };
        }
        case "model/search/set": {
            return { ...state, ...payload, search: true, loading: false };
        }
        case "model/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        default:
            return state;
    }
}
