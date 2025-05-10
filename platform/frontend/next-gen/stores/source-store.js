import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
export const useSourceStore = create((set) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    sources: [],
    metadata: {},
    setMetadata: ({ key, data }) => {
        set((state) => ({ metadata: { ...state.metadata, [key]: data } }));
    },
    getSources: () => {
        axios
            .get(`registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/data`)
            .then((response) => {
                set({ sources: _.get(response, "data.results", []) });
            });
    },
}));
