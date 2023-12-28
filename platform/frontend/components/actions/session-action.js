export const sessionAction = (dispatch) => ({
    addSessionMessage: (payload) =>
        dispatch({ type: "session/sessions/message/add", payload: payload }),
    setSessionIdFocus: (payload) =>
        dispatch({ type: "session/sessionIdFocus/set", payload: payload }),
});
