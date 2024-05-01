import AddAgents from "@/components/agents/AddAgents";
import { AppContext } from "@/components/contexts/app-context";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
import SessionDetail from "@/components/sessions/SessionDetail";
import SessionList from "@/components/sessions/SessionList";
import SessionMessages from "@/components/sessions/SessionMessages";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    H4,
    InputGroup,
    Intent,
    Menu,
    MenuItem,
    NonIdealState,
    Popover,
    Tag,
    TextArea,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCaretDown,
    faCircleA,
    faInboxIn,
    faInboxOut,
    faMessages,
    faPlusLarge,
    faSatelliteDish,
    faSignalStreamSlash,
    faUserPlus,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { FixedSizeList } from "react-window";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const sessionIds = appState.session.sessionIds;
    const [message, setMessage] = useState("");
    const [joinSessionId, setJoinSessionId] = useState("");
    const sessionMessageTextArea = useRef(null);
    const [isSessionDetailOpen, setIsSessionDetailOpen] = useState(false);
    const { socket, reconnectWs } = useSocket();
    const socketReadyState = _.get(socket, "readyState", 3);
    const sendSessionMessage = (message) => {
        if (!_.isEqual(socketReadyState, 1)) return;
        setMessage("");
        socket.send(
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: appState.session.sessionIdFocus,
                message: message,
            })
        );
    };
    const onMessage = useCallback(
        (event) => {
            // Listening to messages from the server
            try {
                // parse the data from string to JSON object
                const data = JSON.parse(event.data);
                // If the data is of type SESSION_MESSAGE
                if (_.isEqual(data["type"], "SESSION_MESSAGE")) {
                    appActions.session.addSessionMessage(data);
                } else if (_.isEqual(data["type"], "CONNECTED")) {
                    appActions.session.setState({
                        key: "connectionId",
                        value: data.id,
                    });
                } else if (_.isEqual(data["type"], "NEW_SESSION_BROADCAST")) {
                    appActions.session.observeSession({
                        sessionId: data["session_id"],
                        socket: socket,
                    });
                }
            } catch (e) {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: event.data,
                });
                console.error(e);
            }
        },
        [socket]
    );
    useEffect(() => {
        if (!_.isNil(socket)) {
            socket.addEventListener("message", onMessage);
            return () => {
                socket.removeEventListener("message", onMessage);
            };
        }
    }, [socket, onMessage]);
    useEffect(() => {
        if (sessionMessageTextArea.current) {
            sessionMessageTextArea.current.focus();
        }
    }, [sessionIdFocus]);
    const SESSION_LISTL_PANEL_WIDTH = 451.65;
    const [getSessionsRequest, setGetSessionsRequest] = useState(null);
    const [existingSessions, setExistingSessions] = useState(null);
    const fetchExistingSessions = () => {
        if (!_.isNil(getSessionsRequest)) {
            getSessionsRequest.cancel();
            setGetSessionsRequest(null);
        }
        const requestSource = axios.CancelToken.source();
        setGetSessionsRequest(requestSource);
        axios
            .get("/sessions", {
                cancelToken: requestSource.token,
            })
            .then((response) => {
                setExistingSessions(
                    _.get(response, "data.results", []).filter((session) => {
                        return !_.includes(sessionIds, session.id);
                    })
                );
            })
            .catch((error) => {});
    };
    const initialJoinAll = useRef(true);
    const joinAllSessions = () => {
        // automatically join all existing sessions onload
        axios
            .get("/sessions")
            .then((response) => {
                const sessions = _.get(response, "data.results", []);
                appActions.session.setSessionDetail(sessions);
                for (let i = 0; i < sessions.length; i++) {
                    const sessionId = sessions[i].id;
                    if (_.includes(sessionIds, sessionId)) continue;
                    appActions.session.observeSession({
                        sessionId: sessionId,
                        socket: socket,
                    });
                }
            })
            .catch((error) => {});
    };

    useEffect(() => {
        if (!_.isEqual(socketReadyState, 1)) return;
        if (initialJoinAll.current) {
            initialJoinAll.current = false;
            socket.send(JSON.stringify({ type: "REQUEST_CONNECTION_ID" }));
            joinAllSessions();
        }
    }, [socketReadyState]);
    const isSocketOpen = appState.session.isSocketOpen;
    const ReconnectButton = () => {
        return (
            <Button
                icon={faIcon({ icon: faSatelliteDish })}
                onClick={reconnectWs}
                intent={Intent.PRIMARY}
                large
                loading={_.isEqual(socketReadyState, 0)}
                text="Reconnect"
            />
        );
    };
    const [sessionDetailTooltipOpen, setSessionDetailTooltipOpen] =
        useState(false);
    const [isAddAgentsOpen, setIsAddAgentsOpen] = useState(false);
    const [skippable, setSkippable] = useState(false);
    const sessionName = _.get(
        appState,
        ["session", "sessionDetail", sessionIdFocus, "name"],
        sessionIdFocus
    );
    useEffect(() => {
        if (appState.session.openAgentsDialogTrigger) {
            setIsCreatingSession(false);
            setIsAddAgentsOpen(true);
            setSkippable(true);
            appActions.session.setState({
                key: "openAgentsDialogTrigger",
                value: false,
            });
        }
    }, [appState.session.openAgentsDialogTrigger]);
    const [isCreatingSession, setIsCreatingSession] = useState(false);
    if (!isSocketOpen && _.isEmpty(sessionIds))
        return (
            <NonIdealState
                icon={faIcon({ icon: faSignalStreamSlash, size: 50 })}
                title={
                    _.isEqual(socketReadyState, 0)
                        ? "Connecting"
                        : "No connection"
                }
                action={<ReconnectButton />}
            />
        );
    return (
        <>
            <div
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    height: "calc(100% - 1px)",
                    width: SESSION_LISTL_PANEL_WIDTH,
                }}
            >
                <div
                    style={{
                        padding: 20,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                    }}
                >
                    <ButtonGroup large>
                        <Tooltip
                            minimal
                            placement="bottom-start"
                            content="Start a new session"
                        >
                            <Button
                                disabled={!_.isEqual(socketReadyState, 1)}
                                text="New"
                                outlined
                                loading={isCreatingSession}
                                intent={Intent.PRIMARY}
                                onClick={() => {
                                    if (!_.isEqual(socketReadyState, 1)) return;
                                    setIsCreatingSession(true);
                                    appActions.session.createSession();
                                }}
                                rightIcon={faIcon({ icon: faInboxOut })}
                            />
                        </Tooltip>
                        <Popover
                            placement="bottom"
                            onOpening={fetchExistingSessions}
                            onClose={() => {
                                setExistingSessions(null);
                                setJoinSessionId("");
                            }}
                            content={
                                <div>
                                    <div style={{ padding: 15 }}>
                                        <InputGroup
                                            placeholder="Session ID"
                                            large
                                            autoFocus
                                            fill
                                            value={joinSessionId}
                                            onChange={(event) => {
                                                setJoinSessionId(
                                                    event.target.value
                                                );
                                            }}
                                            rightElement={
                                                <Button
                                                    className={
                                                        Classes.POPOVER_DISMISS
                                                    }
                                                    minimal
                                                    disabled={_.isEmpty(
                                                        joinSessionId
                                                    )}
                                                    text="Join"
                                                    onClick={() => {
                                                        if (
                                                            _.isEmpty(
                                                                joinSessionId
                                                            ) ||
                                                            !_.isEqual(
                                                                socketReadyState,
                                                                1
                                                            ) ||
                                                            _.includes(
                                                                sessionIds,
                                                                joinSessionId
                                                            )
                                                        )
                                                            return;
                                                        appActions.session.observeSession(
                                                            {
                                                                sessionId:
                                                                    joinSessionId,
                                                                socket: socket,
                                                            }
                                                        );
                                                        setJoinSessionId("");
                                                    }}
                                                    intent={Intent.SUCCESS}
                                                />
                                            }
                                        />
                                    </div>
                                    {!_.isEmpty(existingSessions) ? (
                                        <FixedSizeList
                                            className="bp-border-top"
                                            height={210}
                                            itemCount={_.size(existingSessions)}
                                            itemSize={40}
                                        >
                                            {({ index, style }) => {
                                                const item =
                                                    existingSessions[index];
                                                return (
                                                    <div style={style}>
                                                        <Tag
                                                            onClick={() => {
                                                                if (
                                                                    _.includes(
                                                                        sessionIds,
                                                                        item.id
                                                                    )
                                                                )
                                                                    return;
                                                                appActions.session.observeSession(
                                                                    {
                                                                        sessionId:
                                                                            item.id,
                                                                        socket: socket,
                                                                    }
                                                                );
                                                            }}
                                                            intent={
                                                                !_.includes(
                                                                    sessionIds,
                                                                    item.id
                                                                )
                                                                    ? Intent.PRIMARY
                                                                    : null
                                                            }
                                                            interactive={
                                                                !_.includes(
                                                                    sessionIds,
                                                                    item.id
                                                                )
                                                            }
                                                            large
                                                            minimal
                                                            style={{
                                                                margin: 15,
                                                                width: "calc(100% - 30px)",
                                                            }}
                                                            key={item.id}
                                                        >
                                                            <div
                                                                className={
                                                                    _.includes(
                                                                        sessionIds,
                                                                        item.id
                                                                    )
                                                                        ? Classes.TEXT_DISABLED
                                                                        : null
                                                                }
                                                            >
                                                                {item.name}
                                                            </div>
                                                        </Tag>
                                                    </div>
                                                );
                                            }}
                                        </FixedSizeList>
                                    ) : null}
                                </div>
                            }
                        >
                            <Tooltip
                                minimal
                                placement="bottom"
                                content="Join an existing session"
                            >
                                <Button
                                    disabled={!isSocketOpen}
                                    outlined
                                    text="Join"
                                    rightIcon={faIcon({ icon: faUserPlus })}
                                />
                            </Tooltip>
                        </Popover>
                    </ButtonGroup>
                    {!isSocketOpen ? <ReconnectButton /> : null}
                </div>
                {_.isEmpty(appState.session.sessionIds) ? (
                    <Card
                        style={{
                            padding: 0,
                            marginTop: 1,
                            height: "calc(100% - 80px)",
                            width: "calc(100% - 1.35px)",
                            borderRadius: 0,
                        }}
                    >
                        <NonIdealState
                            icon={faIcon({ icon: faInboxIn, size: 50 })}
                            title="Sessions"
                        />
                    </Card>
                ) : (
                    <SessionList />
                )}
            </div>
            <div
                style={{
                    height: "calc(100% - 80px)",
                    marginLeft: SESSION_LISTL_PANEL_WIDTH,
                    width: `calc(100vw - ${
                        SESSION_LISTL_PANEL_WIDTH + 160.55
                    }px)`,
                }}
            >
                <Card
                    style={{
                        borderRadius: 0,
                        display: "flex",
                        alignItems: "center",
                        height: 80,
                        justifyContent: "space-between",
                    }}
                >
                    {!_.isNull(sessionIdFocus) ? (
                        <Tooltip
                            minimal
                            isOpen={sessionDetailTooltipOpen}
                            content="Get session details"
                            placement="bottom-start"
                        >
                            <Button
                                onMouseEnter={() => {
                                    setSessionDetailTooltipOpen(true);
                                }}
                                onBlur={() => {
                                    setSessionDetailTooltipOpen(false);
                                }}
                                onMouseLeave={() => {
                                    setSessionDetailTooltipOpen(false);
                                }}
                                large
                                minimal
                                onClick={() => {
                                    setIsSessionDetailOpen(true);
                                }}
                                rightIcon={faIcon({ icon: faCaretDown })}
                                text={
                                    <H4 style={{ margin: 0 }}>
                                        #&nbsp;{sessionName}
                                    </H4>
                                }
                            />
                        </Tooltip>
                    ) : null}
                </Card>
                {_.isNull(sessionIdFocus) ? (
                    <NonIdealState
                        icon={faIcon({ icon: faMessages, size: 50 })}
                        title="Messages"
                    />
                ) : (
                    <>
                        <div style={{ height: "calc(100% - 131px" }}>
                            <SessionMessages />
                        </div>
                        <div
                            style={{
                                padding: 20,
                                position: "relative",
                                height: "calc(100% - 772px",
                                borderTop: "1px solid rgba(17, 20, 24, 0.15)",
                            }}
                        >
                            <div
                                style={{
                                    position: "absolute",
                                    height: "calc(100% - 40px)",
                                    top: "50%",
                                    transform: "translateY(-50%)",
                                    msTransform: "translateY(-50%)",
                                    left: 20,
                                }}
                            >
                                <Popover
                                    minimal
                                    placement="top-start"
                                    targetProps={{ style: { height: "100%" } }}
                                    content={
                                        <Menu large>
                                            <MenuItem
                                                onClick={() => {
                                                    setIsAddAgentsOpen(true);
                                                }}
                                                icon={faIcon({
                                                    icon: faCircleA,
                                                })}
                                                text="Agents"
                                            ></MenuItem>
                                        </Menu>
                                    }
                                >
                                    <Button
                                        disabled={!isSocketOpen}
                                        large
                                        minimal
                                        style={{
                                            borderTopRightRadius: 0,
                                            borderBottomRightRadius: 0,
                                            paddingBottom: 62,
                                            paddingTop: 12,
                                        }}
                                        icon={faIcon({ icon: faPlusLarge })}
                                    />
                                </Popover>
                            </div>
                            <TextArea
                                disabled={!isSocketOpen}
                                inputRef={sessionMessageTextArea}
                                style={{
                                    resize: "none",
                                    minHeight: "100%",
                                    paddingLeft: 50,
                                }}
                                value={message}
                                placeholder={`Message # ${sessionName}`}
                                onChange={(event) => {
                                    setMessage(event.target.value);
                                }}
                                onKeyDown={(event) => {
                                    if (
                                        _.isEqual(event.key, "Enter") &&
                                        !event.shiftKey &&
                                        isSocketOpen
                                    ) {
                                        sendSessionMessage(message);
                                        event.preventDefault();
                                    }
                                }}
                                fill
                            />
                        </div>
                    </>
                )}
            </div>
            <SessionDetail
                setIsSessionDetailOpen={setIsSessionDetailOpen}
                isOpen={isSessionDetailOpen}
            />
            <AddAgents
                skippable={skippable}
                setSkippable={setSkippable}
                setIsAddAgentsOpen={setIsAddAgentsOpen}
                isOpen={isAddAgentsOpen}
            />
        </>
    );
}
