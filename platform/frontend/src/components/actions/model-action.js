import axios from "axios";
export const modelAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "model/state/set",
            payload,
        });
    },
    getList: (payload) => {
        axios
            .get(`/registry/${payload}/models`)
            .then((response) => {
                dispatch({
                    type: "model/list/set",
                    payload: _.get(response, "data.results", []),
                });
            })
            .catch(() => {});
    },
    searchList: (payload) => {
        const filter = {
            keywords: payload.keywords,
            approximate: payload.approximate,
            hybrid: payload.hybrid,
            type: payload.type,
            page: payload.page,
            page_size: payload.pageSize,
        };
        axios
            .get(`/registry/${payload.registryName}/models/search`, {
                params: filter,
            })
            .then((response) => {
                dispatch({
                    type: "model/search/set",
                    payload: {
                        list: _.get(response, "data.results", []),
                        filter: filter,
                    },
                });
            });
    },
});
