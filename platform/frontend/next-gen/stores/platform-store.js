import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
export const usePlatformStore = create((set, get) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    users: { list: [], order: {}, loading: false, selected: new Set() },
    configurations: { values: {}, loading: false },
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
    updateConfigurationValues: ({ key, value }) => {
        const { configurations } = get();
        let newValues = _.clone(configurations.values);
        _.set(newValues, key, value);
        set((state) => ({
            configurations: { ...state.configurations, values: newValues },
        }));
    },
    getConfigurations: () => {
        set((state) => ({
            configurations: { ...state.configurations, loading: true },
        }));
        axios
            .get("/platform/settings")
            .then((response) => {
                set((state) => ({
                    configurations: {
                        ...state.configurations,
                        values: _.get(response, "data.settings", {}),
                    },
                }));
            })
            .finally(() => {
                set((state) => ({
                    configurations: { ...state.configurations, loading: false },
                }));
            });
    },
    getUsers: () => {
        set((state) => ({ users: { ...state.users, loading: true } }));
        axios.get("/accounts/users").then((response) => {
            set((state) => ({
                users: {
                    ...state.users,
                    loading: false,
                    selected: new Set(),
                    list: _.get(response, "data.users", []),
                },
            }));
        });
    },
}));
