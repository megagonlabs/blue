import _ from "lodash";
export const defaultState = {
    sessions: {},
    connection: null,
    platform: "default",
    sessionIds: [],
    sessionIdFocus: null,
    unreadSessionIds: new Set(),
};
export default function sessionReducer(
    state = defaultState,
    { type, payload }
) {
    let unreadSessionIds = state.unreadSessionIds;
    let sessionIds = state.sessionIds;
    switch (type) {
        case "session/sessions/message/add":
            unreadSessionIds.add(payload.session_id);
            if (!_.includes(state.sessionIds, payload.session_id)) {
                sessionIds.push(payload.session_id);
            }
            return {
                ...state,
                sessions: {
                    ...state.sessions,
                    [payload.session_id]: [
                        ..._.get(state, `sessions.${payload.session_id}`, []),
                        payload.message,
                    ],
                },
                sessionIds: sessionIds,
                unreadSessionIds: unreadSessionIds,
            };
        case "session/connection/set":
            return {
                ...state,
                connection: payload,
            };
        case "session/sessions/add":
            return {
                ...state,
                sessions: {
                    ...state.sessions,
                    [payload]: [],
                },
                sessionIds: [payload, ...state.sessionIds],
            };
        case "session/sessionIdFocus/set":
            unreadSessionIds.delete(payload);
            return {
                ...state,
                sessionIdFocus: payload,
                unreadSessionIds: unreadSessionIds,
            };
        default:
            return state;
    }
}
