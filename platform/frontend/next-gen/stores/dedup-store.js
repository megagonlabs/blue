import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
export const useDedupStore = create((set, get) => ({
    users: {},
    queue: {},
    getUserProfile: (userId) => {
        const key = `getUserProfile ${userId}`;
        if (!get().queue[key]) {
            set((state) => ({ queue: { ...state.queue, [key]: true } }));
            axios
                .get(`/accounts/profile/${userId}`)
                .then((response) => {
                    const user = _.get(response, "data.user", null);
                    if (_.has(user, "uid")) {
                        set((state) => ({
                            users: { ...state.users, [user.uid]: user },
                        }));
                    }
                })
                .finally(() => {
                    set((state) => ({
                        queue: { ...state.queue, [key]: false },
                    }));
                });
        }
    },
}));
