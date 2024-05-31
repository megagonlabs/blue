import { AppContext } from "@/components/contexts/app-context";
import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { createContext, useContext, useEffect, useState } from "react";
export const SocketContext = createContext();
export const SocketProvider = ({ children }) => {
    const [ws, setWs] = useState(null);
    const { appActions } = useContext(AppContext);
    const reconnect = () => {
        // get WS auth ticket
        axios.get("/accounts/websocket-ticket").then((response) => {
            try {
                let webSocket = null;
                webSocket = new WebSocket(
                    `${process.env.NEXT_PUBLIC_WS_API_SERVER}/sessions/ws?ticket=${response.data.ticket}`
                );
                setWs(webSocket);
            } catch (error) {
                if (AppToaster) {
                    AppToaster.show({
                        intent: Intent.DANGER,
                        message: `Failed to initialize websocket: ${error}`,
                    });
                }
            }
        });
    };
    useEffect(() => {
        reconnect();
    }, []);
    useEffect(() => {
        const onClose = () => {
            AppToaster.show({
                intent: Intent.PRIMARY,
                message: "Connected closed",
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
        <SocketContext.Provider value={{ socket: ws, reconnectWs: reconnect }}>
            {children}
        </SocketContext.Provider>
    );
};
