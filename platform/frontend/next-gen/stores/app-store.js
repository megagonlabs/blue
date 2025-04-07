import { create } from "zustand";
export const useAppStore = create((set) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    darkMode: false,
    showOmnibar: false,
    openOmnibar: () => set({ showOmnibar: true }),
    closeOmnibar: () => set({ showOmnibar: false }),
    omnibarItems: [],
}));
