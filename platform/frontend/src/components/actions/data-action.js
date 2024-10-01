import axios from "axios";
import _ from "lodash";
export const dataAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "data/state/set",
            payload,
        });
    },
    getList: (payload) => {
        axios
            .get(`/registry/${payload}/data`)
            .then((response) => {
                dispatch({
                    type: "data/list/set",
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
            .get(`/registry/${payload.registryName}/data/search`, {
                params: filter,
            })
            .then((response) => {
                dispatch({
                    type: "data/search/set",
                    payload: {
                        list: _.get(response, "data.results", []),
                        filter: filter,
                    },
                });
            });
    },
});
