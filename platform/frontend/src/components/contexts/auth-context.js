// Import the functions you need from the SDKs you need
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Drawer,
    DrawerSize,
    H1,
    H3,
    Intent,
    ProgressBar,
} from "@blueprintjs/core";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { GoogleAuthProvider, getAuth, signInWithPopup } from "firebase/auth";
import _ from "lodash";
import { createContext, useContext, useEffect, useState } from "react";
import { hasInteraction } from "../helper";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAkVp-dj3o1yf89mL3wMUtEidUHjzqyWCQ",
    authDomain: "blue-9d597.firebaseapp.com",
    projectId: "blue-9d597",
    storageBucket: "blue-9d597.appspot.com",
    messagingSenderId: "851224572522",
    appId: "1:851224572522:web:b8b3f5b50e30333773d013",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
const GOOGLE_LOGO_SVG = (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 18 18"
        fill="none"
        role="img"
    >
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M17.64 9.20419C17.64 8.56601 17.5827 7.95237 17.4764 7.36328H9V10.8446H13.8436C13.635 11.9696 13.0009 12.9228 12.0477 13.561V15.8192H14.9564C16.6582 14.2524 17.64 11.9451 17.64 9.20419Z"
            fill="#4285F4"
        ></path>
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.99976 18C11.4298 18 13.467 17.1941 14.9561 15.8195L12.0475 13.5613C11.2416 14.1013 10.2107 14.4204 8.99976 14.4204C6.65567 14.4204 4.67158 12.8372 3.96385 10.71H0.957031V13.0418C2.43794 15.9831 5.48158 18 8.99976 18Z"
            fill="#34A853"
        ></path>
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M3.96409 10.7098C3.78409 10.1698 3.68182 9.59301 3.68182 8.99983C3.68182 8.40664 3.78409 7.82983 3.96409 7.28983V4.95801H0.957273C0.347727 6.17301 0 7.54755 0 8.99983C0 10.4521 0.347727 11.8266 0.957273 13.0416L3.96409 10.7098Z"
            fill="#FBBC05"
        ></path>
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.99976 3.57955C10.3211 3.57955 11.5075 4.03364 12.4402 4.92545L15.0216 2.34409C13.4629 0.891818 11.4257 0 8.99976 0C5.48158 0 2.43794 2.01682 0.957031 4.95818L3.96385 7.29C4.67158 5.16273 6.65567 3.57955 8.99976 3.57955Z"
            fill="#EA4335"
        ></path>
    </svg>
);
export const AuthContext = createContext();
export const useAuthContext = () => useContext(AuthContext);
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [permissions, setPermissions] = useState({});
    const [settings, setSettings] = useState({});
    const [popupOpen, setPopupOpen] = useState(false);
    const [authInitialized, setAuthInitialized] = useState(false);
    const signOut = () => {
        axios.post("/accounts/sign-out").then(() => {
            setUser(null);
            setPermissions({});
        });
    };
    const getPermissions = (user) => {
        const permissions = _.get(user, "permissions", null);
        return {
            canWriteAgentRegistry: hasInteraction(
                _.get(permissions, "agent_registry", []),
                ["write_all", "write_own"]
            ),
            canWritePlatformUsers: hasInteraction(
                _.get(permissions, "platform_users", []),
                ["write_all"]
            ),
            showFormDesigner: hasInteraction(
                _.get(permissions, "form_designer", []),
                ["visible"]
            ),
            canReadPlatformAgents: hasInteraction(
                _.get(permissions, "platform_agents", []),
                ["read_all", "read_own"]
            ),
            canWritePlatformAgents: hasInteraction(
                _.get(permissions, "platform_agents", []),
                ["write_all", "write_own"]
            ),
            canReadSessions: hasInteraction(
                _.get(permissions, "sessions", []),
                ["read_all", "read_own", "read_participate"]
            ),
            canReadDataRegistry: hasInteraction(
                _.get(permissions, "data_registry", []),
                ["read_all"]
            ),
            canReadAgentRegistry: hasInteraction(
                _.get(permissions, "agent_registry", []),
                ["read_all"]
            ),
            canCreateSessions: hasInteraction(
                _.get(permissions, "sessions", []),
                ["write_all", "write_own"]
            ),
        };
    };
    const fetchAccountProfile = () => {
        axios
            .get("/accounts/profile")
            .then((response) => {
                const profile = _.get(response, "data.profile", null);
                setUser(profile);
                setPermissions(getPermissions(profile));
                setSettings(_.get(profile, "settings", {}));
            })
            .finally(() => {
                setAuthInitialized(true);
            });
    };
    const updateSettings = (key, value) => {
        setSettings({ ...settings, [key]: value });
        axios
            .post(`/accounts/profile/settings/${key}`, { value: value })
            .then(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Settings updated",
                });
            });
    };
    const signInWithGoogle = () => {
        setPopupOpen(true);
        signInWithPopup(auth, provider)
            .then((result) => {
                result.user.getIdToken().then((idToken) => {
                    axios
                        .post("/accounts/sign-in", { id_token: idToken })
                        .then(() => {
                            setPopupOpen(false);
                            fetchAccountProfile();
                        })
                        .catch(() => {
                            setPopupOpen(false);
                        });
                });
            })
            .catch((error) => {
                setPopupOpen(false);
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `${error.code ? `[${error.code}]` : ""} ${
                        error.message
                    }`,
                });
            });
    };
    useEffect(() => {
        fetchAccountProfile();
    }, []);
    return (
        <AuthContext.Provider
            value={{ user, permissions, settings, updateSettings, signOut }}
        >
            <Drawer
                size={DrawerSize.SMALL}
                portalClassName="z-index-36"
                position="bottom"
                backdropClassName="glassmorphism-5"
                isOpen={_.isNil(user) && authInitialized}
            >
                <div style={{ margin: "auto" }}>
                    <H1>Blue</H1>
                    <H3>Good to see you!</H3>
                    <div>Sign in to your account to continue.</div>
                    <Button
                        loading={!authInitialized || popupOpen}
                        large
                        style={{ marginTop: 20 }}
                        outlined
                        onClick={signInWithGoogle}
                        text="Sign in with Google"
                        icon={GOOGLE_LOGO_SVG}
                    />
                </div>
            </Drawer>
            <div style={{ display: authInitialized ? null : "none" }}>
                {children}
            </div>
            {!authInitialized ? (
                <div style={{ height: "100vh", width: "100vw" }}>
                    <div
                        style={{
                            width: "calc(100vw - 40px)",
                            maxWidth: 300,
                            height: 30,
                        }}
                        className="center-center"
                    >
                        <ProgressBar intent={Intent.PRIMARY} />
                    </div>
                </div>
            ) : null}
        </AuthContext.Provider>
    );
};
