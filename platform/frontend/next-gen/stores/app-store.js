import { create } from "zustand";

export const useAppStore = create((set) => ({
    darkMode: false,
    showOmnibar: false,
    openOmnibar: () => set({ showOmnibar: true }),
    closeOmnibar: () => set({ showOmnibar: false }),
    omnibarItems: [],
}));
