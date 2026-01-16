import { waitForOpenConnection } from "@/components/helper";
import _ from "lodash";
import { create } from "zustand";
export const useSocketStore = create((set, get) => ({
    socket: null,
    connectionId: null,
    sessionAttributes: {},
    setState: ({ key, value }) => set({ [key]: value }),
    setConnectionSessionAttribute: (payload) => {
        const { sendMessage, sessionAttributes } = get();
        let newAttributes = _.cloneDeep(sessionAttributes);
        _.set(newAttributes, [payload.session_id, payload.key], payload.value);
        set({ sessionAttributes: newAttributes });
        sendMessage(
            JSON.stringify({
                type: "CONNECTION_SESSION_ATTRIBUTE",
                ...payload,
            })
        );
    },
    sendMessage: (message, retry = 0) => {
        const { socket } = get();
        try {
            socket.send(message);
        } catch (error) {
            if (retry < 4 && _.isEqual(error.name, "InvalidStateError")) {
                waitForOpenConnection(socket)
                    .then(() => {
                        sendMessage(message, retry + 1);
                    })
                    .catch((waitError) => {
                        console.error(
                            "Error waiting for WebSocket connection:",
                            waitError
                        );
                    });
            } else {
                console.error(
                    "Failed to send message after retries or unexpected error:",
                    error
                );
                socket.close();
                set({ socket: null });
            }
        }
    },
    observeSession: (sessionId) => {
        const { sendMessage } = get();
        sendMessage(
            JSON.stringify({ type: "OBSERVE_SESSION", session_id: sessionId })
        );
    },
}));
