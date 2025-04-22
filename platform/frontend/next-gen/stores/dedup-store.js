import axios from "axios";
import { differenceInMinutes } from "date-fns";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
import { useAgentStore } from "./agent-store";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export const useDedupStore = create((set, get) => ({
    users: {},
    queue: {},
    cachedTime: {},
    getAgentMetadata: (agent) => {
        const key = `getAgentMetadata ${agent}`;
        const { queue, cachedTime } = get();
        const diff = differenceInMinutes(Date.now(), cachedTime[key]);
        if (!queue[key] && (diff > 5 || _.isNaN(diff))) {
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
                        cachedTime: { ...state.cachedTime, [key]: Date.now() },
                    }));
                });
        }
    },
    getUserProfile: (userId) => {
        const key = `getUserProfile ${userId}`;
        const { queue, cachedTime } = get();
        const diff = differenceInMinutes(Date.now(), cachedTime[key]);
        if (!queue[key] && (diff > 5 || _.isNaN(diff))) {
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
                        cachedTime: { ...state.cachedTime, [key]: Date.now() },
                    }));
                });
        }
    },
}));
