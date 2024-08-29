import axios from "axios";
import _ from "lodash";
export const appAction = (dispatch) => ({
    getUserProfile: (payload) => {
        dispatch({
            type: "app/pendingRequests/set",
            payload: { key: `getUserProfile ${payload}`, value: true },
        });
        axios.get(`/accounts/profile/${payload}`).then((response) => {
            const user = _.get(response, "data.user", null);
            if (!_.isEmpty(user)) {
                dispatch({ type: "app/users/profile/add", payload: user });
            }
            dispatch({
                type: "app/pendingRequests/set",
                payload: { key: `getUserProfile ${payload}`, value: false },
            });
        });
    },
});
