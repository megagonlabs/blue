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
    switch (type) {
        case "session/sessions/message/add": {
            const messageType = _.get(payload, "message.type", null);
            const contentType = _.get(payload, "message.content.type", null);
            // non-conversational message; not adding to session messages
            if (
                _.isEqual(messageType, "INTERACTION") &&
                _.isEqual(contentType, "DONE")
            ) {
                const stream = _.get(payload, "stream", null);
                const formId = _.get(payload, "message.content.form_id", null);
                if (!_.isEmpty(stream) && !_.isEmpty(formId)) {
                    terminatedInteraction.add(`${stream},${formId}`);
                }
                return { ...state, terminatedInteraction };
            } else {
                if (
                    !_.startsWith(payload.stream, `USER:${state.connectionId}`)
                ) {
                    unreadSessionIds.add(payload.session_id);
                }
                if (!_.includes(state.sessionIds, payload.session_id)) {
                    sessionIds.push(payload.session_id);
                }
                const nextMessages = [
                    ..._.get(state, `sessions.${payload.session_id}`, []),
                    {
                        message: payload.message,
                        stream: payload.stream,
                        timestamp: payload.timestamp,
                    },
                ];
                return {
                    ...state,
                    sessions: {
                        ...state.sessions,
                        [payload.session_id]: _.sortBy(
                            nextMessages,
                            function (o) {
                                return o.timestamp;
                            }
                        ),
                    },
                    sessionIds,
                    unreadSessionIds,
                };
            }
        }
        case "session/state/set": {
            return { ...state, [payload.key]: payload.value };
        }
        case "session/sessions/detail/set": {
            let nextSessionDetail = { ...state.sessionDetail };
            for (let i = 0; i < _.size(payload); i++) {
                const detail = payload[i];
                _.set(nextSessionDetail, [detail.id], {
                    name: detail.name,
                    description: detail.description,
                });
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
                    [payload]: [],
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
