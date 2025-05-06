import clone from "clone";
import _ from "lodash";
import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";
export const useGridStore = create((set, get) => ({
    layout: [],
    containers: {},
    setLayout: (layout) => {
        set(() => ({ layout }));
    },
    removeContainer: (key) => {
        set((state) => ({
            containers: _.omit(state.containers, [key]),
            layout: state.layout.filter(
                (element) => !_.isEqual(element.i, key)
            ),
        }));
    },
    resizeContainerWidth: ({ id, width = 12 }) => {
        const { layout } = clone(get());
        for (let i = 0; i < _.size(layout); i++) {
            if (_.isEqual(_.get(layout, [i, "i"]), id)) {
                _.set(layout, [i, "w"], width);
                break;
            }
        }
        set({ layout });
    },
    addContainer: ({ title, content, icon }) => {
        const key = uuidv4();
        set((state) => ({
            containers: {
                ...state.containers,
                [key]: { title, content, icon },
            },
            layout: [
                { i: key, x: 0, y: 0, w: 12, h: 3, minW: 4, minH: 3 },
                ...state.layout,
            ],
        }));
    },
}));
