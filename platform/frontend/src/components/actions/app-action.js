import axios from "axios";
import _ from "lodash";
export const appAction = (dispatch) => ({
    getUserProfileByEmail: (payload) => {
        axios.get(`/accounts/profile/email/${payload}`).then((response) => {
            const user = _.get(response, "data.user", null);
            if (!_.isEmpty(user)) {
                dispatch({ type: "app/users/profile/add", payload: user });
            }
        });
    },
    getUserProfileByUid: (payload) => {
        axios.get(`/accounts/profile/uid/${payload}`).then((response) => {
            const user = _.get(response, "data.user", null);
            if (!_.isEmpty(user)) {
                dispatch({ type: "app/users/profile/add", payload: user });
            }
        });
    },
});
