import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
const { NEXT_PUBLIC_TOOL_REGISTRY_NAME } = allEnv();
export const useToolStore = create((set, get) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    tools: [],
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
    getTools: () => {
        const { filter } = get();
        if (_.isEmpty(_.get(filter, "keywords", ""))) {
            axios
                .get(`registry/${NEXT_PUBLIC_TOOL_REGISTRY_NAME}/tools`)
                .then((response) => {
                    set({
                        tools: _.get(response, "data.results", []),
                        search: false,
                    });
                });
        } else {
            const approximate = _.isEqual(filter.searchType, "approximate");
            axios
                .get(
                    `registry/${NEXT_PUBLIC_TOOL_REGISTRY_NAME}/tools/search`,
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
                        tools: _.get(response, "data.results", []),
                        search: true,
                    });
                });
        }
    },
}));
