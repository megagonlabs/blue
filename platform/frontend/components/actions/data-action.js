import axios from "axios";
import _ from "lodash";
export const dataAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "agent/state/set",
            payload: payload,
        });
    },
    getList: () => {
        axios.get("/data").then((response) => {
            dispatch({
                type: "data/list/set",
                payload: _.get(response, "data.results", []),
            });
        });
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
            .get(`/data/${payload.registryName}/search`, {
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
