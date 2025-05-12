import { hasIntersection } from "@/components/helper";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { GoogleAuthProvider, getAuth, signInWithPopup } from "firebase/auth";
import _ from "lodash";
import { create } from "zustand";
import { useAppStore } from "./app-store";
import { useSocketStore } from "./socket-store";
const firebaseConfig = {
    apiKey: "AIzaSyAkVp-dj3o1yf89mL3wMUtEidUHjzqyWCQ",
    authDomain: "blue-9d597.firebaseapp.com",
    projectId: "blue-9d597",
    storageBucket: "blue-9d597.appspot.com",
    messagingSenderId: "851224572522",
    appId: "1:851224572522:web:b8b3f5b50e30333773d013",
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
export const useAuthStore = create((set, get) => ({
    user: null,
    permissions: {},
    initialized: false,
    isPopupOpen: false,
    signInWithGoogle: () => {
        set({ isPopupOpen: true });
        signInWithPopup(auth, provider).then((result) =>
            result.user.getIdToken().then((idToken) =>
                axios
                    .post("/accounts/sign-in", { id_token: idToken })
                    .then(() => {
                        const { fetchAccountProfile } = get();
                        fetchAccountProfile();
                    })
                    .finally(() => {
                        set({ isPopupOpen: false });
                    })
            )
        );
    },
    logout: () => {
        axios.post("/accounts/sign-out").then(() => {
            set({ user: null });
            const { socket } = useSocketStore.getState();
            if (!_.isNull(socket)) {
                // close existing ws connection
                if (!_.isEqual(WebSocket.CLOSED, socket.readyState)) {
                    socket.close();
                }
            }
        });
    },
    clearUser: () => {
        set({ user: null });
    },
    fetchAccountProfile: () => {
        axios
            .get("/accounts/profile")
            .then((response) => {
                const user = _.get(response, "data.profile", null);
                const permissions = {
                    canWriteAgentRegistry: hasIntersection(
                        _.get(user, "permissions.agent_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canWriteDataRegistry: hasIntersection(
                        _.get(user, "permissions.data_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canWriteOperatorRegistry: hasIntersection(
                        _.get(user, "permissions.operator_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canWriteModelRegistry: hasIntersection(
                        _.get(user, "permissions.model_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canWritePlatformAgents: hasIntersection(
                        _.get(user, "permissions.platform_agents", []),
                        ["write_all", "write_own"]
                    ),
                };
                const { setState } = useAppStore.getState();
                const KEYS = ["dark_mode", "show_workspace", "expand_message"];
                for (let i = 0; i < _.size(KEYS); i++) {
                    setState({
                        key: KEYS[i],
                        value: _.get(user, ["settings", KEYS[i]], false),
                    });
                }
                set({ user, permissions });
            })
            .catch((error) => {})
            .finally(() => {
                set({ initialized: true });
            });
    },
}));
