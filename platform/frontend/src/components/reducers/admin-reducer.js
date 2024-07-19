import _ from "lodash";
export const defaultState = {
    selectedUsers: new Set(),
    users: [],
    usersMap: {},
};
export default function adminReducer(state = defaultState, { type, payload }) {
    let selectedUsers = state.selectedUsers;
    switch (type) {
        case "admin/selectedUsers/add": {
            return {
                ...state,
                selectedUsers: selectedUsers.add(payload),
            };
        }
        case "admin/users/set": {
            let usersMap = {};
            for (let i = 0; i < _.size(payload); i++) {
                let user = payload[i];
                _.set(usersMap, user.uid, user);
            }
            return {
                ...state,
                users: payload,
                usersMap: usersMap,
            };
        }
        case "admin/selectedUsers/remove": {
            selectedUsers.delete(payload);
            return {
                ...state,
                selectedUsers,
            };
        }
        case "admin/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        default:
            return state;
    }
}
