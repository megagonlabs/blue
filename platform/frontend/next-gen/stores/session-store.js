import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
export const useSessionStore = create((set, get) => ({
    sessions: {},
    sessionIds: [],
    filter: { group: "owner", keyword: "" },
    pinnedSessionIds: new Set(),
    addNewSession: (session) => {
        const sessionId = _.get(session, "id", null);
        const { sessionIds } = get();
        if (_.includes(sessionIds, sessionId)) return;
        set((state) => ({
            sessionIds: [sessionId, ...state.sessionIds],
            sessions: {
                ...state.sessions,
                [sessionId]: { messages: [], streams: {}, details: session },
            },
        }));
    },
    createNewSession: (agentGroup = null) => {
        let url = "/sessions/session";
        if (!_.isEmpty(agentGroup)) url += `/${agentGroup}`;
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
            for (let i = 0; i < _.size(sessions); i++) {
                addNewSession(sessions[i]);
            }
        });
    },
}));
