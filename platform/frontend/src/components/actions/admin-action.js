export const adminAction = (dispatch) => ({
    addSelectedUser: (payload) =>
        dispatch({ type: "admin/selectedUsers/add", payload }),
    removeSelectedUser: (payload) =>
        dispatch({ type: "admin/selectedUsers/remove", payload }),
    addSelectedAgent: (payload) =>
        dispatch({ type: "admin/selectedAgents/add", payload }),
    removeSelectedAgent: (payload) =>
        dispatch({ type: "admin/selectedAgents/remove", payload }),
    addSelectedService: (payload) =>
        dispatch({ type: "admin/selectedServices/add", payload }),
    removeSelectedService: (payload) =>
        dispatch({ type: "admin/selectedServices/remove", payload }),
    setUserList: (payload) => dispatch({ type: "admin/users/set", payload }),
    setAgentList: (payload) => dispatch({ type: "admin/agents/set", payload }),
    setServiceList: (payload) =>
        dispatch({ type: "admin/services/set", payload }),
    setState: (payload) => dispatch({ type: "admin/state/set", payload }),
});
