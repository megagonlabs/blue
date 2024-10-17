import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
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
    faThumbTack,
    faThumbTackSlash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { useSocket } from "../hooks/useSocket";
export default function SessionRow({ index, style }) {
    const { appState, appActions } = useContext(AppContext);
    const {
        unreadSessionIds,
        sessionIdFocus,
        pinnedSessionIds,
        groupedSessionIds,
        sessions,
    } = appState.session;
    const sessionId = groupedSessionIds[index];
    const isPinned = pinnedSessionIds.has(sessionId);
    const messages = _.get(sessions, [sessionId, "messages"], []);
    const streams = _.get(sessions, [sessionId, "streams"], {});
    const sessionName = _.get(
        appState,
        ["session", "sessionDetails", sessionId, "name"],
        sessionId
    );
    const [showActions, setShowActions] = useState(false);
    const [lastMessage, setLastMessage] = useState("-");
    useEffect(() => {
        const lastMessage = _.last(messages);
        if (_.isEmpty(lastMessage)) {
            setLastMessage("-");
        } else {
            const complete = _.get(
                streams,
                [lastMessage.stream, "complete"],
                false
            );
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
                const contentType = _.get(lastMessage, "contentType", null);
                if (_.includes(["STR", "INT", "FLOAT"], contentType)) {
                    const data = _.get(
                        streams,
                        [lastMessage.stream, "data"],
                        []
                    );
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
                            FORM
                        </Tag>
                    );
                } else {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faQuestion })}>
                            UNKNOWN
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
    const [updatingPin, setUpdatingPin] = useState(false);
    const handlePinSession = () => {
        setUpdatingPin(true);
        axios
            .put(`/sessions/session/${sessionId}/${isPinned ? "un" : ""}pin`)
            .then(() => {
                if (isPinned)
                    appActions.session.removePinnedSessionId(sessionId);
                else appActions.session.addPinnedSessionId(sessionId);
                AppToaster.show({
                    icon: faIcon({ icon: faThumbTack }),
                    message: `${
                        isPinned ? "Unpinned" : "Pinned"
                    } "${sessionName}"`,
                });
            })
            .finally(() => {
                setUpdatingPin(false);
            });
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
                borderBottom: "1px solid rgba(17, 20, 24, 0.1)",
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
            <div
                style={{
                    width: "calc(100% - 31px)",
                    paddingRight: showActions ? 90 : 0,
                }}
            >
                <H5
                    style={{ marginBottom: 5 }}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                >
                    #&nbsp;
                    {sessionName}
                </H5>
                <div
                    className={`${Classes.TEXT_OVERFLOW_ELLIPSIS} ${Classes.TEXT_MUTED}`}
                    style={{ height: 20, lineHeight: "20px" }}
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
                <ButtonGroup large minimal>
                    <Tooltip
                        content={isPinned ? "Unpin" : "Pin"}
                        minimal
                        placement="bottom"
                    >
                        <Button
                            loading={updatingPin}
                            onClick={(event) => {
                                handlePinSession();
                                event.stopPropagation();
                            }}
                            icon={faIcon({
                                icon: isPinned ? faThumbTackSlash : faThumbTack,
                                size: isPinned ? 20 : 16,
                            })}
                        />
                    </Tooltip>
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
                                });
                                event.stopPropagation();
                            }}
                            icon={faIcon({ icon: faCopy })}
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
        </Card>
    );
}
