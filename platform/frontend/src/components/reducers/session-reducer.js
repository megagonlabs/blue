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
    let sessions = _.cloneDeep(state.sessions);
    switch (type) {
        case "session/sessions/message/add": {
            const messageLabel = _.get(payload, "message.label", null);
            const mode = _.get(payload, "mode", "batch");
            if (_.isEqual(mode, "streaming")) {
                if (_.isEqual(messageLabel, "BOS")) {
                    if (!_.includes(state.sessionIds, payload.session_id)) {
                        sessionIds.push(payload.session_id);
                    }
                    let messages = _.get(
                        sessions,
                        [payload.session_id, "messages"],
                        []
                    );
                    let streams = _.get(
                        sessions,
                        [payload.session_id, "streams"],
                        {}
                    );
                    messages.push({
                        stream: payload.stream,
                        timestamp: payload.timestamp,
                    });
                    _.set(streams, payload.stream, {
                        data: [],
                        dtype: _.get(payload, "message.dtype", null),
                        complete: false,
                    });
                    _.set(sessions, payload.session_id, {
                        messages: _.sortBy(
                            _.uniqBy(messages, "stream"),
                            "timestamp"
                        ),
                        streams,
                    });
                } else if (_.isEqual(messageLabel, "DATA")) {
                    _.set(
                        sessions,
                        [
                            payload.session_id,
                            "streams",
                            payload.stream,
                            "dtype",
                        ],
                        _.get(payload, "message.dtype", null)
                    );
                    let data = _.get(
                        sessions,
                        [payload.session_id, "streams", payload.stream, "data"],
                        []
                    );
                    data.push({
                        timestamp: payload.timestamp,
                        content: _.get(payload, "message.content", null),
                        order: payload.order,
                        id: payload.id,
                    });
                    _.set(
                        sessions,
                        [payload.session_id, "streams", payload.stream, "data"],
                        _.sortBy(_.uniqBy(data, "id"), ["timestamp", "order"])
                    );
                } else if (_.isEqual(messageLabel, "EOS")) {
                    if (
                        !_.startsWith(
                            payload.stream,
                            `USER:${state.connectionId}`
                        )
                    ) {
                        unreadSessionIds.add(payload.session_id);
                    }
                    _.set(
                        sessions,
                        [
                            payload.session_id,
                            "streams",
                            payload.stream,
                            "complete",
                        ],
                        true
                    );
                }
            }
            return {
                ...state,
                sessions,
                sessionIds,
                unreadSessionIds,
            };
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
