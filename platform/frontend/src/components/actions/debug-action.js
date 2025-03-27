export const debugAction = (dispatch) => ({
    clearMessages: () => dispatch({ type: "debug/messages/clear" }),
    addMessage: (payload) => dispatch({ type: "debug/messages/add", payload }),
});
