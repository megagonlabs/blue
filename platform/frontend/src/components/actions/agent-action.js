import axios from "axios";
import _ from "lodash";
export const agentAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "agent/state/set",
            payload,
        });
    },
    getList: () => {
        axios
            .get("/agents")
            .then((response) => {
                dispatch({
                    type: "agent/list/set",
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
            .get(`/agents/${payload.registryName}/search`, {
                params: filter,
            })
            .then((response) => {
                dispatch({
                    type: "agent/search/set",
                    payload: {
                        list: _.get(response, "data.results", []),
                        filter: filter,
                    },
                });
            });
    },
});
