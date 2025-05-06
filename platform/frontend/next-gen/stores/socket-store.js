import { waitForOpenConnection } from "@/components/helper";
import _ from "lodash";
import { create } from "zustand";
export const useSocketStore = create((set, get) => ({
    socket: null,
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
}));
