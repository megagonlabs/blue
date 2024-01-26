import { Button, Card, Classes, Colors, H5, Tooltip } from "@blueprintjs/core";
import { faCircleDot, faCopy } from "@fortawesome/pro-duotone-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext, useState } from "react";
import { AppContext } from "../app-context";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
export default function SessionRow({ index, style }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionId = appState.session.sessionIds[index];
    const unreadSessionIds = appState.session.unreadSessionIds;
    const sessionMessages = appState.session.sessions[sessionId];
    const [showActions, setShowActions] = useState(false);
    return (
        <Card
            interactive
            style={{
                ...style,
                borderRadius: 0,
            }}
            onMouseEnter={() => {
                setShowActions(true);
            }}
            onMouseLeave={() => {
                setShowActions(false);
            }}
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
                    style={{ paddingRight: showActions ? 50 : 0 }}
                >
                    {_.isEmpty(sessionMessages)
                        ? "-"
                        : _.last(sessionMessages).message}
                </div>
            </div>
            <div
                style={{
                    display: showActions ? null : "none",
                    position: "absolute",
                    right: 20,
                    top: "50%",
                    transform: "translateY(-50%)",
                    msTransform: "translateY(-50%)",
                }}
            >
                <Tooltip
                    content="Copy session ID"
                    minimal
                    placement="bottom-end"
                >
                    <Button
                        onClick={(event) => {
                            copy(sessionId);
                            AppToaster.show({
                                message: "Copied",
                                timeout: 2000,
                            });
                            event.stopPropagation();
                        }}
                        large
                        minimal
                        icon={faIcon({ icon: faCopy })}
                    />
                </Tooltip>
            </div>
        </Card>
    );
}
