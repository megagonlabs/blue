import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
const { NEXT_PUBLIC_MODEL_REGISTRY_NAME } = allEnv();
export const useModelStore = create((set) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    models: [],
    metadata: {},
    setMetadata: ({ key, data }) => {
        set((state) => ({ metadata: { ...state.metadata, [key]: data } }));
    },
    getModels: () => {
        axios
            .get(`registry/${NEXT_PUBLIC_MODEL_REGISTRY_NAME}/models`)
            .then((response) => {
                set({ models: _.get(response, "data.results", []) });
            });
    },
}));
