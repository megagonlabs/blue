import { waitForOpenConnection } from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { create } from "zustand";
import { useSessionStore } from "./session-store";
const { NEXT_PUBLIC_WS_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
const BACKOFF = { attempts: 0, delay: 1000, timeout: null };
export const useSocketStore = create((set, get) => ({
    socket: null,
    backoff: BACKOFF,
    connectionId: null,
    setState: ({ key, value }) => set({ [key]: value }),
    sendMessage: async (message, retry = 0) => {
        const { socket } = get();
        try {
            socket.send(message);
        } catch (error) {
            if (retry < 4 && _.isEqual(error.name, "InvalidStateError")) {
                await waitForOpenConnection(socket);
                sendMessage(message, retry + 1);
            } else {
                console.error(error);
            }
        }
    },
    observeSession: (sessionId) => {
        const { sendMessage } = get();
        sendMessage(
            JSON.stringify({ type: "OBSERVE_SESSION", session_id: sessionId })
        );
    },
    connectWebSocket: (debugMode = false) => {
        const { socket } = get();
        if (!_.isNull(socket)) {
            // close existing ws connection
            const socketState = socket.readyState;
            if (!_.includes(WebSocket.CLOSED, WebSocket.CLOSING)) {
                socket.close();
            }
        }
        axios.get("/accounts/websocket-ticket").then((response) => {
            try {
                const searchParams = new URLSearchParams({
                    ticket: response.data.ticket,
                    debug_mode: debugMode,
                });
                const newSocket = new WebSocket(
                    `${NEXT_PUBLIC_WS_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}/sessions/ws?${searchParams.toString()}`
                );
                newSocket.onopen = () => {
                    const { backoff } = get();
                    AppToaster.show({
                        intent: Intent.SUCCESS,
                        message: "Connection established",
                    });
                    clearTimeout(backoff.timeout);
                    set({ backoff: BACKOFF });
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
                            set({ connectionId: data.connection_id });
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
                set({ socket: newSocket });
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
    },
}));
