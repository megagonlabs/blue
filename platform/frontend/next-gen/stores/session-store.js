import { reorderWithEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/util/reorder-with-edge";
import axios from "axios";
import clone from "clone";
import _ from "lodash";

import { create } from "zustand";
export const useSessionStore = create((set, get) => ({
    sessions: {},
    sessionIds: [],
    filter: { group: "owner", keyword: "" },
    jsonforms: {},
    progress: {},
    addNewSession: (session) => {
        const sessionId = _.get(session, "id", null);
        const { sessionIds } = get();
        if ((!_.isNull(sessionId), _.includes(sessionIds, sessionId))) return;
        set((state) => ({
            sessionIds: [sessionId, ...state.sessionIds],
            sessions: {
                ...state.sessions,
                [sessionId]: {
                    messages: [],
                    streams: {},
                    details: session,
                    workspace: [],
                    tags: [],
                },
            },
        }));
    },
    removeSession: (sessionId) => {
        const { sessions, sessionIds } = clone(get());
        _.unset(sessions, sessionId);
        _.pull(sessionIds, sessionId);
        set({ sessions, sessionIds });
    },
    setSessionDetails: ({ sessionId, fields }) => {
        // fields: list of objects
        // elements:  { path, value }
        const { sessions } = clone(get());
        let details = _.get(sessions, [sessionId, "details"], {});
        for (let i = 0; i < _.size(fields); i++) {
            _.set(details, fields[i].path, fields[i].value);
        }
        _.set(sessions, [sessionId, "details"], details);
        set({ sessions });
    },
    createNewSession: (agentGroup = null) => {
        let url = "/sessions/session";
        if (!_.isEmpty(agentGroup)) {
            url += `/${agentGroup}`;
        }
        axios.post(url).then((response) => {});
    },
    getSessions: () => {
        const { filter, addNewSession } = get();
        const my_sessions = _.includes(
            ["owner", "member"],
            _.get(filter, "group")
        );
        axios.get("/sessions", { params: { my_sessions } }).then((response) => {
            const sessions = _.get(response, "data.results", []);
            let responseSessionIds = [];
            for (let i = 0; i < _.size(sessions); i++) {
                const sessionId = _.get(sessions[i], "id", null);
                if (!_.isNull(sessionId)) {
                    responseSessionIds.push(sessionId);
                }
                addNewSession(sessions[i]);
            }
            const { sessions: stateSessions, sessionIds } = clone(get());
            const deletedSessionIds = _.difference(
                sessionIds,
                responseSessionIds
            );
            for (let i = 0; i < _.size(deletedSessionIds); i++) {
                _.unset(stateSessions, deletedSessionIds[i]);
            }
            set({ sessions: stateSessions, sessionIds: responseSessionIds });
        });
    },
    removeWorkspaceMessage: ({ sessionId, index }) => {
        const { sessions } = clone(get());
        let contents = _.get(sessions, [sessionId, "workspace"], []);
        _.pullAt(contents, [index]);
        _.set(sessions, [sessionId, "workspace"], contents);
        set({ sessions });
    },
    clearWorkspace: (sessionId) => {
        const { sessions } = clone(get());
        _.set(sessions, [sessionId, "workspace"], []);
        set({ sessions });
    },
    reorderWorkspace: ({
        sessionId,
        indexOfSource,
        indexOfTarget,
        closestEdgeOfTarget,
    }) => {
        const { sessions } = clone(get());
        let contents = _.get(sessions, [sessionId, "workspace"], []);
        _.set(
            sessions,
            [sessionId, "workspace"],
            reorderWithEdge({
                list: contents,
                startIndex: indexOfSource,
                indexOfTarget,
                closestEdgeOfTarget,
                axis: "vertical",
            })
        );
        set({ sessions });
    },
    addToWorkspace: ({ type, message, sessionId }) => {
        const stream = _.get(message, "stream", null);
        const { sessions } = clone(get());
        let contents = _.get(sessions, [sessionId, "workspace"], []);
        contents.push({ type, message, sessionId });
        _.set(sessions, [sessionId, "workspace"], contents);
        set({ sessions });
    },
    addSessionMessage: (data) => {
        const messageLabel = _.get(data, "message.label", null);
        const contentType = _.get(data, "message.content_type", null);
        const mode = _.get(data, "mode", "batch");
        const {
            session_id: sessionId,
            metadata,
            timestamp,
            order,
            stream,
        } = data;
        const tags = Object.entries(_.get(data, "metadata.tags", {}));
        const { sessions, jsonforms, progress, sessionIds } = clone(get());
        let sessionTags = _.get(sessions, [sessionId, "tags"], []);
        for (let i = 0; i < _.size(tags); i++) {
            const [tag, value] = tags[i];
            if (_.isEqual(tag, "WORKSPACE_ONLY")) continue;
            if (value) {
                sessionTags.push(tag);
            }
        }
        _.set(sessions, [sessionId, "tags"], _.uniq(sessionTags));
        if (!_.includes(sessionIds, sessionId)) {
            sessionIds.push(sessionId);
        }
        if (_.isEqual(mode, "streaming")) {
            let messages = _.get(sessions, [sessionId, "messages"], []);
            let streamData = _.get(
                sessions,
                [sessionId, "streams", stream, "data"],
                []
            );
            const baseData = {
                timestamp,
                order,
                id: data.id,
                dataType: contentType,
            };
            const baseMessage = { stream, metadata, timestamp, order };
            let workspace = _.get(sessions, [sessionId, "workspace"], []);
            let considerWorkspace = false;
            if (_.isEqual(messageLabel, "CONTROL")) {
                const messageContentsCode = _.get(
                    data,
                    "message.contents.code",
                    null
                );
                const messageContentsArgs = _.get(
                    data,
                    "message.contents.args",
                    null
                );
                const formId = _.get(messageContentsArgs, "form_id", null);
                if (
                    _.isEqual(messageContentsCode, "BOS") &&
                    !_.endsWith(stream, "PROGRESS:STREAM")
                ) {
                    considerWorkspace = true;
                    messages.push(baseMessage);
                    let streams = _.get(sessions, [sessionId, "streams"], {});
                    _.set(streams, stream, {
                        data: [],
                        contentType: null,
                        complete: false,
                    });
                    _.set(sessions, [sessionId, "messages"], messages);
                    _.set(sessions, [sessionId, "streams"], streams);
                } else if (_.isEqual(messageContentsCode, "EOS")) {
                    _.set(
                        sessions,
                        [sessionId, "streams", stream, "complete"],
                        true
                    );
                } else if (
                    (_.includes(["CREATE_FORM", "UPDATE_FORM"]),
                    messageContentsCode)
                ) {
                    for (let i = _.size(messages) - 1; i >= 0; i--) {
                        if (_.isEqual(messages[i].stream, stream)) {
                            _.set(messages, [i, "contentType"], "JSON_FORM");
                            break;
                        }
                    }
                    for (let i = _.size(workspace) - 1; i >= 0; i--) {
                        if (_.isEqual(workspace[i].message.stream, stream)) {
                            _.set(workspace, [i, "loading"], false);
                            _.set(
                                workspace,
                                [i, "message", "contentType"],
                                "JSON_FORM"
                            );
                            break;
                        }
                    }
                    streamData.push({ ...baseData, content: { formId } });
                    // create or update forms
                    _.set(jsonforms, [formId, "content"], messageContentsArgs);
                } else if (_.isEqual(messageContentsCode, "CLOSE_FORM")) {
                    _.set(jsonforms, [formId, "closed"], true);
                } else if (_.isEqual(messageContentsCode, "PROGRESS")) {
                    const { progress_id: progressId, value } =
                        messageContentsArgs;
                    let sessionProgress = _.get(progress, sessionId, {});
                    _.set(sessionProgress, progressId, messageContentsArgs);
                    if (_.isEqual(value, 1)) {
                        sessionProgress = _.omit(sessionProgress, progressId);
                    }
                    _.set(progress, sessionId, sessionProgress);
                }
            } else if (_.isEqual(messageLabel, "DATA")) {
                for (let i = _.size(messages) - 1; i >= 0; i--) {
                    if (_.isEqual(messages[i].stream, stream)) {
                        _.set(messages, [i, "contentType"], contentType);
                        break;
                    }
                }
                for (let i = _.size(workspace) - 1; i >= 0; i--) {
                    if (_.isEqual(workspace[i].message.stream, stream)) {
                        _.set(workspace, [i, "loading"], false);
                        _.set(
                            workspace,
                            [i, "message", "contentType"],
                            contentType
                        );
                        break;
                    }
                }
                _.set(
                    sessions,
                    [sessionId, "streams", stream, "contentType"],
                    contentType
                );
                streamData.push({
                    ...baseData,
                    content: _.get(data, "message.contents", null),
                });
            }
            _.set(
                sessions,
                [sessionId, "messages"],
                _.sortBy(_.unionBy(messages, "stream"), ["timestamp", "order"])
            );
            _.set(
                sessions,
                [sessionId, "streams", stream, "data"],
                _.sortBy(_.uniqBy(streamData, "id"), ["timestamp", "order"])
            );
            if (
                considerWorkspace &&
                (_.get(data, "metadata.tags.WORKSPACE", false) ||
                    _.get(data, "metadata.tags.WORKSPACE_ONLY", false))
            ) {
                workspace.push({
                    type: "session",
                    message: baseMessage,
                    loading: true,
                });
            }
            _.set(sessions, [sessionId, "workspace"], workspace);
        }
        set({ sessions, jsonforms, progress, sessionIds });
    },
}));
