import axios from "axios";
import _ from "lodash";
export const agentAction = (dispatch) => ({
    getList: () => {
        axios.get("/agents").then((response) => {
            dispatch({
                type: "agent/list/set",
                payload: _.get(response, "data", []),
            });
        });
    },
    getAgent: () => {},
    setRegistryName: (payload) => {
        dispatch({
            type: "agent/registryName/set",
            payload: payload,
        });
    },
});
