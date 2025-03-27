import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export const agentAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "agent/state/set",
            payload,
        });
    },
    fetchAttributes: (payload) => {
        if (_.isEmpty(payload)) return;
        const requestKey = `fetchAttributes ${payload}`;
        dispatch({
            type: "agent/pendingAttributesRequests/set",
            payload: { key: requestKey, value: true },
        });
        axios
            .get(
                `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${payload}`
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
                dispatch({
                    type: "agent/propertyLookups/set",
                    payload: {
                        agent: payload,
                        key: "display_name",
                        value: _.get(
                            response,
                            "data.result.properties.display_name",
                            null
                        ),
                    },
                });
                dispatch({
                    type: "agent/pendingAttributesRequests/set",
                    payload: { key: requestKey, value: false },
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
    updateAgentGroupSelection: (payload) => {
        dispatch({ type: "agent/agent_group/selection/set", payload });
    },
    clearAgentGroupSelection: (payload) => {
        dispatch({ type: "agent/agent_group/selection/clear", payload });
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
