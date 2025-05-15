import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
export const usePlatformStore = create((set, get) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    users: { list: [], order: {}, loading: false, selected: new Set() },
    setUserTableOrder: (order) => {
        set((state) => ({ users: { ...state.users, order } }));
    },
    updateUserTableSelected: ({ uid, checked = false }) => {
        const { users } = get();
        let newSelected = _.clone(users.selected);
        if (checked) {
            newSelected.add(uid);
        } else {
            newSelected.delete(uid);
        }
        set((state) => ({ users: { ...state.users, selected: newSelected } }));
    },
    updateUserTableRole: ({ uids, role }) => {
        const { users } = get();
        let newList = _.clone(users.list);
        for (let i = 0; i < _.size(newList); i++) {
            if (_.isSet(uids) && uids.has(newList[i].uid)) {
                _.set(newList[i], "role", role);
            }
        }
        set((state) => ({ users: { ...state.users, list: newList } }));
    },
    getUsers: () => {
        set((state) => ({ users: { ...state.users, loading: true } }));
        axios.get("/accounts/users").then((response) => {
            set((state) => ({
                users: {
                    ...state.users,
                    loading: false,
                    list: _.get(response, "data.users", []),
                },
            }));
        });
    },
}));
