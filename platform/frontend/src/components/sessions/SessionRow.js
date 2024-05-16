import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Card,
    Classes,
    Colors,
    H5,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCircleDot,
    faClipboard,
    faCopy,
    faPenField,
} from "@fortawesome/pro-duotone-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function SessionRow({ index, style }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionId = appState.session.sessionIds[index];
    const unreadSessionIds = appState.session.unreadSessionIds;
    const sessionMessages = appState.session.sessions[sessionId];
    const [showActions, setShowActions] = useState(false);
    const [lastMessage, setLastMessage] = useState("-");
    useEffect(() => {
        const last = _.last(sessionMessages),
            messageType = _.get(last, "message.type", "STRING"),
            messageContent = _.get(last, "message.content", null);
        if (_.isEqual(messageType, "STRING")) {
            setLastMessage(messageContent);
        } else if (_.isEqual(messageType, "INTERACTION")) {
            setLastMessage(
                <Tag minimal icon={faIcon({ icon: faPenField })}>
                    interactive message
                </Tag>
            );
        }
    }, [sessionMessages]);
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
                    #&nbsp;
                    {_.get(
                        appState,
                        ["session", "sessionDetail", sessionId, "name"],
                        sessionId
                    )}
                </H5>
                <div
                    className={`${Classes.TEXT_OVERFLOW_ELLIPSIS} ${Classes.TEXT_MUTED}`}
                    style={{
                        paddingRight: showActions ? 50 : 0,
                        lineHeight: "20px",
                    }}
                >
                    {_.isEmpty(sessionMessages) ? "-" : lastMessage}
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
                                icon: faIcon({ icon: faClipboard }),
                                message: `Copied "${sessionId}"`,
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
