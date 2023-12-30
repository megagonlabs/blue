import _ from "lodash";
export const defaultState = {
    sessions: {},
    sessionIds: [],
    sessionIdFocus: null,
    unreadSessionIds: new Set(),
};
export default function sessionReducer(
    state = defaultState,
    { type, payload }
) {
    let unreadSessionIds = state.unreadSessionIds;
    switch (type) {
        case "session/sessions/message/add":
            unreadSessionIds.add(payload.session_id);
            return {
                ...state,
                sessions: {
                    ...state.sessions,
                    [payload.session_id]: [
                        ..._.get(state, `sessions.${payload.session_id}`, []),
                        payload.content,
                    ],
                },
                sessionIds: [
                    payload.session_id,
                    ...state.sessionIds.filter(
                        (id) => !_.isEqual(id, payload.session_id)
                    ),
                ],
                unreadSessionIds: unreadSessionIds,
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
