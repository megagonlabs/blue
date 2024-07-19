export const adminAction = (dispatch) => ({
    addSelectedUser: (payload) => {
        dispatch({ type: "admin/selectedUsers/add", payload: payload });
    },
    removeSelectedUser: (payload) => {
        dispatch({ type: "admin/selectedUsers/remove", payload: payload });
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
