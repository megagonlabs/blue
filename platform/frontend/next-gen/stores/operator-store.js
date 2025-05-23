import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
const { NEXT_PUBLIC_OPERATOR_REGISTRY_NAME } = allEnv();
export const useOperatorStore = create((set, get) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    operators: [],
    metadata: {},
    setMetadata: ({ key, data }) => {
        set((state) => ({ metadata: { ...state.metadata, [key]: data } }));
    },
    search: false,
    filter: {
        keywords: "",
        type: "",
        page: 0,
        pageSize: 10,
        searchType: "approximate",
    },
    setFilterValue: ({ key, value }) => {
        set((state) => ({ filter: { ...state.filter, [key]: value } }));
    },
    getOperators: () => {
        const { filter } = get();
        if (_.isEmpty(_.get(filter, "keywords", ""))) {
            axios
                .get(`registry/${NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/operators`)
                .then((response) => {
                    set({
                        operators: _.get(response, "data.results", []),
                        search: false,
                    });
                });
        } else {
            const approximate = _.isEqual(filter.searchType, "approximate");
            axios
                .get(
                    `registry/${NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/operators/search`,
                    {
                        params: {
                            keywords: filter.keywords,
                            type: filter.type,
                            page: filter.page,
                            page_size: filter.pageSize,
                            approximate,
                            hybrid: !approximate,
                        },
                    }
                )
                .then((response) => {
                    set({
                        operators: _.get(response, "data.results", []),
                        search: true,
                    });
                });
        }
    },
}));
