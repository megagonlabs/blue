import { useSessionStore } from "@/stores/session-store";
import _ from "lodash";
import { useMemo } from "react";
export default function SessionDisplayName({ sessionId }) {
    const sessions = useSessionStore((state) => state.sessions);
    const details = _.get(sessions, [sessionId, "details"], {});
    const sessionName = _.get(details, "name", sessionId);
    const displayName = useMemo(() => {
        if (_.isEqual(sessionId, sessionName) || _.isEmpty(sessionName)) {
            const utcSeconds = _.get(details, "created_date");
            let date = new Date(0);
            date.setUTCSeconds(utcSeconds);
            return date.toLocaleString();
        }
        return sessionName;
    }, [details]);
    return <>#&nbsp;{displayName}</>;
}
