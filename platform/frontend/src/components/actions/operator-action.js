import axios from "axios";
export const operatorAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "operator/state/set",
            payload,
        });
    },
    getList: (payload) => {
        axios
            .get(`/registry/${payload}/operators`)
            .then((response) => {
                dispatch({
                    type: "operator/list/set",
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
            .get(`/registry/${payload.registryName}/operators/search`, {
                params: filter,
            })
            .then((response) => {
                dispatch({
                    type: "operator/search/set",
                    payload: {
                        list: _.get(response, "data.results", []),
                        filter: filter,
                    },
                });
            });
    },
});
