import { useAuthStore } from "@/stores/auth-store";
import { useSessionStore } from "@/stores/session-store";
import { useSocketStore } from "@/stores/socket-store";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import { useToaster } from "./contexts/ToasterContext";
const { NEXT_PUBLIC_WS_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
export default function SocketHandler({ children }) {
    const user = useAuthStore((state) => state.user);
    const { socket, setState } = useSocketStore(
        useShallow((state) => ({
            socket: state.socket,
            setState: state.setState,
        }))
    );
    const reconnectAttempts = useRef(0);
    const reconnectDelay = useRef(1000); // initial delay
    const reconnectTimeout = useRef(null); // use a timeout for reconnect attempts
    const resetBackoff = () => {
        reconnectAttempts.current = 0;
        reconnectDelay.current = 1000;
        reconnectTimeout.current = null;
    };
    const closeSocket = () => {
        if (!_.isNull(socket)) {
            // close existing ws connection
            if (!_.isEqual(WebSocket.CLOSED, socket.readyState)) {
                socket.close();
            }
        }
    };
    const { appToaster, showAxiosErrorToast } = useToaster();
    const connectWebSocket = () => {
        closeSocket();
        axios
            .get("/accounts/websocket-ticket")
            .then((response) => {
                try {
                    setState({
                        key: "socketReadyState",
                        value: 0,
                    });
                    const newSocket = new WebSocket(
                        `${NEXT_PUBLIC_WS_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}/sessions/ws?${new URLSearchParams(
                            { ticket: response.data.ticket }
                        ).toString()}`
                    );
                    newSocket.onopen = () => {
                        if (appToaster) {
                            appToaster.show({
                                intent: Intent.SUCCESS,
                                message: "Connection established",
                            });
                        }
                        setState({
                            key: "socketReadyState",
                            value: 1,
                        });
                        clearTimeout(reconnectTimeout.current);
                        resetBackoff();
                    };
                    newSocket.onmessage = (event) => {
                        try {
                            // parse the data from string to JSON object
                            const data = JSON.parse(event.data);
                            const type = data["type"];
                            if (_.isEqual(type, "SESSION_MESSAGE")) {
                                const { addSessionMessage } =
                                    useSessionStore.getState();
                                addSessionMessage(data);
                            } else if (_.isEqual(type, "CONNECTED")) {
                                setState({
                                    key: "connectionId",
                                    value: data.connection_id,
                                });
                            } else if (
                                _.isEqual(type, "NEW_SESSION_BROADCAST")
                            ) {
                                const { addNewSession } =
                                    useSessionStore.getState();
                                addNewSession(data["session"]);
                            }
                        } catch (error) {
                            // debug
                            appToaster.show({
                                intent: Intent.DANGER,
                                message: error,
                            });
                            console.log(event.data);
                            console.error(error);
                        }
                    };
                    newSocket.onclose = () => {
                        if (appToaster) {
                            appToaster.show({
                                intent: Intent.PRIMARY,
                                message: "Connection closed",
                            });
                        }
                        setState({
                            key: "socketReadyState",
                            value: 3,
                        });
                        setState({
                            key: "connectionId",
                            value: null,
                        });
                        // exponential backoff and reconnection using setInterval
                        const delay = Math.min(
                            reconnectDelay.current * 2,
                            60000
                        );
                        reconnectDelay.current = delay;
                        reconnectAttempts.current++;
                        if (appToaster) {
                            appToaster.show({
                                intent: Intent.PRIMARY,
                                message: `Reconnecting in ${
                                    delay / 1000
                                } seconds (attempt ${
                                    reconnectAttempts.current
                                })`,
                            });
                        }
                        // attempt reconnection
                        reconnectTimeout.current = setTimeout(
                            connectWebSocket,
                            delay
                        ); // use setTimeout for next attempt
                    };
                    newSocket.onerror = (error) => {
                        console.log(error);
                        if (appToaster) {
                            appToaster.show({
                                intent: Intent.DANGER,
                                message:
                                    "Failed to connect to websocket (onerror)",
                            });
                        }
                        newSocket.close();
                    };
                    setState({ key: "socket", value: newSocket });
                } catch (error) {
                    if (appToaster) {
                        appToaster.show({
                            intent: Intent.DANGER,
                            message: (
                                <div className="multiline-ellipsis-5">
                                    <div>
                                        Failed to initialize websocket
                                        connection
                                    </div>
                                    {error.message}
                                </div>
                            ),
                        });
                    }
                }
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            });
    };
    useEffect(() => {
        setState({
            key: "connectWebSocket",
            value: connectWebSocket,
        });
    }, [connectWebSocket]);
    useEffect(() => {
        if (!_.isNull(socket)) return;
        connectWebSocket();
        return () => {
            clearTimeout(reconnectTimeout.current);
            resetBackoff();
            closeSocket();
        };
    }, [socket]);
    useEffect(() => {
        if (_.isNull(user)) return;
        connectWebSocket();
        return () => {
            clearTimeout(reconnectTimeout.current);
            resetBackoff();
            closeSocket();
        };
    }, [user]);
    return children;
}
