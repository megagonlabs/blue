import axios from "axios";
import _ from "lodash";
import { sendSocketMessage } from "../helper";
export const sessionAction = (dispatch) => ({
    setState: (payload) => {
        dispatch({
            type: "session/state/set",
            payload,
        });
    },
    setSessionDetails: (payload) => {
        dispatch({
            type: "session/sessions/detail/set",
            payload,
        });
    },
    setSessionDetailMembers: (payload) => {
        dispatch({
            type: "session/sessions/detail/members/set",
            payload,
        });
    },
    expandMessageStream: (payload) => {
        dispatch({ type: "session/expandedMessageStream/add", payload });
    },
    addPinnedSessionId: (payload) => {
        dispatch({ type: "session/pinnedSessionIds/add", payload });
    },
    removePinnedSessionId: (payload) => {
        dispatch({ type: "session/pinnedSessionIds/remove", payload });
    },
    clearCurrentWorkspace: () => {
        dispatch({ type: "session/workspace/clear" });
    },
    removeWorkspaceContent: (payload) => {
        dispatch({ type: "session/workspace/remove", payload });
    },
    toggleWorkspaceCollapse: (payload) => {
        dispatch({ type: "session/toggleWorkspaceCollapse/toggle", payload });
    },
    createSession: ({ socket, groupName = null }) => {
        let postSessionUrl = `/sessions/session${
            _.isEmpty(groupName) ? "" : "/" + groupName
        }`;
        dispatch({
            type: "session/state/set",
            payload: {
                key: "creatingSession",
                value: true,
            },
        });
        axios.post(postSessionUrl).then((response) => {
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
                socket.send(
                    JSON.stringify({
                        type: "OBSERVE_SESSION",
                        session_id: session.id,
                    })
                );
                dispatch({
                    type: "session/sessionIdFocus/set",
                    payload: session.id,
                });
                dispatch({
                    type: "session/state/set",
                    payload: {
                        key: "openAgentsDialogTrigger",
                        value: _.isEmpty(groupName),
                    },
                });
                if (!_.isEmpty(groupName)) {
                    dispatch({
                        type: "session/state/set",
                        payload: {
                            key: "joinAgentGroupSession",
                            value: true,
                        },
                    });
                }
            } catch (error) {
                console.log(error);
            } finally {
                dispatch({
                    type: "session/state/set",
                    payload: {
                        key: "creatingSession",
                        value: false,
                    },
                });
            }
        });
    },
    addSession: (payload) => {
        dispatch({ type: "session/sessions/add", payload });
    },
    addToWorkspace: (payload) => {
        dispatch({ type: "session/sessions/addToWorkspace", payload });
    },
    observeSession: (payload) => {
        dispatch({ type: "session/sessions/add", payload: payload.sessionId });
        sendSocketMessage(
            payload.socket,
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
