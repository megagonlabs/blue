import _ from "lodash";
import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";

export const useGridStore = create((set) => ({
    layout: [],
    containers: {},
    setLayout: (layout) => set(() => ({ layout })),
    removeContainer: (key) => {
        set((state) => ({
            containers: _.omit(state.containers, [key]),
            layout: state.layout.filter(
                (element) => !_.isEqual(element.i, key)
            ),
        }));
    },
    addContainer: (title, content) => {
        const key = uuidv4();
        set((state) => ({
            containers: { ...state.containers, [key]: { title, content } },
            layout: [
                { i: key, x: 0, y: 0, w: 12, h: 2, minW: 4, minH: 2 },
                ...state.layout,
            ],
        }));
    },
}));
