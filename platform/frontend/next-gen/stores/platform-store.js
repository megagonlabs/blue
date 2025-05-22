import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
export const usePlatformStore = create((set, get) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    users: { list: [], order: {}, loading: false, selected: new Set() },
    configurations: {
        values: {},
        loading: false,
        emailsLoading: false,
        selectedEmails: new Set(),
    },
    setUserTableOrder: (order) => {
        set((state) => ({ users: { ...state.users, order } }));
    },
    updateUserTableSelected: ({ uid, checked = false }) => {
        const { users } = get();
        let newSelected = _.cloneDeep(users.selected);
        if (checked) {
            newSelected.add(uid);
        } else {
            newSelected.delete(uid);
        }
        set((state) => ({ users: { ...state.users, selected: newSelected } }));
    },
    updateEmailTableSelected: ({ email, checked = false }) => {
        const { configurations } = get();
        let newSelected = _.cloneDeep(configurations.selectedEmails);
        if (checked) {
            newSelected.add(email);
        } else {
            newSelected.delete(email);
        }
        set((state) => ({
            configurations: {
                ...state.configurations,
                selectedEmails: newSelected,
            },
        }));
    },
    addAllowedEmail: (email) => {
        const { configurations } = get();
        let newValues = _.cloneDeep(configurations.values);
        _.set(newValues, ["allowed_emails", email], { email, allow: true });
        set((state) => ({
            configurations: { ...state.configurations, values: newValues },
        }));
    },
    removeAllowedEmail: (email) => {
        const { configurations } = get();
        let newValues = _.cloneDeep(configurations.values);
        _.unset(newValues, ["allowed_emails", email]);
        set((state) => ({
            configurations: { ...state.configurations, values: newValues },
        }));
    },
    updateUserTableRole: ({ uids, role }) => {
        const { users } = get();
        let newList = _.cloneDeep(users.list);
        for (let i = 0; i < _.size(newList); i++) {
            if (_.isSet(uids) && uids.has(newList[i].uid)) {
                _.set(newList[i], "role", role);
            }
        }
        set((state) => ({ users: { ...state.users, list: newList } }));
    },
    updateConfigurationValues: ({ key, value }) => {
        const { configurations } = get();
        let newValues = _.cloneDeep(configurations.values);
        _.set(newValues, key, value);
        set((state) => ({
            configurations: { ...state.configurations, values: newValues },
        }));
    },
    getConfigurations: () => {
        set((state) => ({
            configurations: { ...state.configurations, loading: true },
        }));
        axios.get("/platform/settings").then((response) => {
            set((state) => ({
                configurations: {
                    ...state.configurations,
                    values: _.get(response, "data.settings", {}),
                    loading: false,
                    selectedEmails: new Set(),
                },
            }));
        });
    },
    getAllowedEmails: () => {
        set((state) => ({
            configurations: { ...state.configurations, emailsLoading: true },
        }));
        axios.get("/platform/settings").then((response) => {
            const allowed_emails = _.get(
                response,
                "data.settings.allowed_emails",
                {}
            );
            set((state) => ({
                configurations: {
                    ...state.configurations,
                    values: { ...state.configurations.values, allowed_emails },
                    emailsLoading: false,
                    selectedEmails: new Set(),
                },
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
