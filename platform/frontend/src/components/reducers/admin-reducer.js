import _ from "lodash";
export const defaultState = {
    selectedUsers: new Set(),
    selectedAgents: new Set(),
    users: [],
    usersMap: {},
};
export default function adminReducer(state = defaultState, { type, payload }) {
    let selectedUsers = state.selectedUsers;
    let selectedAgents = state.selectedAgents;
    switch (type) {
        case "admin/selectedUsers/add": {
            return {
                ...state,
                selectedUsers: selectedUsers.add(payload),
            };
        }
        case "admin/selectedUsers/remove": {
            selectedUsers.delete(payload);
            return {
                ...state,
                selectedUsers,
            };
        }
        case "admin/selectedAgents/add": {
            return {
                ...state,
                selectedAgents: selectedAgents.add(payload),
            };
        }
        case "admin/selectedAgents/remove": {
            selectedAgents.delete(payload);
            return {
                ...state,
                selectedAgents,
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
        case "admin/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        default:
            return state;
    }
}
