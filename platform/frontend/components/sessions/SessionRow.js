import { Card, Classes, Colors, H5 } from "@blueprintjs/core";
import { faCircleDot } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../app-context";
import { faIcon } from "../icon";
export default function SessionRow({ index, style }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionId = appState.session.sessionIds[index];
    const unreadSessionIds = appState.session.unreadSessionIds;
    return (
        <Card
            interactive
            style={{ ...style, borderRadius: 0 }}
            onClick={() => appActions.session.setSessionIdFocus(sessionId)}
        >
            <div style={{ width: 31 }}>
                {unreadSessionIds.has(sessionId)
                    ? faIcon({
                          icon: faCircleDot,
                          style: {
                              color: Colors.BLUE5,
                              opacity: 0.5,
                          },
                      })
                    : null}
            </div>
            <div style={{ width: "calc(100% - 31px)" }}>
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
