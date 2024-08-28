import axios from "axios";
import _ from "lodash";
export const agentAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "agent/state/set",
            payload,
        });
    },
    fetchAttributes: (payload) => {
        axios
            .get(
                `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${payload}`
            )
            .then((response) => {
                let icon = _.get(response, "data.result.icon", null);
                if (!_.isEmpty(icon) && !_.startsWith(icon, "data:image/")) {
                    icon = _.split(icon, ":");
                }
                dispatch({
                    type: "agent/icon/set",
                    payload: { key: payload, value: icon },
                });
                dispatch({
                    type: "agent/systemAgents/set",
                    payload: {
                        key: payload,
                        value: _.get(
                            response,
                            "data.result.properties.system_agent",
                            false
                        ),
                    },
                });
            });
    },
    setIcon: (payload) => {
        dispatch({ type: "agent/icon/set", payload });
    },
    getList: (payload) => {
        axios
            .get(`/registry/${payload}/agents`)
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
            .get(`/registry/${payload.registryName}/agents/search`, {
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
