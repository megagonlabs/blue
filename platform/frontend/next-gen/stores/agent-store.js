import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export const useAgentStore = create((set) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    agents: [],
    metadata: {},
    setMetadata: ({ key, data }) => {
        set((state) => ({ metadata: { ...state.metadata, [key]: data } }));
    },
    getAgents: () => {
        axios
            .get(`registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agents`)
            .then((response) =>
                set({ agents: _.get(response, "data.results", []) })
            );
    },
}));
