import axios from "axios";
import { create } from "zustand";
export const useUIVisibilityStore = create((set, get) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    UIVisibility: {},
    queue: {},
    setVisibility: ({ id, value }) => {
        set((state) => ({ queue: { ...state.queue, [id]: true } }));
        axios
            .put(`/accounts/profile/ui_visibility/${id}`, { value })
            .then(() => {
                const { UIVisibility, setState } = get();
                let newVisibility = _.cloneDeep(UIVisibility);
                _.set(newVisibility, id, value);
                setState({ key: "UIVisibility", value: newVisibility });
                set((state) => ({ queue: { ...state.queue, [id]: false } }));
            });
    },
}));
