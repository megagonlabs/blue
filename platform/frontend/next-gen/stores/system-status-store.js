import _ from "lodash";
import { create } from "zustand";
export const useSystemStatusStore = create((set, get) => ({
    live: false,
    trackers: [],
    trackerData: {},
    setState: ({ key, value }) => set({ [key]: value }),
    addTracker: (channel) => {
        set((state) => ({
            trackers: _.uniq([...state.trackers, channel]).sort(),
        }));
    },
    setTrackerData: ({ key, data, graphs }) => {
        set((state) => ({
            trackerData: { ...state.trackerData, [key]: { data, graphs } },
        }));
    },
}));
