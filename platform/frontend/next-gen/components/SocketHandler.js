import { useAuthStore } from "@/stores/auth-store";
import { useSocketStore } from "@/stores/socket-store";
import _ from "lodash";
import { useEffect } from "react";
export default function SocketHandler({ children }) {
    const user = useAuthStore((state) => state.user);
    const debugMode = _.get(user, "settings.debug_mode", false);
    const connectWebSocket = useSocketStore((state) => state.connectWebSocket);
    useEffect(() => {
        if (_.isNull(user)) return;
        connectWebSocket(debugMode);
    }, [user, debugMode]);
    return children;
}
