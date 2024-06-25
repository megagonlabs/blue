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
            if (!_.includes(sessionIds, payload.session_id)) {
                sessionIds.push(payload.session_id);
            }
            if (_.isEqual(mode, "streaming")) {
                const contentType = _.get(
                    payload,
                    "message.content.type",
                    null
                );
                let messages = _.get(
                    sessions,
                    [payload.session_id, "messages"],
                    []
                );
                if (_.isEqual(messageLabel, "BOS")) {
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
                } else if (_.includes(["DATA", "INTERACTION"], messageLabel)) {
                    let addToData = true;
                    if (_.isEqual(messageLabel, "INTERACTION")) {
                        for (let i = _.size(messages) - 1; i >= 0; i--) {
                            if (
                                !_.isEqual(messages[i].stream, payload.stream)
                            ) {
                                continue;
                            }
                            messages[i].label = "INTERACTION";
                        }
                        _.set(
                            sessions,
                            [payload.session_id, "messages"],
                            messages
                        );
                        // non-conversational message; not adding to session messages
                        if (_.isEqual(contentType, "DONE")) {
                            addToData = false;
                            const stream = _.get(payload, "stream", null);
                            const formId = _.get(
                                payload,
                                "message.content.form_id",
                                null
                            );
                            if (!_.isEmpty(stream) && !_.isEmpty(formId)) {
                                terminatedInteraction.add(
                                    `${stream},${formId}`
                                );
                            }
                        } else {
                            if (
                                !_.startsWith(
                                    payload.stream,
                                    `USER:${state.connectionId}`
                                )
                            ) {
                                unreadSessionIds.add(payload.session_id);
                            }
                        }
                    }
                    if (addToData) {
                        const dtype = _.get(payload, "message.dtype", null);
                        _.set(
                            sessions,
                            [
                                payload.session_id,
                                "streams",
                                payload.stream,
                                "dtype",
                            ],
                            dtype
                        );
                        let data = _.get(
                            sessions,
                            [
                                payload.session_id,
                                "streams",
                                payload.stream,
                                "data",
                            ],
                            []
                        );
                        data.push({
                            timestamp: payload.timestamp,
                            content: _.get(payload, "message.content", null),
                            order: payload.order,
                            id: payload.id,
                            dtype: dtype,
                        });
                        _.set(
                            sessions,
                            [
                                payload.session_id,
                                "streams",
                                payload.stream,
                                "data",
                            ],
                            _.sortBy(_.uniqBy(data, "id"), [
                                "timestamp",
                                "order",
                            ])
                        );
                    }
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
                    const dtype = _.get(
                        sessions,
                        [
                            payload.session_id,
                            "streams",
                            payload.stream,
                            "dtype",
                        ],
                        null
                    );
                    for (let i = _.size(messages) - 1; i >= 0; i--) {
                        if (
                            !_.isEqual(messages[i].stream, payload.stream) ||
                            _.isEqual(messages[i].label, "INTERACTION")
                        ) {
                            continue;
                        }
                        if (_.isEqual(dtype, "str")) {
                            messages[i].label = "TEXT";
                        }
                        if (_.isEqual(dtype, "json")) {
                            messages[i].label = "JSON";
                        }
                    }
                    _.set(sessions, [payload.session_id, "messages"], messages);
                }
            }
            return {
                ...state,
                sessions,
                sessionIds,
                unreadSessionIds,
                terminatedInteraction,
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
                    [payload]: { messages: [], streams: {} },
                },
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
