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
    setContainerHeader: ({ id, title, icon }) => {
        set((state) => ({
            containers: {
                ...state.containers,
                [id]: { ..._.get(state.containers, id, {}), title, icon },
            },
        }));
    },
    removeContainer: (id) => {
        set((state) => ({
            containers: _.omit(state.containers, [id]),
            layout: state.layout.filter((element) => !_.isEqual(element.i, id)),
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
        const id = uuidv4();
        set((state) => ({
            containers: {
                ...state.containers,
                [id]: { title, content, icon },
            },
            layout: [
                { i: id, x: 0, y: 0, w: 12, h: 3, minW: 4, minH: 3 },
                ...state.layout,
            ],
        }));
    },
}));
