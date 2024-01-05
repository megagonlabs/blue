import axios from "axios";
import _ from "lodash";
export const agentAction = (dispatch) => ({
    getAgents: () => {
        axios.get("/agents").then((response) => {
            dispatch({
                type: "agent/list/set",
                payload: _.get(response, "data", []),
            });
        });
    },
});
