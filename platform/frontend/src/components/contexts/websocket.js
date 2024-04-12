import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import _ from "lodash";
import { createContext, useEffect, useState } from "react";
let webSocket = null;
try {
    webSocket = new WebSocket(
        `${process.env.NEXT_PUBLIC_WS_API_SERVER}/sessions/ws`
    );
} catch (error) {
    if (AppToaster) {
        AppToaster.show({
            intent: Intent.DANGER,
            message: `Failed to initialize websocket: ${error}`,
        });
    }
}
export const SocketContext = createContext(webSocket);
export const SocketProvider = (props) => {
    const [ws, setWs] = useState(webSocket);
    const reconnect = () => {
        setTimeout(() => {
            setWs(
                new WebSocket(
                    `${process.env.NEXT_PUBLIC_WS_API_SERVER}/sessions/ws`
                )
            );
        }, 0);
    };
    useEffect(() => {
        const onClose = () => {
            AppToaster.show({
                intent: Intent.PRIMARY,
                message: "Connected closed",
            });
        };
        // Adding an event listener to when the connection is opened
        const onOpen = () => {
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: "Connection established",
                timeout: 2000,
            });
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
        <SocketContext.Provider value={{ socket: ws, reconnectWs: reconnect }}>
            {props.children}
        </SocketContext.Provider>
    );
};
