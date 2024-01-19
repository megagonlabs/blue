import axios from "axios";
export const sessionAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "session/state/set",
            payload,
        });
    },
    createSession: (payload) => {
        axios.post(`/sessions/${payload}/session`).then((response) => {
            try {
                const sessionId = _.get(response, "data.result.id");
                payload.connection.send(
                    JSON.stringify({
                        type: "OBSERVE_SESSION",
                        session_id: sessionId,
                    })
                );
                dispatch({ type: "session/sessions/add", payload: sessionId });
            } catch (error) {
                console.log(error);
            }
        });
    },
    addSessionMessage: (payload) =>
        dispatch({ type: "session/sessions/message/add", payload }),
    setSessionIdFocus: (payload) =>
        dispatch({ type: "session/sessionIdFocus/set", payload }),
});
