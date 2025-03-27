import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { createContext, useContext, useEffect, useState } from "react";
import { AppContext } from "./app-context";
import { AuthContext } from "./auth-context";
export const SocketContext = createContext();
export const SocketProvider = ({ children }) => {
    const [ws, setWs] = useState(null);
    const { settings } = useContext(AuthContext);
    const { appActions } = useContext(AppContext);
    const [authenticating, setAuthenticating] = useState(false);
    const [isSocketOpen, setIsSocketOpen] = useState(false);
    const reconnectWs = () => {
        // close existing WS connection
        try {
            if (isSocketOpen) {
                ws.close();
            }
        } catch (error) {
            console.log(error);
        }
        setTimeout(() => {
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
                        `${
                            process.env.NEXT_PUBLIC_WS_API_SERVER
                        }/blue/platform/${
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
        }, 0);
    };
    useEffect(() => {
        reconnectWs();
    }, [settings.debug_mode]);
    useEffect(() => {
        const onMessage = (event) => {
            try {
                // parse the data from string to JSON object
                const data = JSON.parse(event.data);
                // If the data is of type SESSION_MESSAGE
                if (_.isEqual(data["type"], "SESSION_MESSAGE")) {
                    appActions.session.addSessionMessage(data);
                } else if (_.isEqual(data["type"], "CONNECTED")) {
                    appActions.session.setState({
                        key: "connectionId",
                        value: data.connection_id,
                    });
                } else if (_.isEqual(data["type"], "NEW_SESSION_BROADCAST")) {
                    appActions.session.addSession(_.get(data, "session.id"));
                    appActions.session.setSessionDetails([data["session"]]);
                }
            } catch (e) {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: event.data,
                });
                console.error(e);
            }
        };
        const onClose = () => {
            setIsSocketOpen(false);
            AppToaster.show({
                intent: Intent.PRIMARY,
                message: "Connection closed",
            });
        };
        // Adding an event listener to when the connection is opened
        const onOpen = () => {
            setIsSocketOpen(true);
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: "Connection established",
            });
        };
        const onError = () => {
            setIsSocketOpen(false);
            AppToaster.show({
                intent: Intent.DANGER,
                message: `Failed to connect to websocket (onerror)`,
            });
        };
        if (!_.isNil(ws)) {
            ws.addEventListener("close", onClose);
            ws.addEventListener("open", onOpen);
            ws.addEventListener("error", onError);
            ws.addEventListener("message", onMessage);
            return () => {
                ws.removeEventListener("close", onClose);
                ws.removeEventListener("open", onOpen);
                ws.removeEventListener("error", onError);
                ws.removeEventListener("message", onMessage);
            };
        }
        setIsSocketOpen(ws != null && _.isEqual(ws.readyState, WebSocket.OPEN));
    }, [ws, setWs]);
    return (
        <SocketContext.Provider
            value={{ authenticating, socket: ws, reconnectWs, isSocketOpen }}
        >
            {children}
        </SocketContext.Provider>
    );
};
