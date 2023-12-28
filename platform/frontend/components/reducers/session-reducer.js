import _ from "lodash";
export const defaultState = {
    sessions: {},
    sessionIds: [],
    sessionIdFocus: null,
};
export default function sessionReducer(
    state = defaultState,
    { type, payload }
) {
    switch (type) {
        case "session/sessions/message/add":
            return {
                ...state,
                sessions: {
                    ...state.sessions,
                    [payload.session_id]: [
                        ..._.get(state, ["session", payload.session_id], []),
                        payload.content,
                    ],
                },
                sessionIds: [
                    payload.session_id,
                    ...state.sessionIds.filter(
                        (id) => !_.isEqual(id, payload.session_id)
                    ),
                ],
            };
        case "session/sessionIdFocus/set":
            return {
                ...state,
                sessionIdFocus: payload,
            };
        default:
            return state;
    }
}
