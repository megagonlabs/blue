import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
const { NEXT_PUBLIC_OPERATOR_REGISTRY_NAME } = allEnv();
export const useOperatorStore = create((set) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    operators: [],
    metadata: {},
    setMetadata: ({ key, data }) => {
        set((state) => ({ metadata: { ...state.metadata, [key]: data } }));
    },
    getOperators: () => {
        axios
            .get(`registry/${NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/operators`)
            .then((response) => {
                set({ operators: _.get(response, "data.results", []) });
            });
    },
}));
