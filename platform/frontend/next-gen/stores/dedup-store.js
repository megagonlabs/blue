import axios from "axios";
import { differenceInMinutes } from "date-fns";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
import { useAgentStore } from "./agent-store";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
const CACHE_DURATION_MINUTES = 1;
export const useDedupStore = create((set, get) => ({
    users: {},
    queue: {},
    cachedTime: {},
    getAgentMetadata: (agent) => {
        const key = `getAgentMetadata ${agent}`;
        const { queue, cachedTime } = get();
        const diff = differenceInMinutes(Date.now(), cachedTime[key]);
        if (!queue[key] && (diff > CACHE_DURATION_MINUTES || _.isNaN(diff))) {
            set((state) => ({ queue: { ...state.queue, [key]: true } }));
            axios
                .get(
                    `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${agent}`
                )
                .then((response) => {
                    let icon = _.get(response, "data.result.icon", null);
                    let displayName = _.get(
                        response,
                        "data.result.properties.display_name",
                        null
                    );
                    const { setMetadata } = useAgentStore.getState();
                    setMetadata({ key: agent, data: { icon, displayName } });
                })
                .finally(() => {
                    set((state) => ({
                        queue: { ...state.queue, [key]: false },
                        cachedTime: { ...state.cachedTime, [key]: Date.now() },
                    }));
                });
        }
    },
    addUserProfile: (user) => {
        if (_.has(user, "uid")) {
            set((state) => ({
                users: { ...state.users, [user.uid]: user },
            }));
        }
    },
    getUserProfile: (userId) => {
        const key = `getUserProfile ${userId}`;
        const { queue, cachedTime, addUserProfile } = get();
        const diff = differenceInMinutes(Date.now(), cachedTime[key]);
        if (
            !queue[key] &&
            (diff > CACHE_DURATION_MINUTES || _.isNaN(diff)) &&
            _.isString(userId)
        ) {
            set((state) => ({ queue: { ...state.queue, [key]: true } }));
            axios
                .get(`/accounts/profile/${userId}`)
                .then((response) => {
                    const user = _.get(response, "data.user", null);
                    addUserProfile(user);
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
