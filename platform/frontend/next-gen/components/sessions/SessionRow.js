import { useSessionStore } from "@/stores/session-store";
import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import { useMemo } from "react";
export default function SessionRow({ sessionId }) {
    const sessions = useSessionStore((state) => state.sessions);
    const details = _.get(sessions, [sessionId, "details"], {});
    const sessionName = _.get(details, "name", sessionId);
    const displayName = useMemo(() => {
        if (_.isEqual(sessionId, sessionName)) {
            const utcSeconds = _.get(details, "created_date");
            let date = new Date(0);
            date.setUTCSeconds(utcSeconds);
            return date.toLocaleString();
        }
        return sessionName;
    }, [details]);
    const description = _.get(details, "description", "");
    return (
        <Card className="full-parent-dimension" style={{ display: "flex" }}>
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                }}
            >
                <div style={{ fontWeight: 600 }}>#&nbsp;{displayName}</div>
                <div className={Classes.TEXT_MUTED}>
                    {!_.isEmpty(description) ? description : sessionId}
                </div>
            </div>
            <div>member stack</div>
        </Card>
    );
}
