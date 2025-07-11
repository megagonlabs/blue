import { AppToaster } from "@/components/toaster";
import { useAuthStore } from "@/stores/auth-store";
import { useSessionStore } from "@/stores/session-store";
import { useSocketStore } from "@/stores/socket-store";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef } from "react";
const { NEXT_PUBLIC_WS_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
export default function SocketHandler({ children }) {
    const user = useAuthStore((state) => state.user);
    const socket = useSocketStore((state) => state.socket);
    const setState = useSocketStore((state) => state.setState);
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
    const connectWebSocket = () => {
        closeSocket();
        axios.get("/accounts/websocket-ticket").then((response) => {
            try {
                const newSocket = new WebSocket(
                    `${NEXT_PUBLIC_WS_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}/sessions/ws?${new URLSearchParams(
                        { ticket: response.data.ticket }
                    ).toString()}`
                );
                newSocket.onopen = () => {
                    AppToaster.show({
                        intent: Intent.SUCCESS,
                        message: "Connection established",
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
                        } else if (_.isEqual(type, "NEW_SESSION_BROADCAST")) {
                            const { addNewSession } =
                                useSessionStore.getState();
                            addNewSession(data["session"]);
                        }
                    } catch (e) {
                        // debug
                        AppToaster.show({
                            intent: Intent.DANGER,
                            message: e,
                        });
                        console.log(event.data);
                        console.error(e);
                    }
                };
                newSocket.onclose = () => {
                    AppToaster.show({
                        intent: Intent.PRIMARY,
                        message: "Connection closed",
                    });
                    // exponential backoff and reconnection using setInterval
                    const delay = Math.min(reconnectDelay.current * 2, 60000);
                    reconnectDelay.current = delay;
                    reconnectAttempts.current++;
                    AppToaster.show({
                        intent: Intent.PRIMARY,
                        message: `Reconnecting in ${
                            delay / 1000
                        } seconds (attempt ${reconnectAttempts.current})`,
                    });
                    // attempt reconnection
                    reconnectTimeout.current = setTimeout(
                        connectWebSocket,
                        delay
                    ); // use setTimeout for next attempt
                };
                newSocket.onerror = (error) => {
                    console.log(error);
                    AppToaster.show({
                        intent: Intent.DANGER,
                        message: "Failed to connect to websocket (onerror)",
                    });
                    newSocket.close();
                };
                setState({ key: "socket", value: newSocket });
            } catch (error) {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: (
                        <div className="multiline-ellipsis-5">
                            <div>Failed to initialize websocket connection</div>
                            {error.message}
                        </div>
                    ),
                });
            }
        });
    };
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
