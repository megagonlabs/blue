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
    sessionAgentProgress: {},
    // search parameters
    filter: { keywords: "" },
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
        sessionAgentProgress,
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
            let collapseState = _.get(
                sessionWorkspaceCollapse,
                payload.stream,
                true
            );
            return {
                ...state,
                sessionWorkspaceCollapse: {
                    ...sessionWorkspaceCollapse,
                    [payload.stream]: _.has(payload, "value")
                        ? payload.value
                        : !collapseState,
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
            const { session_id, metadata, timestamp, order, stream } = payload;
            if (!_.includes(sessionIds, session_id)) {
                sessionIds.push(session_id);
            }
            if (_.isEqual(mode, "streaming")) {
                let messages = _.get(sessions, [session_id, "messages"], []);
                let data = _.get(
                    sessions,
                    [session_id, "streams", stream, "data"],
                    []
                );
                const baseData = {
                    timestamp,
                    order,
                    id: payload.id,
                    dataType: contentType,
                };
                const baseMessage = { stream, metadata, timestamp, order };
                let workspaceContents = _.get(
                    sessionWorkspace,
                    sessionIdFocus,
                    []
                );
                let considerWorkspace = false;
                if (_.isEqual(messageLabel, "CONTROL")) {
                    const messageContentsCode = _.get(
                        payload,
                        "message.contents.code",
                        null
                    );
                    const messageContentsArgs = _.get(
                        payload,
                        "message.contents.args",
                        null
                    );
                    if (
                        _.isEqual(messageContentsCode, "BOS") &&
                        !_.endsWith(stream, "PROGRESS:STREAM")
                    ) {
                        considerWorkspace = true;
                        messages.push(baseMessage);
                        let streams = _.get(
                            sessions,
                            [session_id, "streams"],
                            {}
                        );
                        _.set(streams, stream, {
                            data: [],
                            contentType: null,
                            complete: false,
                        });
                        _.set(sessions, session_id, { messages, streams });
                    } else if (_.isEqual(messageContentsCode, "EOS")) {
                        if (!_.includes(stream, `USER:${state.userId}`)) {
                            unreadSessionIds.add(session_id);
                        }
                        _.set(
                            sessions,
                            [session_id, "streams", stream, "complete"],
                            true
                        );
                    } else if (
                        _.includes(
                            ["CREATE_FORM", "UPDATE_FORM"],
                            messageContentsCode
                        )
                    ) {
                        for (let i = _.size(messages) - 1; i >= 0; i--) {
                            if (_.isEqual(messages[i].stream, stream)) {
                                messages[i].contentType = "JSON_FORM";
                                break;
                            }
                        }
                        for (
                            let i = _.size(workspaceContents) - 1;
                            i >= 0;
                            i--
                        ) {
                            if (
                                _.isEqual(workspaceContents[i].stream, stream)
                            ) {
                                workspaceContents[i].loading = false;
                                workspaceContents[i].contentType = "JSON_FORM";
                                break;
                            }
                        }
                        data.push({
                            ...baseData,
                            content: messageContentsArgs,
                        });
                    } else if (_.isEqual(messageContentsCode, "CLOSE_FORM")) {
                        terminatedInteraction.add(
                            _.get(
                                payload,
                                "message.contents.args.form_id",
                                null
                            )
                        );
                    } else if (_.isEqual(messageContentsCode, "PROGRESS")) {
                        const { progress_id, value } = messageContentsArgs;
                        let progress = _.get(
                            sessionAgentProgress,
                            session_id,
                            {}
                        );
                        _.set(progress, progress_id, messageContentsArgs);
                        if (_.isEqual(value, 1)) {
                            progress = _.omit(progress, progress_id);
                        }
                        _.set(sessionAgentProgress, session_id, progress);
                    }
                } else if (_.isEqual(messageLabel, "DATA")) {
                    for (let i = _.size(messages) - 1; i >= 0; i--) {
                        if (_.isEqual(messages[i].stream, stream)) {
                            messages[i].contentType = contentType;
                            break;
                        }
                    }
                    for (let i = _.size(workspaceContents) - 1; i >= 0; i--) {
                        if (_.isEqual(workspaceContents[i].stream, stream)) {
                            workspaceContents[i].loading = false;
                            workspaceContents[i].contentType = contentType;
                            break;
                        }
                    }
                    _.set(
                        sessions,
                        [session_id, "streams", stream, "contentType"],
                        contentType
                    );
                    data.push({
                        ...baseData,
                        content: _.get(payload, "message.contents", null),
                    });
                }
                _.set(
                    sessions,
                    [session_id, "messages"],
                    _.sortBy(_.uniqBy(messages, "stream"), [
                        "timestamp",
                        "order",
                    ])
                );
                _.set(
                    sessions,
                    [session_id, "streams", stream, "data"],
                    _.sortBy(_.uniqBy(data, "id"), ["timestamp", "order"])
                );
                const addToWorkspace = _.get(
                    payload,
                    "metadata.tags.WORKSPACE",
                    false
                );
                if (considerWorkspace && addToWorkspace) {
                    workspaceContents.push({
                        type: "session",
                        message: { ...baseMessage, loading: true },
                    });
                }
                _.set(sessionWorkspace, sessionIdFocus, workspaceContents);
            }
            return {
                ...state,
                sessions,
                sessionIds,
                unreadSessionIds,
                terminatedInteraction,
                sessionAgentProgress,
                sessionWorkspace,
            };
        }
        case "session/sessions/progress/remove": {
            let progress = _.get(sessionAgentProgress, sessionIdFocus, {});
            progress = _.omit(progress, payload);
            _.set(sessionAgentProgress, sessionIdFocus, progress);
            return { ...state, sessionAgentProgress };
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
                sessionIds: [payload, ...sessionIds],
            };
        }
        case "session/sessions/remove": {
            return { ...state, sessionIds: _.without(sessionIds, payload) };
        }
        case "session/sessionIdFocus/set": {
            unreadSessionIds.delete(payload);
            return { ...state, sessionIdFocus: payload, unreadSessionIds };
        }
        default:
            return state;
    }
}
