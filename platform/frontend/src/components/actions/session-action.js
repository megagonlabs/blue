import axios from "axios";
export const sessionAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "session/state/set",
            payload,
        });
    },
    setSessionDetail: (payload) => {
        dispatch({
            type: "session/sessions/detail/set",
            payload: payload,
        });
    },
    createSession: (payload) => {
        axios.post(`/sessions/session`).then((response) => {
            try {
                const sessionId = _.get(response, "data.result.id");
                dispatch({
                    type: "session/state/set",
                    payload: { key: "openAgentsDialogTrigger", value: true },
                });
                dispatch({
                    type: "session/sessions/add",
                    payload: sessionId,
                });
            } catch (error) {
                console.log(error);
            }
        });
    },
    observeSession: (payload) => {
        dispatch({ type: "session/sessions/add", payload: payload.sessionId });
        payload.socket.send(
            JSON.stringify({
                type: "OBSERVE_SESSION",
                session_id: payload.sessionId,
            })
        );
    },
    addSessionMessage: (payload) =>
        dispatch({ type: "session/sessions/message/add", payload }),
    setSessionIdFocus: (payload) =>
        dispatch({ type: "session/sessionIdFocus/set", payload }),
});
