import _ from "lodash";
export const defaultState = {
    sessions: {},
    isSocketOpen: false,
    platform: "default",
    sessionIds: [],
    groupedSessionIds: [],
    sessionIdFocus: null,
    sessionDetails: {},
    userId: null,
    collapsed: true,
    unreadSessionIds: new Set(),
    pinnedSessionIds: new Set(),
    terminatedInteraction: new Set(),
    expandedMessageStream: new Set(),
    sessionGroupBy: "all",
};
export default function sessionReducer(
    state = defaultState,
    { type, payload }
) {
    let {
        unreadSessionIds,
        sessionIds,
        terminatedInteraction,
        expandedMessageStream,
    } = state;
    let sessions = _.cloneDeep(state.sessions);
    let pinnedSessionIds = _.clone(state.pinnedSessionIds);
    switch (type) {
        case "session/pinnedSessionIds/add": {
            pinnedSessionIds.add(payload);
            return { ...state, pinnedSessionIds };
        }
        case "session/pinnedSessionIds/remove": {
            pinnedSessionIds.delete(payload);
            return { ...state, pinnedSessionIds };
        }
        case "session/expandedMessageStream/add": {
            expandedMessageStream.add(payload);
            return { ...state, expandedMessageStream };
        }
        case "session/sessions/message/add": {
            const messageLabel = _.get(payload, "message.label", null);
            const contentType = _.get(payload, "message.content_type", null);
            const mode = _.get(payload, "mode", "batch");
            if (!_.includes(sessionIds, payload.session_id)) {
                sessionIds.push(payload.session_id);
            }
            if (_.isEqual(mode, "streaming")) {
                let messages = _.get(
                    sessions,
                    [payload.session_id, "messages"],
                    []
                );
                let data = _.get(
                    sessions,
                    [payload.session_id, "streams", payload.stream, "data"],
                    []
                );
                if (_.isEqual(messageLabel, "CONTROL")) {
                    const messageContentsCode = _.get(
                        payload,
                        "message.contents.code",
                        null
                    );
                    if (_.isEqual(messageContentsCode, "BOS")) {
                        messages.push({
                            stream: payload.stream,
                            metadata: payload.metadata,
                            timestamp: payload.timestamp,
                            order: payload.order,
                        });
                        let streams = _.get(
                            sessions,
                            [payload.session_id, "streams"],
                            {}
                        );
                        _.set(streams, payload.stream, {
                            data: [],
                            contentType: null,
                            complete: false,
                        });
                        _.set(sessions, payload.session_id, {
                            messages,
                            streams,
                        });
                    } else if (_.isEqual(messageContentsCode, "EOS")) {
                        if (
                            !_.includes(payload.stream, `USER:${state.userId}`)
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
                    } else if (
                        _.includes(
                            ["CREATE_FORM", "UPDATE_FORM"],
                            messageContentsCode
                        )
                    ) {
                        for (let i = _.size(messages) - 1; i >= 0; i--) {
                            if (_.isEqual(messages[i].stream, payload.stream)) {
                                messages[i].contentType = "JSON_FORM";
                                break;
                            }
                        }
                        data.push({
                            timestamp: payload.timestamp,
                            content: _.get(
                                payload,
                                "message.contents.args",
                                null
                            ),
                            order: payload.order,
                            id: payload.id,
                            dataType: contentType,
                        });
                    } else if (_.isEqual(messageContentsCode, "CLOSE_FORM")) {
                        terminatedInteraction.add(
                            _.get(
                                payload,
                                "message.contents.args.form_id",
                                null
                            )
                        );
                    }
                } else if (_.isEqual(messageLabel, "DATA")) {
                    for (let i = _.size(messages) - 1; i >= 0; i--) {
                        if (_.isEqual(messages[i].stream, payload.stream)) {
                            messages[i].contentType = contentType;
                            break;
                        }
                    }
                    _.set(
                        sessions,
                        [
                            payload.session_id,
                            "streams",
                            payload.stream,
                            "contentType",
                        ],
                        contentType
                    );
                    data.push({
                        timestamp: payload.timestamp,
                        content: _.get(payload, "message.contents", null),
                        order: payload.order,
                        id: payload.id,
                        dataType: contentType,
                    });
                }
                _.set(
                    sessions,
                    [payload.session_id, "messages"],
                    _.sortBy(_.uniqBy(messages, "stream"), [
                        "timestamp",
                        "order",
                    ])
                );
                _.set(
                    sessions,
                    [payload.session_id, "streams", payload.stream, "data"],
                    _.sortBy(_.uniqBy(data, "id"), ["timestamp", "order"])
                );
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
            let nextSessionDetail = { ...state.sessionDetails };
            for (let i = 0; i < _.size(payload); i++) {
                const detail = payload[i];
                if (!_.isNil(detail.id)) {
                    _.set(nextSessionDetail, [detail.id], detail);
                }
            }
            return { ...state, sessionDetails: nextSessionDetail };
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
            return { ...state, sessionIdFocus: payload, unreadSessionIds };
        }
        default:
            return state;
    }
}
