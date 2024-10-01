import axios from "axios";
import _ from "lodash";
export const appAction = (dispatch) => ({
    getUserProfile: (payload) => {
        if (_.isEmpty(payload)) return;
        const requestKey = `getUserProfile ${payload}`;
        dispatch({
            type: "app/pendingRequests/set",
            payload: { key: requestKey, value: true },
        });
        axios.get(`/accounts/profile/${payload}`).then((response) => {
            const user = _.get(response, "data.user", null);
            if (!_.isEmpty(user)) {
                dispatch({ type: "app/users/profile/add", payload: user });
            }
            dispatch({
                type: "app/pendingRequests/set",
                payload: { key: requestKey, value: false },
            });
        });
    },
});
