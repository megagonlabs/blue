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
            payload,
        });
    },
    expandMessageStream: (payload) => {
        dispatch({ type: "session/expandedMessageStream/add", payload });
    },
    createSession: (payload) => {
        axios.post(`/sessions/session`).then((response) => {
            try {
                const session = _.get(response, "data.result", {});
                dispatch({
                    type: "session/sessions/detail/set",
                    payload: [session],
                });
                dispatch({
                    type: "session/sessions/add",
                    payload: session.id,
                });
                payload.send(
                    JSON.stringify({
                        type: "OBSERVE_SESSION",
                        session_id: session.id,
                    })
                );
                dispatch({
                    type: "session/sessionIdFocus/set",
                    payload: session.id,
                }),
                    dispatch({
                        type: "session/state/set",
                        payload: {
                            key: "openAgentsDialogTrigger",
                            value: true,
                        },
                    });
            } catch (error) {
                console.log(error);
            }
        });
    },
    addSession: (payload) => {
        dispatch({ type: "session/sessions/add", payload });
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
    addSessionMessage: (payload) => {
        dispatch({ type: "session/sessions/message/add", payload });
    },
    setSessionIdFocus: (payload) => {
        dispatch({ type: "session/sessionIdFocus/set", payload });
    },
});
