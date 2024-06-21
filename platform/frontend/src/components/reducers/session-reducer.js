import _ from "lodash";
export const defaultState = {
    sessions: {},
    isSocketOpen: false,
    platform: "default",
    sessionIds: [],
    sessionIdFocus: null,
    sessionDetail: {},
    connectionId: null,
    unreadSessionIds: new Set(),
    terminatedInteraction: new Set(),
};
export default function sessionReducer(
    state = defaultState,
    { type, payload }
) {
    let unreadSessionIds = state.unreadSessionIds;
    let sessionIds = state.sessionIds;
    let terminatedInteraction = state.terminatedInteraction;
    let sessions = state.sessions;
    switch (type) {
        case "session/sessions/message/add": {
            const messageLabel = _.get(payload, "message.label", null);
            const mode = _.get(payload, "mode", "batch");
            if (_.isEqual(mode, "streaming")) {
                if (_.isEqual(messageLabel, "BOS")) {
                    if (!_.includes(state.sessionIds, payload.session_id)) {
                        sessionIds.push(payload.session_id);
                    }
                    console.log(sessions);
                    if (_.has(sessions, payload.session_id)) {
                    } else {
                        _.set(sessions, payload.session_id, {
                            messages: [
                                {
                                    stream: payload.stream,
                                    timestamp: payload.timestamp,
                                },
                            ],
                            streams: {
                                [payload.stream]: {
                                    data: [],
                                    dtype: _.get(
                                        payload,
                                        "message.dtype",
                                        null
                                    ),
                                    complete: false,
                                },
                            },
                        });
                    }
                    return {
                        ...state,
                        sessions,
                        sessionIds,
                    };
                } else if (_.isEqual(messageLabel, "DATA")) {
                } else if (_.isEqual(messageLabel, "EOS")) {
                    if (
                        !_.startsWith(
                            payload.stream,
                            `USER:${state.connectionId}`
                        )
                    ) {
                        unreadSessionIds.add(payload.session_id);
                    }
                    return {
                        ...state,
                        unreadSessionIds,
                    };
                }
            }
            return { ...state };
        }
        case "session/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        case "session/sessions/detail/set": {
            let nextSessionDetail = { ...state.sessionDetail };
            for (let i = 0; i < _.size(payload); i++) {
                const detail = payload[i];
                if (!_.isNil(detail.id)) {
                    _.set(nextSessionDetail, [detail.id], detail);
                }
            }
            return { ...state, sessionDetail: nextSessionDetail };
        }
        case "session/sessions/add": {
            if (_.includes(sessionIds, payload)) {
                return { ...state };
            }
            return {
                ...state,
                sessions: {
                    ...state.sessions,
                    [payload]: {
                        messages: [],
                        streams: {},
                    },
                },
                sessionIdFocus: payload,
                sessionIds: [payload, ...state.sessionIds],
            };
        }
        case "session/sessionIdFocus/set": {
            unreadSessionIds.delete(payload);
            return {
                ...state,
                sessionIdFocus: payload,
                unreadSessionIds: unreadSessionIds,
            };
        }
        default:
            return state;
    }
}
