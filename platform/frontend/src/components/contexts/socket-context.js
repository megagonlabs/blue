import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import { AppContext } from "./app-context";
import { AuthContext } from "./auth-context";
export const SocketContext = createContext();
export const SocketProvider = ({ children }) => {
    const { settings } = useContext(AuthContext);
    const { appState, appActions } = useContext(AppContext);
    const [authenticating, setAuthenticating] = useState(false);
    const [isSocketOpen, setIsSocketOpen] = useState(false);
    const socketRef = useRef(null);
    const reconnectAttempts = useRef(0);
    const reconnectDelay = useRef(1000); // Initial delay
    const reconnectTimeout = useRef(null); // Use a timeout for reconnect attempts
    useEffect(() => {
        if (_.isUndefined(settings.debug_mode)) return;
        const connectWebSocket = () => {
            // close existing WS connection
            try {
                if (isSocketOpen) socketRef.current.close();
            } catch (error) {
                console.log(error);
            }
            // get WS auth ticket
            setAuthenticating(true);
            axios.get("/accounts/websocket-ticket").then((response) => {
                try {
                    const searchParams = new URLSearchParams({
                        ticket: response.data.ticket,
                        debug_mode: _.get(settings, "debug_mode", false),
                    });
                    socketRef.current = new WebSocket(
                        `${
                            process.env.NEXT_PUBLIC_WS_API_SERVER
                        }/blue/platform/${
                            process.env.NEXT_PUBLIC_PLATFORM_NAME
                        }/sessions/ws?${searchParams.toString()}`
                    );
                    // re-observe current session
                    if (!_.isEmpty(appState.session.sessionIdFocus))
                        appActions.session.observeSession({
                            sessionId: appState.session.sessionIdFocus,
                            socket: socketRef.current,
                        });
                    socketRef.current.onopen = () => {
                        setIsSocketOpen(true);
                        reconnectAttempts.current = 0;
                        reconnectDelay.current = 1000;
                        AppToaster.show({
                            intent: Intent.SUCCESS,
                            message: "Connection established",
                        });
                        clearTimeout(reconnectTimeout.current); // Clear any pending reconnect attempts
                    };
                    socketRef.current.onmessage = (event) => {
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
                            } else if (
                                _.isEqual(data["type"], "NEW_SESSION_BROADCAST")
                            ) {
                                appActions.session.addSession(
                                    _.get(data, "session.id")
                                );
                                appActions.session.setSessionDetails([
                                    data["session"],
                                ]);
                            }
                        } catch (e) {
                            AppToaster.show({
                                intent: Intent.DANGER,
                                message: e,
                            });
                            console.log(event.data);
                            console.error(e);
                        }
                    };
                    socketRef.current.onclose = () => {
                        setIsSocketOpen(false);
                        AppToaster.show({
                            intent: Intent.PRIMARY,
                            message: "Connection closed",
                        });
                        // Exponential backoff and reconnection using setInterval
                        const delay = Math.min(
                            reconnectDelay.current * 2,
                            60000
                        );
                        reconnectDelay.current = delay;
                        reconnectAttempts.current++;
                        AppToaster.show({
                            intent: Intent.PRIMARY,
                            message: `Reconnecting in ${
                                delay / 1000
                            } seconds (attempt ${reconnectAttempts.current})`,
                        });
                        // Attempt reconnection
                        reconnectTimeout.current = setTimeout(
                            connectWebSocket,
                            delay
                        ); // Use setTimeout for next attempt
                    };
                    socketRef.current.onerror = () => {
                        setIsSocketOpen(false);
                        AppToaster.show({
                            intent: Intent.DANGER,
                            message: `Failed to connect to websocket (onerror)`,
                        });
                        socketRef.current.close();
                    };
                } catch (error) {
                    AppToaster.show({
                        intent: Intent.DANGER,
                        message: `Failed to initialize websocket: ${error}`,
                    });
                } finally {
                    setAuthenticating(false);
                }
            });
        };
        connectWebSocket();
        return () => {
            if (socketRef.current) socketRef.current.close();
            clearTimeout(reconnectTimeout.current); // Clear timeout on unmount or component updates
        };
    }, [settings.debug_mode]);
    return (
        <SocketContext.Provider
            value={{ authenticating, socket: socketRef.current, isSocketOpen }}
        >
            {children}
        </SocketContext.Provider>
    );
};
