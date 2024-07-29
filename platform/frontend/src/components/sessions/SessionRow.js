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
    faBracketsCurly,
    faCircleDot,
    faClipboard,
    faCopy,
    faEllipsisH,
    faPenLine,
    faQuestion,
} from "@fortawesome/pro-duotone-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { useSocket } from "../hooks/useSocket";
export default function SessionRow({ index, style }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const sessionId = appState.session.sessionIds[index];
    const unreadSessionIds = appState.session.unreadSessionIds;
    const messages = appState.session.sessions[sessionId].messages;
    const streams = appState.session.sessions[sessionId].streams;
    const [showActions, setShowActions] = useState(false);
    const [lastMessage, setLastMessage] = useState("-");
    useEffect(() => {
        const last = _.last(messages);
        if (_.isEmpty(last)) {
            setLastMessage("-");
        } else {
            const complete = _.get(streams, [last.stream, "complete"], false);
            if (!complete) {
                setLastMessage(
                    <Tag
                        minimal
                        icon={faIcon({
                            icon: faEllipsisH,
                            size: 16.5,
                            className: "fa-fade",
                            style: { color: Colors.BLACK },
                        })}
                    />
                );
            } else {
                const contentType = _.get(last, "contentType", null);
                if (_.includes(["STR", "INT", "FLOAT"], contentType)) {
                    const data = _.get(streams, [last.stream, "data"], []);
                    setLastMessage(_.join(_.map(data, "content"), " "));
                } else if (_.isEqual(contentType, "JSON")) {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faBracketsCurly })}>
                            JSON
                        </Tag>
                    );
                } else if (_.isEqual(contentType, "JSON_FORM")) {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faPenLine })}>
                            Form
                        </Tag>
                    );
                } else {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faQuestion })}>
                            Unknown
                        </Tag>
                    );
                }
            }
        }
    }, [messages, streams]);
    const { socket } = useSocket();
    const handleSetSessionIdFocus = () => {
        appActions.session.observeSession({
            sessionId,
            socket,
        });
        appActions.session.setSessionIdFocus(sessionId);
    };
    return (
        <Card
            interactive
            style={{
                ...style,
                borderRadius: 0,
                backgroundColor: _.isEqual(sessionIdFocus, sessionId)
                    ? "#F6F7F9"
                    : null,
            }}
            onMouseEnter={() => {
                setShowActions(true);
            }}
            onMouseLeave={() => {
                setShowActions(false);
            }}
            onClick={handleSetSessionIdFocus}
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
                        height: 20,
                        lineHeight: "20px",
                    }}
                >
                    {lastMessage}
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
