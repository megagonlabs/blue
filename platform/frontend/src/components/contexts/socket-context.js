import { AppContext } from "@/components/contexts/app-context";
import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { createContext, useContext, useEffect, useState } from "react";
import { AuthContext } from "./auth-context";
export const SocketContext = createContext();
export const SocketProvider = ({ children }) => {
    const [ws, setWs] = useState(null);
    const { appActions } = useContext(AppContext);
    const { settings } = useContext(AuthContext);
    const [authenticating, setAuthenticating] = useState(false);
    const reconnectWs = () => {
        // get WS auth ticket
        setAuthenticating(true);
        axios.get("/accounts/websocket-ticket").then((response) => {
            try {
                let webSocket = null;
                const searchParams = new URLSearchParams({
                    ticket: response.data.ticket,
                    debug_mode: _.get(settings, "debug_mode", false),
                });
                webSocket = new WebSocket(
                    `${process.env.NEXT_PUBLIC_WS_API_SERVER}/blue/platform/${
                        process.env.NEXT_PUBLIC_PLATFORM_NAME
                    }/sessions/ws?${searchParams.toString()}`
                );
                setWs(webSocket);
            } catch (error) {
                if (AppToaster) {
                    AppToaster.show({
                        intent: Intent.DANGER,
                        message: `Failed to initialize websocket: ${error}`,
                    });
                }
            } finally {
                setAuthenticating(false);
            }
        });
    };
    useEffect(() => {
        reconnectWs();
    }, [settings.debug_mode]);
    useEffect(() => {
        const onClose = () => {
            AppToaster.show({
                intent: Intent.PRIMARY,
                message: "Connection closed",
            });
            appActions.session.setState({ key: "isSocketOpen", value: false });
        };
        // Adding an event listener to when the connection is opened
        const onOpen = () => {
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: "Connection established",
                timeout: 2000,
            });
            appActions.session.setState({ key: "isSocketOpen", value: true });
        };
        const onError = () => {
            AppToaster.show({
                intent: Intent.DANGER,
                message: `Failed to connect to websocket (onerror)`,
            });
        };
        if (!_.isNil(ws)) {
            ws.addEventListener("close", onClose);
            ws.addEventListener("open", onOpen);
            ws.addEventListener("error", onError);
            return () => {
                ws.removeEventListener("close", onClose);
                ws.removeEventListener("open", onOpen);
                ws.removeEventListener("error", onError);
            };
        }
    }, [ws, setWs]);
    return (
        <SocketContext.Provider
            value={{ authenticating, socket: ws, reconnectWs }}
        >
            {children}
        </SocketContext.Provider>
    );
};
