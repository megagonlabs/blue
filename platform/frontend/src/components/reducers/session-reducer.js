import { reorderWithEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/util/reorder-with-edge";
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
    sessionListPanelCollapsed: true,
    showWorkspacePanel: false,
    sessionWorkspaceCollapse: {},
    sessionWorkspace: {},
    unreadSessionIds: new Set(),
    pinnedSessionIds: new Set(),
    terminatedInteraction: new Set(),
    expandedMessageStream: new Set(),
    sessionGroupBy: "all",
    creatingSession: false,
    joinAgentGroupSession: false,
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
        sessionWorkspace,
        sessionWorkspaceCollapse,
    } = state;
    const { sessionIdFocus } = state;
    let sessions = _.cloneDeep(state.sessions);
    let pinnedSessionIds = _.clone(state.pinnedSessionIds);
    switch (type) {
        case "session/workspace/clear": {
            return {
                ...state,
                sessionWorkspace: { ...sessionWorkspace, [sessionIdFocus]: [] },
            };
        }
        case "session/workspace/remove": {
            let contents = _.get(sessionWorkspace, sessionIdFocus, []);
            _.pullAt(contents, [payload]);
            return {
                ...state,
                sessionWorkspace: {
                    ...sessionWorkspace,
                    [sessionIdFocus]: contents,
                },
            };
        }
        case "session/sessions/addToWorkspace": {
            let workspaceContents = _.get(sessionWorkspace, sessionIdFocus, []);
            workspaceContents.push(payload);
            _.set(sessionWorkspace, sessionIdFocus, workspaceContents);
            return { ...state, sessionWorkspace };
        }
        case "session/workspaceCollapse/all": {
            let workspaceContent = _.get(sessionWorkspace, sessionIdFocus, []);
            for (let i = 0; i < _.size(workspaceContent); i++) {
                _.set(
                    sessionWorkspaceCollapse,
                    _.get(workspaceContent, [i, "message", "stream"], null),
                    true
                );
            }
            return { ...state, sessionWorkspaceCollapse };
        }
        case "session/workspace/reorder": {
            const { indexOfSource, indexOfTarget, closestEdgeOfTarget } =
                payload;
            return {
                ...state,
                sessionWorkspace: {
                    ...sessionWorkspace,
                    [sessionIdFocus]: reorderWithEdge({
                        list: _.get(sessionWorkspace, sessionIdFocus, []),
                        startIndex: indexOfSource,
                        indexOfTarget,
                        closestEdgeOfTarget,
                        axis: "vertical",
                    }),
                },
            };
        }
        case "session/workspaceCollapse/toggle": {
            let collapseState = _.get(sessionWorkspaceCollapse, payload, false);
            return {
                ...state,
                sessionWorkspaceCollapse: {
                    ...sessionWorkspaceCollapse,
                    [payload]: !collapseState,
                },
            };
        }
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
        case "session/sessions/detail/members/set": {
            let nextSessionDetail = { ...state.sessionDetails };
            const { id, members } = payload;
            _.set(nextSessionDetail, [id, "members"], members);
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
