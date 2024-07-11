export const defaultState = { users: {} };
export default function appReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "app/users/profile/add": {
            return {
                ...state,
                users: {
                    ...state.users,
                    [payload.id]: payload,
                    [payload.uid]: payload,
                },
            };
        }
        default:
            return state;
    }
}
