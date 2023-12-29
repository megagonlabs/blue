import { Card, Classes, H5 } from "@blueprintjs/core";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../app-context";
export default function SessionRow({ index, style }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionId = appState.session.sessionIds[index];
    return (
        <Card
            interactive
            style={{ ...style, borderRadius: 0, padding: "20px 15px" }}
            onClick={() => appActions.session.setSessionIdFocus(sessionId)}
        >
            <div style={{ width: "100%" }}>
                <H5
                    style={{ marginBottom: 5 }}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                >
                    {sessionId}
                </H5>
                <div
                    className={`${Classes.TEXT_OVERFLOW_ELLIPSIS} ${Classes.TEXT_MUTED}`}
                >
                    {_.last(appState.session.sessions[sessionId])}
                </div>
            </div>
        </Card>
    );
}
