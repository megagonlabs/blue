import { NAVIGATION_MENU_WIDTH } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { SocketContext } from "@/components/contexts/socket-context";
import { sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
import AddAgents from "@/components/sessions/AddAgents";
import PlanVisualizationPanel from "@/components/sessions/PlanVisualizationPanel";
import SessionDetail from "@/components/sessions/SessionDetail";
import SessionList from "@/components/sessions/SessionList";
import SessionMessages from "@/components/sessions/message/SessionMessages";
import { AppToaster } from "@/components/toaster";
import {
    Alignment,
    Button,
    ButtonGroup,
    Card,
    Classes,
    ControlGroup,
    H4,
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
    faBell,
    faCaretDown,
    faChevronLeft,
    faChevronRight,
    faCircleA,
    faClipboard,
    faInboxIn,
    faMessages,
    faPlusLarge,
    faRefresh,
    faSatelliteDish,
    faSignalStreamSlash,
} from "@fortawesome/pro-duotone-svg-icons";
import { ReactFlowProvider } from "@xyflow/react";
import axios from "axios";
import classNames from "classnames";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const { unreadSessionIds, sessionIdFocus, sessionIds, collapsed } =
        appState.session;
    const [message, setMessage] = useState("");
    const sessionMessageTextArea = useRef(null);
    const [isSessionDetailOpen, setIsSessionDetailOpen] = useState(false);
    const { socket, reconnectWs, isSocketOpen } = useSocket();
    const { settings } = useContext(AuthContext);
    const { authenticating } = useContext(SocketContext);
    const sendSessionMessage = (message) => {
        if (!isSocketOpen) return;
        setMessage("");
        sendSocketMessage(
            socket,
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: sessionIdFocus,
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
                        value: data.connection_id,
                    });
                } else if (_.isEqual(data["type"], "NEW_SESSION_BROADCAST")) {
                    appActions.session.addSession(_.get(data, "session.id"));
                    appActions.session.setSessionDetails([data["session"]]);
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
    // const SESSION_LIST_PANEL_WIDTH = 327.92;
    const SESSION_LIST_PANEL_WIDTH = 327.92;
    const initialFetchAll = useRef(true);
    const [loading, setLoading] = useState(false);
    const fetchAllSessions = () => {
        // automatically fetch all existing sessions onload
        setLoading(true);
        axios
            .get("/sessions")
            .then((response) => {
                let sessions = _.get(response, "data.results", []);
                appActions.session.setSessionDetails(sessions);
                for (let i = 0; i < sessions.length; i++) {
                    const sessionId = sessions[i].id;
                    appActions.session.addSession(sessionId);
                }
                setLoading(false);
            })
            .catch(() => {});
    };
    useEffect(() => {
        if (!isSocketOpen) return;
        if (initialFetchAll.current) {
            initialFetchAll.current = false;
            sendSocketMessage(
                socket,
                JSON.stringify({ type: "REQUEST_USER_AGENT_ID" })
            );
            fetchAllSessions();
        }
    }, [isSocketOpen]);
    const ReconnectButton = () => {
        return (
            <Button
                icon={faIcon({ icon: faSatelliteDish })}
                onClick={reconnectWs}
                intent={Intent.PRIMARY}
                large
                loading={
                    (socket != null &&
                        _.isEqual(socket.readyState, WebSocket.CONNECTING)) ||
                    authenticating
                }
                text="Connect"
            />
        );
    };
    const [isAddAgentsOpen, setIsAddAgentsOpen] = useState(false);
    const [skippable, setSkippable] = useState(false);
    const sessionDetails = _.get(
        appState,
        ["session", "sessionDetails", sessionIdFocus],
        {}
    );
    const sessionName = _.get(sessionDetails, "name", sessionIdFocus);
    const sessionDescription = _.get(sessionDetails, "description", "");
    useEffect(() => {
        if (appState.session.openAgentsDialogTrigger) {
            setIsAddAgentsOpen(true);
            setSkippable(true);
            appActions.session.setState({
                key: "openAgentsDialogTrigger",
                value: false,
            });
        }
    }, [appState.session.openAgentsDialogTrigger]);
    if (!isSocketOpen && _.isEmpty(sessionIds))
        return (
            <NonIdealState
                icon={faIcon({ icon: faSignalStreamSlash, size: 50 })}
                title={
                    socket != null &&
                    _.isEqual(socket.readyState, WebSocket.CONNECTING)
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
                    width: collapsed ? 80 : SESSION_LIST_PANEL_WIDTH,
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
                            content={collapsed ? "Expand" : "Collapse"}
                            placement={`bottom${collapsed ? "" : "-start"}`}
                            minimal
                        >
                            <Button
                                outlined
                                onClick={() =>
                                    appActions.session.setState({
                                        key: "collapsed",
                                        value: !collapsed,
                                    })
                                }
                                icon={faIcon({
                                    icon: collapsed
                                        ? faChevronRight
                                        : faChevronLeft,
                                })}
                            />
                        </Tooltip>
                        {!collapsed ? (
                            <Tooltip
                                content="Refresh"
                                placement="bottom"
                                minimal
                            >
                                <Button
                                    outlined
                                    loading={loading}
                                    onClick={fetchAllSessions}
                                    icon={faIcon({ icon: faRefresh })}
                                />
                            </Tooltip>
                        ) : null}
                    </ButtonGroup>
                    {!collapsed ? (
                        !isSocketOpen ? (
                            <ReconnectButton />
                        ) : _.get(settings, "debug_mode", false) ? (
                            <Tooltip
                                content="Copy connection ID"
                                minimal
                                placement="bottom-end"
                            >
                                <Tag
                                    minimal
                                    large
                                    interactive
                                    onClick={() => {
                                        copy(appState.session.connectionId);
                                        AppToaster.show({
                                            icon: faIcon({ icon: faClipboard }),
                                            message: `Copied "${appState.session.connectionId}"`,
                                        });
                                    }}
                                >
                                    {appState.session.connectionId}
                                </Tag>
                            </Tooltip>
                        ) : null
                    ) : null}
                </div>
                {!collapsed ? (
                    _.isEmpty(appState.session.sessionIds) ? (
                        <Card
                            style={{
                                padding: 0,
                                marginTop: 1,
                                height: "calc(100% - 80px)",
                                width: "calc(100% - 1px)",
                                borderRadius: 0,
                            }}
                        >
                            <NonIdealState
                                icon={faIcon({ icon: faInboxIn, size: 50 })}
                                title="Sessions"
                            />
                        </Card>
                    ) : (
                        <div className="full-parent-height">
                            <div
                                className="bp-border-top bp-border-right"
                                style={{
                                    padding: "5px 20px",
                                    borderRadius: 0,
                                }}
                            >
                                <ButtonGroup fill minimal>
                                    <Button
                                        text="All"
                                        onClick={() => {
                                            appActions.session.setState({
                                                key: "sessionGroupBy",
                                                value: "all",
                                            });
                                        }}
                                        active={_.isEqual(
                                            appState.session.sessionGroupBy,
                                            "all"
                                        )}
                                    />
                                    <Button
                                        text="Pinned"
                                        onClick={() => {
                                            appActions.session.setState({
                                                key: "sessionGroupBy",
                                                value: "pinned",
                                            });
                                        }}
                                        active={_.isEqual(
                                            appState.session.sessionGroupBy,
                                            "pinned"
                                        )}
                                    />
                                    <Button
                                        text="Owner"
                                        onClick={() => {
                                            appActions.session.setState({
                                                key: "sessionGroupBy",
                                                value: "owner",
                                            });
                                        }}
                                        active={_.isEqual(
                                            appState.session.sessionGroupBy,
                                            "owner"
                                        )}
                                    />
                                    <Button
                                        text="Member"
                                        onClick={() => {
                                            appActions.session.setState({
                                                key: "sessionGroupBy",
                                                value: "member",
                                            });
                                        }}
                                        active={_.isEqual(
                                            appState.session.sessionGroupBy,
                                            "member"
                                        )}
                                    />
                                </ButtonGroup>
                            </div>
                            <SessionList />
                        </div>
                    )
                ) : (
                    <div
                        className="full-parent-height bp-border-right"
                        style={{ padding: 20 }}
                    >
                        {!_.isEmpty(unreadSessionIds) ? (
                            <Tooltip
                                content={`${_.size(
                                    unreadSessionIds
                                )} unread session${
                                    _.size(unreadSessionIds) > 1 ? "s" : ""
                                }`}
                            >
                                <Button
                                    large
                                    minimal
                                    icon={faIcon({ icon: faBell })}
                                />
                            </Tooltip>
                        ) : null}
                    </div>
                )}
            </div>
            <div
                style={{
                    height: "calc(100% - 80px)",
                    marginLeft: collapsed ? 80 : SESSION_LIST_PANEL_WIDTH,
                    width: `calc(100vw - ${
                        (collapsed ? 80 : SESSION_LIST_PANEL_WIDTH) +
                        NAVIGATION_MENU_WIDTH
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
                        position: "relative",
                        zIndex: 1,
                    }}
                >
                    {!_.isNull(sessionIdFocus) ? (
                        <div style={{ maxWidth: "50%" }}>
                            <Tooltip
                                openOnTargetFocus={false}
                                minimal
                                className="full-parent-width"
                                content="Get session details"
                                placement="bottom-start"
                            >
                                <Button
                                    fill
                                    ellipsizeText
                                    minimal
                                    alignText={Alignment.LEFT}
                                    onClick={() => setIsSessionDetailOpen(true)}
                                    rightIcon={faIcon({ icon: faCaretDown })}
                                    text={
                                        <H4
                                            className={classNames(
                                                "margin-0",
                                                Classes.TEXT_OVERFLOW_ELLIPSIS
                                            )}
                                        >
                                            #&nbsp;{sessionName}
                                        </H4>
                                    }
                                />
                            </Tooltip>
                            <div
                                className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                                style={{ paddingLeft: 10, width: "100%" }}
                            >
                                {sessionDescription}
                            </div>
                        </div>
                    ) : null}
                    <Popover
                        placement="bottom-end"
                        content={<div style={{ padding: 20 }}></div>}
                    ></Popover>
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
                            className="bp-border-top"
                            style={{
                                padding: 20,
                                position: "relative",
                                height: 131,
                            }}
                        >
                            <ControlGroup fill style={{ height: "100%" }}>
                                <Popover
                                    minimal
                                    placement="top-start"
                                    targetProps={{ style: { maxWidth: 40 } }}
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
                                        style={{ maxWidth: 40, height: 91 }}
                                        icon={faIcon({ icon: faPlusLarge })}
                                    />
                                </Popover>
                                <TextArea
                                    disabled={!isSocketOpen}
                                    inputRef={sessionMessageTextArea}
                                    style={{ resize: "none", height: 91 }}
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
                                />
                            </ControlGroup>
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
            <ReactFlowProvider>
                <PlanVisualizationPanel />
            </ReactFlowProvider>
        </>
    );
}
