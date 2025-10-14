import SessionContainer from "@/components/sessions/SessionContainer";
import SessionDisplayName from "@/components/sessions/SessionDisplayName";
import { reorderWithEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/util/reorder-with-edge";
import { faComments } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
import { useGridStore } from "./grid-layout-store";
export const useSessionStore = create((set, get) => ({
    sessions: {},
    sessionIds: [],
    filter: { group: "owner", keywords: "" },
    forms: {},
    progress: {},
    inspection: {},
    expandedMessages: {},
    messageFilterTags: {},
    triggers: {},
    removeSessionProgress: (sessionId, progressId) => {
        const { progress } = get();
        let newProgress = _.cloneDeep(progress);
        let next = _.get(newProgress, sessionId, {});
        next = _.omit(next, progressId);
        _.set(newProgress, sessionId, next);
        set({ progress: newProgress });
    },
    toggleMessageFilterTag: (sessionId, tag) => {
        const { messageFilterTags } = get();
        let next = _.cloneDeep(messageFilterTags);
        let current = _.get(messageFilterTags, sessionId, []);
        if (!_.includes(current, tag)) {
            current.push(tag);
        } else {
            current = _.pull(current, tag);
        }
        _.set(next, sessionId, current);
        set({ messageFilterTags: next });
    },
    clearMessageFilterTags: (sessionId) => {
        set((state) => ({
            messageFilterTags: {
                ...state.clearMessageFilterTags,
                [sessionId]: [],
            },
        }));
    },
    resetTrigger: (path) => {
        const { triggers } = get();
        let next = _.cloneDeep(triggers);
        _.set(next, path, false);
        set({ triggers: next });
    },
    expandMessage: (sessionId, stream) => {
        const { expandedMessages } = get();
        let next = _.cloneDeep(expandedMessages);
        _.set(next, [sessionId, stream], true);
        set({ expandedMessages: next });
    },
    setFilterValue: ({ key, value }) => {
        set((state) => ({ filter: { ...state.filter, [key]: value } }));
    },
    setInspectionFocusStream: (sessionId, focusStream) => {
        set((state) => ({
            inspection: {
                ...state.inspection,
                [sessionId]: {
                    ..._.get(state.inspection, sessionId, {}),
                    focusStream,
                },
            },
        }));
    },
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
        const { sessions, sessionIds } = get();
        let newSessions = _.cloneDeep(sessions),
            newSessionIds = _.cloneDeep(sessionIds);
        _.unset(newSessions, sessionId);
        _.pull(newSessionIds, sessionId);
        set({ sessions: newSessions, sessionIds: newSessionIds });
    },
    setSessionDetails: ({ sessionId, fields }) => {
        // fields: list of objects
        // elements:  { path, value }
        const { sessions } = get();
        let newSessions = _.cloneDeep(sessions);
        let details = _.get(newSessions, [sessionId, "details"], {});
        for (let i = 0; i < _.size(fields); i++) {
            _.set(details, fields[i].path, fields[i].value);
        }
        _.set(newSessions, [sessionId, "details"], details);
        set({ sessions: newSessions });
    },
    createNewSession: ({
        agentGroup = null,
        replace = false,
        gridContainerId = null,
    }) => {
        let url = "/sessions/session";
        if (!_.isEmpty(agentGroup)) {
            url += `/${agentGroup}`;
        }
        axios.post(url).then((response) => {
            const sessionId = _.get(response, "data.result.id", null);
            if (!_.isNull(sessionId)) {
                const { addContainer, replaceContainer } =
                    useGridStore.getState();
                if (replace && !_.isEmpty(gridContainerId)) {
                    replaceContainer({
                        id: gridContainerId,
                        title: <SessionDisplayName sessionId={sessionId} />,
                        content: <SessionContainer sessionId={sessionId} />,
                        icon: faComments,
                    });
                } else {
                    addContainer({
                        icon: faComments,
                        title: <SessionDisplayName sessionId={sessionId} />,
                        content: <SessionContainer sessionId={sessionId} />,
                    });
                }
                const { triggers } = get();
                let next = _.cloneDeep(triggers);
                _.set(
                    next,
                    ["addSessionAgent", sessionId],
                    _.isEmpty(agentGroup)
                );
                set({ triggers: next });
            }
        });
    },
    getSessions: () => {
        const { filter, addNewSession } = get();
        const my_sessions = _.includes(
            ["owner", "member"],
            _.get(filter, "group")
        );
        axios.get("/sessions", { params: { my_sessions } }).then((response) => {
            const results = _.get(response, "data.results", []);
            let responseSessionIds = [];
            for (let i = 0; i < _.size(results); i++) {
                const sessionId = _.get(results[i], "id", null);
                if (!_.isNull(sessionId)) {
                    responseSessionIds.push(sessionId);
                }
                addNewSession(results[i]);
            }
            const { sessions, sessionIds } = get();
            let stateSessions = _.cloneDeep(sessions);
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
        const { sessions } = get();
        let newSessions = _.cloneDeep(sessions);
        let contents = _.get(newSessions, [sessionId, "workspace"], []);
        _.pullAt(contents, [index]);
        _.set(newSessions, [sessionId, "workspace"], contents);
        set({ sessions: newSessions });
    },
    clearWorkspace: (sessionId) => {
        const { sessions } = get();
        let newSessions = _.cloneDeep(sessions);
        _.set(newSessions, [sessionId, "workspace"], []);
        set({ sessions: newSessions });
    },
    reorderWorkspace: ({
        sessionId,
        indexOfSource,
        indexOfTarget,
        closestEdgeOfTarget,
    }) => {
        const { sessions } = get();
        let newSessions = _.cloneDeep(sessions);
        let contents = _.get(newSessions, [sessionId, "workspace"], []);
        _.set(
            newSessions,
            [sessionId, "workspace"],
            reorderWithEdge({
                list: contents,
                startIndex: indexOfSource,
                indexOfTarget,
                closestEdgeOfTarget,
                axis: "vertical",
            })
        );
        set({ sessions: newSessions });
    },
    addToWorkspace: ({ type, message, sessionId }) => {
        const { sessions } = get();
        let newSessions = _.cloneDeep(sessions);
        let contents = _.get(newSessions, [sessionId, "workspace"], []);
        contents.push({ type, message, sessionId });
        _.set(newSessions, [sessionId, "workspace"], contents);
        set({ sessions: newSessions });
    },
    setFormData: (formId, data, newTimestamp) => {
        const { forms } = get();
        const currentForm = _.get(forms, formId);
        const currentTimestamp = _.get(currentForm, "content.timestamp", 0);
        if (newTimestamp > currentTimestamp) {
            let newForms = _.cloneDeep(forms);
            _.set(newForms, [formId, "content", "data"], data);
            _.set(newForms, [formId, "content", "timestamp"], newTimestamp);
            set({ forms: newForms });
        }
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
        const tags = _.entries(_.get(data, "metadata.tags", {}));
        const { sessions, forms, progress, sessionIds } = get();
        let newSessions = _.cloneDeep(sessions),
            newForms = _.cloneDeep(forms),
            newProgress = _.cloneDeep(progress),
            newSessionIds = _.cloneDeep(sessionIds);
        let sessionTags = _.get(newSessions, [sessionId, "tags"], []);
        for (let i = 0; i < _.size(tags); i++) {
            const [tag, value] = tags[i];
            if (_.isEqual(tag, "WORKSPACE_ONLY")) continue;
            if (value) {
                sessionTags.push(tag);
            }
        }
        _.set(newSessions, [sessionId, "tags"], _.uniq(sessionTags));
        if (!_.includes(newSessionIds, sessionId)) {
            newSessionIds.push(sessionId);
        }
        if (_.isEqual(mode, "streaming")) {
            let messages = _.get(newSessions, [sessionId, "messages"], []);
            let streamData = _.get(
                newSessions,
                [sessionId, "streams", stream, "data"],
                []
            );
            const baseData = {
                timestamp,
                order,
                id: data.id,
                dataType: contentType,
                label: messageLabel,
            };
            const baseMessage = { stream, metadata, timestamp, order };
            let workspace = _.get(newSessions, [sessionId, "workspace"], []);
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
                    _.isEqual(messageContentsCode, "BOS")
                    // && !_.endsWith(stream, "PROGRESS:STREAM")
                ) {
                    considerWorkspace = true;
                    messages.push(baseMessage);
                    let streams = _.get(
                        newSessions,
                        [sessionId, "streams"],
                        {}
                    );
                    _.set(streams, stream, {
                        data: [],
                        contentType: null,
                        complete: false,
                    });
                    _.set(newSessions, [sessionId, "messages"], messages);
                    _.set(newSessions, [sessionId, "streams"], streams);
                } else if (_.isEqual(messageContentsCode, "EOS")) {
                    _.set(
                        newSessions,
                        [sessionId, "streams", stream, "complete"],
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
                    streamData.push({
                        ...baseData,
                        content: { form_id: formId },
                    });
                    // create or update forms
                    _.set(newForms, [formId, "content"], messageContentsArgs);
                } else if (_.isEqual(messageContentsCode, "CLOSE_FORM")) {
                    _.set(newForms, [formId, "closed"], true);
                } else if (_.isEqual(messageContentsCode, "PROGRESS")) {
                    const { progress_id: progressId, value } =
                        messageContentsArgs;
                    let sessionProgress = _.get(newProgress, sessionId, {});
                    _.set(sessionProgress, progressId, messageContentsArgs);
                    if (_.isEqual(value, 1)) {
                        sessionProgress = _.omit(sessionProgress, progressId);
                    }
                    _.set(newProgress, sessionId, sessionProgress);
                    for (let i = _.size(messages) - 1; i >= 0; i--) {
                        if (_.isEqual(messages[i].stream, stream)) {
                            _.set(messages, [i, "contentType"], "PROGRESS");
                            break;
                        }
                    }
                    streamData.push({
                        ...baseData,
                        content: messageContentsArgs,
                    });
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
                    newSessions,
                    [sessionId, "streams", stream, "contentType"],
                    contentType
                );
                streamData.push({
                    ...baseData,
                    content: _.get(data, "message.contents", null),
                });
            }
            _.set(
                newSessions,
                [sessionId, "messages"],
                _.sortBy(_.unionBy(messages, "stream"), ["timestamp", "order"])
            );
            _.set(
                newSessions,
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
            _.set(newSessions, [sessionId, "workspace"], workspace);
        }
        set({
            sessions: newSessions,
            forms: newForms,
            progress: newProgress,
            sessionIds: newSessionIds,
        });
    },
}));
