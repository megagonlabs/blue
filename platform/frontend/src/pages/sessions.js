import { AppContext } from "@/components/app-context";
import { faIcon } from "@/components/icon";
import SessionList from "@/components/sessions/SessionList";
import SessionMessages from "@/components/sessions/SessionMessages";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    H4,
    H5,
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
    faCirclePlus,
    faInboxIn,
    faInboxOut,
    faMessages,
    faSignalStreamSlash,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import { FixedSizeList } from "react-window";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const sessionIds = appState.session.sessionIds;
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [joinSessionId, setJoinSessionId] = useState("");
    const sessionMessageTextArea = useRef(null);
    const sendSessionMessage = (message) => {
        if (_.isNil(appState.session.connection)) return;
        setMessage("");
        appState.session.connection.send(
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: appState.session.sessionIdFocus,
                message: message,
            })
        );
    };
    const handleConnectToWebsocket = () => {
        if (!_.isNil(appState.session.connection)) return;
        if (_.isFunction(setLoading)) {
            setLoading(true);
        }
        try {
            // Creating an instance of the WebSocket
            const socket = new WebSocket(
                `${process.env.NEXT_PUBLIC_WS_API_SERVER}/sessions/ws`
            );
            // Listening to messages from the server
            socket.onmessage = (event) => {
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
                    } else if (
                        _.isEqual(data["type"], "NEW_SESSION_BROADCAST")
                    ) {
                        appActions.session.observeSessionBroadcast(
                            data["session_id"]
                        );
                    }
                } catch (e) {
                    AppToaster.show({
                        intent: Intent.PRIMARY,
                        message: event.data,
                    });
                    console.log(event.data);
                    console.error(e);
                }
            };
            socket.onerror = () => {
                if (_.isFunction(setLoading)) {
                    setLoading(false);
                }
                appActions.session.setState({ key: "connection", value: null });
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `Failed to connect to websocketc (onerror)`,
                });
            };
            socket.onclose = () => {
                if (_.isFunction(setLoading)) {
                    setLoading(false);
                }
                appActions.session.setState({ key: "connection", value: null });
                AppToaster.show({
                    intent: Intent.PRIMARY,
                    message: "Connected closed",
                });
            };
            // Adding an event listener to when the connection is opened
            socket.onopen = () => {
                if (_.isFunction(setLoading)) {
                    setLoading(false);
                }
                appActions.session.setState({
                    key: "connection",
                    value: socket,
                });
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Connection established",
                    timeout: 2000,
                });
                if (!_.isEmpty(sessionIds)) {
                    for (var i = 0; i < sessionIds.length; i++) {
                        appActions.session.observeSession({
                            sessionId: sessionIds[i],
                            connection: socket,
                        });
                    }
                }
            };
        } catch (e) {
            if (_.isFunction(setLoading)) {
                setLoading(false);
            }
            appActions.session.setState({ key: "connection", value: null });
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: `Failed to connect to websocket: ${e}`,
            });
        }
    };
    useEffect(() => {
        handleConnectToWebsocket();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps
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
        axios.get("/sessions").then((response) => {
            const sessions = _.get(response, "data.results", []);
            for (let i = 0; i < sessions.length; i++) {
                const sessionId = sessions[i].id;
                if (_.includes(sessionIds, sessionId)) continue;
                appActions.session.observeSession({
                    sessionId: sessionId,
                    connection: appState.session.connection,
                });
            }
        });
    };
    useEffect(() => {
        if (_.isNil(appState.session.connection)) return;
        if (initialJoinAll.current) {
            initialJoinAll.current = false;
            joinAllSessions();
        }
    }, [appState.session.connection]);
    if (_.isNil(appState.session.connection))
        return (
            <NonIdealState
                icon={faIcon({ icon: faSignalStreamSlash, size: 50 })}
                title={loading ? "Connecting" : "No connection"}
                action={
                    <Button
                        onClick={handleConnectToWebsocket}
                        intent={Intent.PRIMARY}
                        large
                        loading={loading}
                        text="Reconnect"
                    />
                }
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
                                disabled={_.isNil(appState.session.connection)}
                                text="New"
                                outlined
                                intent={Intent.PRIMARY}
                                onClick={() => {
                                    if (_.isNil(appState.session.connection))
                                        return;
                                    appActions.session.createSession({
                                        platform: appState.session.platform,
                                        connection: appState.session.connection,
                                    });
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
                                    <div style={{ padding: 10 }}>
                                        <H5>Join an existing session</H5>
                                        <InputGroup
                                            large
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
                                                            _.isNil(
                                                                appState.session
                                                                    .connection
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
                                                                connection:
                                                                    appState
                                                                        .session
                                                                        .connection,
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
                                            height={267}
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
                                                                        connection:
                                                                            appState
                                                                                .session
                                                                                .connection,
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
                                                                margin: 10,
                                                                width: "calc(100% - 20px)",
                                                            }}
                                                            id={item.id}
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
                            <Button
                                outlined
                                icon={faIcon({ icon: faCaretDown })}
                            />
                        </Popover>
                    </ButtonGroup>
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
                    <H4
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{ margin: 0 }}
                    >
                        {sessionIdFocus}
                    </H4>
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
                                                disabled
                                                icon={faIcon({
                                                    icon: faCircleA,
                                                })}
                                                text="Agents"
                                            ></MenuItem>
                                        </Menu>
                                    }
                                >
                                    <Button
                                        large
                                        minimal
                                        style={{
                                            borderTopRightRadius: 0,
                                            borderBottomRightRadius: 0,
                                            paddingBottom: 62,
                                            paddingTop: 12,
                                        }}
                                        icon={faIcon({ icon: faCirclePlus })}
                                    />
                                </Popover>
                            </div>
                            <TextArea
                                inputRef={sessionMessageTextArea}
                                style={{
                                    resize: "none",
                                    minHeight: "100%",
                                    paddingLeft: 50,
                                }}
                                value={message}
                                placeholder={`Message @${sessionIdFocus}`}
                                onChange={(event) => {
                                    setMessage(event.target.value);
                                }}
                                onKeyDown={(event) => {
                                    if (
                                        _.isEqual(event.key, "Enter") &&
                                        !event.shiftKey
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
        </>
    );
}
