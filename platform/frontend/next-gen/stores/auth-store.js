import { hasIntersection } from "@/components/helper";
import axios from "axios";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import _ from "lodash";
import { create } from "zustand";
import { useAppStore } from "./app-store";
import { useSocketStore } from "./socket-store";
import { useUIVisibilityStore } from "./ui-visibility-store";
const provider = new GoogleAuthProvider();
export const useAuthStore = create((set, get) => ({
    user: null,
    permissions: {},
    initialized: false,
    isPopupOpen: false,
    signInWithGoogle: (auth) => {
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
                    canReadSessions: hasIntersection(
                        _.get(user, "permissions.sessions", []),
                        ["read_all", "read_own", "read_participate"]
                    ),
                    canWriteSessions: hasIntersection(
                        _.get(user, "permissions.sessions", []),
                        ["write_all", "write_own"]
                    ),
                    canReadAgentRegistry: hasIntersection(
                        _.get(user, "permissions.agent_registry", []),
                        ["read_all"]
                    ),
                    canWriteAgentRegistry: hasIntersection(
                        _.get(user, "permissions.agent_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canReadDataRegistry: hasIntersection(
                        _.get(user, "permissions.data_registry", []),
                        ["read_all"]
                    ),
                    canWriteDataRegistry: hasIntersection(
                        _.get(user, "permissions.data_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canReadOperatorRegistry: hasIntersection(
                        _.get(user, "permissions.operator_registry", []),
                        ["read_all"]
                    ),
                    canWriteOperatorRegistry: hasIntersection(
                        _.get(user, "permissions.operator_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canReadModelRegistry: hasIntersection(
                        _.get(user, "permissions.model_registry", []),
                        ["read_all"]
                    ),
                    canWriteModelRegistry: hasIntersection(
                        _.get(user, "permissions.model_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canReadToolRegistry: hasIntersection(
                        _.get(user, "permissions.tool_registry", []),
                        ["read_all", "read_own"]
                    ),
                    canWriteToolRegistry: hasIntersection(
                        _.get(user, "permissions.tool_registry", []),
                        ["write_all", "write_own"]
                    ),
                    canWritePlatformUsers: hasIntersection(
                        _.get(user, "permissions.platform_users", []),
                        ["write_all"]
                    ),
                    canReadPlatformAgents: hasIntersection(
                        _.get(user, "permissions.platform_agents", []),
                        ["read_all", "read_own"]
                    ),
                    canWritePlatformAgents: hasIntersection(
                        _.get(user, "permissions.platform_agents", []),
                        ["write_all", "write_own"]
                    ),
                    canReadPlatformStatus: hasIntersection(
                        _.get(user, "permissions.platform_status", []),
                        ["read_all"]
                    ),
                    canReadPlatformServices: hasIntersection(
                        _.get(user, "permissions.platform_services", []),
                        ["read_all"]
                    ),
                    canWritePlatformSettings: hasIntersection(
                        _.get(user, "permissions.platform_settings", []),
                        ["write_all"]
                    ),
                    showFormDesigner: hasIntersection(
                        _.get(user, "permissions.form_designer", []),
                        ["visible"]
                    ),
                    showPromptDesigner: hasIntersection(
                        _.get(user, "permissions.prompt_designer", []),
                        ["visible"]
                    ),
                };
                const { setState } = useAppStore.getState();
                const { setState: setUIVisibility } =
                    useUIVisibilityStore.getState();
                const KEYS = [
                    "dark_mode",
                    "show_workspace",
                    "expand_message",
                    "windows_control_buttons",
                    "detailed_message",
                    "full_window_height",
                ];
                for (let i = 0; i < _.size(KEYS); i++) {
                    setState({
                        key: KEYS[i],
                        value: _.get(user, ["settings", KEYS[i]], false),
                    });
                }
                setUIVisibility({
                    key: "UIVisibility",
                    value: _.get(user, "ui_visibility", {}),
                });
                set({ user, permissions });
            })
            .catch((error) => {})
            .finally(() => {
                set({ initialized: true });
            });
    },
}));
