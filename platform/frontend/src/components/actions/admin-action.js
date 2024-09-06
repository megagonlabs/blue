export const adminAction = (dispatch) => ({
    addSelectedUser: (payload) => {
        dispatch({ type: "admin/selectedUsers/add", payload: payload });
    },
    removeSelectedUser: (payload) => {
        dispatch({ type: "admin/selectedUsers/remove", payload: payload });
    },
    addSelectedAgent: (payload) => {
        dispatch({ type: "admin/selectedAgents/add", payload: payload });
    },
    removeSelectedAgent: (payload) => {
        dispatch({ type: "admin/selectedAgents/remove", payload: payload });
    },
    setUserList: (payload) => {
        dispatch({ type: "admin/users/set", payload: payload });
    },
    setState: (payload) => {
        dispatch({
            type: "admin/state/set",
            payload,
        });
    },
});
