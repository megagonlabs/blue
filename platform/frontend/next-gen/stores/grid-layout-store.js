import _ from "lodash";
import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";
export const useGridStore = create((set, get) => ({
    layout: [],
    layoutData: [],
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
    replaceContainer: ({ id, title, content, icon }) => {
        set((state) => ({
            containers: {
                ...state.containers,
                [id]: {
                    ..._.get(state.containers, id, {}),
                    title,
                    content,
                    icon,
                },
            },
        }));
    },
    removeContainer: (id) => {
        set((state) => ({
            containers: _.omit(state.containers, [id]),
            layout: state.layout.filter((element) => !_.isEqual(element.i, id)),
            layoutData: state.layoutData.filter(
                (element) => !_.isEqual(element.id, id)
            ),
        }));
    },
    resizeContainerFullHeight: ({ id, grid }) => {
        const { layout } = _.cloneDeep(get());
        try {
            const gridHeight = _.get(grid, "current.clientHeight", null);
            const calculatedHeight = _.floor((gridHeight - 40 + 20) / 170);
            if (_.isInteger(calculatedHeight)) {
                for (let i = 0; i < _.size(layout); i++) {
                    if (_.isEqual(_.get(layout, [i, "i"]), id)) {
                        _.set(layout, [i, "h"], calculatedHeight);
                        break;
                    }
                }
            }
        } catch (error) {}
        set({ layout });
    },
    resizeContainerWidth: ({ id, width = 12 }) => {
        const { layout } = _.cloneDeep(get());
        for (let i = 0; i < _.size(layout); i++) {
            if (_.isEqual(_.get(layout, [i, "i"]), id)) {
                _.set(layout, [i, "w"], width);
                break;
            }
        }
        set({ layout });
    },
    addContainer: ({ title, content, icon, uniqueId = null }) => {
        const id = uuidv4();
        const { layoutData } = get();
        let exist = false;
        for (let i = 0; i < _.size(layoutData); i++) {
            if (
                !_.isNull(uniqueId) &&
                _.isEqual(uniqueId, layoutData[i].uniqueId)
            ) {
                exist = true;
            }
        }
        if (!exist) {
            set((state) => ({
                containers: {
                    ...state.containers,
                    [id]: { title, content, icon },
                },
                layout: [
                    { i: id, x: 0, y: 0, w: 12, h: 3, minW: 4, minH: 3 },
                    ...state.layout,
                ],
                layoutData: [...state.layoutData, { id, uniqueId }],
            }));
        }
    },
}));
