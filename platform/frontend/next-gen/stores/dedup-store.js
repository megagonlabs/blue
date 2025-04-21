import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
import { useAgentStore } from "./agent-store";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export const useDedupStore = create((set, get) => ({
    users: {},
    queue: {},
    getAgentMetadata: (agent) => {
        const key = `getAgentMetadata ${agent}`;
        if (!get().queue[key]) {
            set((state) => ({ queue: { ...state.queue, [key]: true } }));
            axios
                .get(
                    `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${agent}`
                )
                .then((response) => {
                    let icon = _.get(response, "data.result.icon", null);
                    const { setMetadata } = useAgentStore.getState();
                    setMetadata(agent, { icon });
                })
                .finally(() => {
                    set((state) => ({
                        queue: { ...state.queue, [key]: false },
                    }));
                });
        }
    },
    getUserProfile: (userId) => {
        const key = `getUserProfile ${userId}`;
        if (!get().queue[key]) {
            set((state) => ({ queue: { ...state.queue, [key]: true } }));
            axios
                .get(`/accounts/profile/${userId}`)
                .then((response) => {
                    const user = _.get(response, "data.user", null);
                    if (_.has(user, "uid")) {
                        set((state) => ({
                            users: { ...state.users, [user.uid]: user },
                        }));
                    }
                })
                .finally(() => {
                    set((state) => ({
                        queue: { ...state.queue, [key]: false },
                    }));
                });
        }
    },
}));
