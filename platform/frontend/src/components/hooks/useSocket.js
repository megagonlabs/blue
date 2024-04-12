import { SocketContext } from "@/components/contexts/websocket";
import { useContext } from "react";
export const useSocket = () => {
    const socket = useContext(SocketContext);
    return socket;
};
