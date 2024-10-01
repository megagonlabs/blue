import _ from "lodash";
export const defaultState = {
    selectedUsers: new Set(),
    selectedAgents: new Set(),
    selectedServices: new Set(),
    users: [],
    usersMap: {},
};
export default function adminReducer(state = defaultState, { type, payload }) {
    let { selectedUsers, selectedAgents, selectedServices } = state;
    switch (type) {
        case "admin/selectedUsers/add": {
            selectedUsers.add(payload);
            return { ...state, selectedUsers };
        }
        case "admin/selectedUsers/remove": {
            selectedUsers.delete(payload);
            return { ...state, selectedUsers };
        }
        case "admin/selectedServices/add": {
            selectedServices.add(payload);
            return { ...state, selectedServices };
        }
        case "admin/selectedServices/remove": {
            selectedServices.delete(payload);
            return { ...state, selectedServices };
        }
        case "admin/selectedAgents/add": {
            selectedAgents.add(payload);
            return { ...state, selectedAgents };
        }
        case "admin/selectedAgents/remove": {
            selectedAgents.delete(payload);
            return { ...state, selectedAgents };
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
