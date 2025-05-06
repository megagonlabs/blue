import axios from "axios";
import { initializeApp } from "firebase/app";
import { GoogleAuthProvider, getAuth, signInWithPopup } from "firebase/auth";
import _ from "lodash";
import { create } from "zustand";
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
                set({ user: _.get(response, "data.profile", null) });
            })
            .catch((error) => {})
            .finally(() => {
                set({ initialized: true });
            });
    },
}));
