import { useSessionStore } from "@/stores/session-store";
import { Card, Classes, Size, Tag } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import { useMemo } from "react";
import SessionMemberStack from "./SessionMemberStack";
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
        <Card
            compact
            className="full-parent-dimension responsive-container"
            style={{ alignItems: "center", paddingLeft: 20, paddingRight: 20 }}
        >
            <div
                className="session-row-info"
                style={{
                    height: 40,
                    display: "flex",
                    justifyContent: "space-between",
                    flexDirection: "column",
                }}
            >
                <div style={{ fontWeight: 600 }}>#&nbsp;{displayName}</div>
                <div
                    className={classNames(
                        Classes.TEXT_MUTED,
                        Classes.TEXT_OVERFLOW_ELLIPSIS
                    )}
                >
                    {!_.isEmpty(description) ? description : sessionId}
                </div>
            </div>
            <div className="session-row-message">
                <Tag size={Size.LARGE} minimal>
                    message
                </Tag>
            </div>
            <div className="session-row-members" style={{ height: 40 }}>
                <SessionMemberStack sessionId={sessionId} />
            </div>
        </Card>
    );
}
