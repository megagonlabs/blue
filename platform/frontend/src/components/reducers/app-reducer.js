import _ from "lodash";
export const defaultState = { users: {} };
export default function appReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "app/users/profile/add": {
            if (_.isEmpty(payload)) {
                return { ...state };
            } else {
                return {
                    ...state,
                    users: {
                        ...state.users,
                        [payload.uid]: payload,
                    },
                };
            }
        }
        default:
            return state;
    }
}
