import axios from "axios";
import _ from "lodash";
export const dataAction = (dispatch) => ({
    getList: () => {
        axios.get("/data").then((response) => {
            dispatch({
                type: "data/list/set",
                payload: _.get(response, "data.results", []),
            });
        });
    },
    setRegistryName: (payload) => {
        dispatch({
            type: "data/registryName/set",
            payload: payload,
        });
    },
});
