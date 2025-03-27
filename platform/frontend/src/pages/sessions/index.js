import {
    MIN_ALLOTMENT_PANE,
    NAVIGATION_MENU_WIDTH,
} from "@/components/constant";
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
import SessionMemberStack from "@/components/sessions/SessionMemberStack";
import SessionMessages from "@/components/sessions/message/SessionMessages";
import Workspace from "@/components/sessions/message/workspace/Workspace";
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
    ProgressBar,
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
    faTableColumns,
    faTableLayout,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { ReactFlowProvider } from "@xyflow/react";
import { Allotment } from "allotment";
import axios from "axios";
import classNames from "classnames";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const {
        unreadSessionIds,
        sessionIdFocus,
        sessionIds,
        sessionListPanelCollapsed,
        sessionAgentProgress,
        openAgentsDialogTrigger,
    } = appState.session;
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
    useEffect(() => {
        if (sessionMessageTextArea.current) {
            sessionMessageTextArea.current.focus();
        }
    }, [sessionIdFocus]);
    const SESSION_LIST_PANEL_WIDTH = 327.92;
    const initialFetchAll = useRef(true);
    const [loading, setLoading] = useState(false);
    const fetchMySessions = () => {
        setLoading(true);
        axios
            .get("/sessions", { params: { my_sessions: true } })
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
            fetchMySessions();
        }
    }, [isSocketOpen]); // eslint-disable-line react-hooks/exhaustive-deps
    const ReconnectButton = () => {
        return (
            <Button
                icon={faIcon({ icon: faSatelliteDish })}
                onClick={reconnectWs}
                intent={Intent.PRIMARY}
                large
                loading={
                    (!_.isNil(socket) &&
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
        if (openAgentsDialogTrigger) {
            setIsAddAgentsOpen(true);
            setSkippable(true);
        }
        appActions.session.setState({
            key: "openAgentsDialogTrigger",
            value: false,
        });
    }, [openAgentsDialogTrigger]); // eslint-disable-line react-hooks/exhaustive-deps
    const progress = _.get(sessionAgentProgress, sessionIdFocus, {});
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
                    width: sessionListPanelCollapsed
                        ? 80
                        : SESSION_LIST_PANEL_WIDTH,
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
                            content={
                                sessionListPanelCollapsed
                                    ? "Expand"
                                    : "Collapse"
                            }
                            placement={
                                sessionListPanelCollapsed
                                    ? "right"
                                    : "bottom-start"
                            }
                            minimal
                        >
                            <Button
                                outlined
                                onClick={() =>
                                    appActions.session.setState({
                                        key: "sessionListPanelCollapsed",
                                        value: !sessionListPanelCollapsed,
                                    })
                                }
                                icon={faIcon({
                                    icon: sessionListPanelCollapsed
                                        ? faChevronRight
                                        : faChevronLeft,
                                })}
                            />
                        </Tooltip>
                        {!sessionListPanelCollapsed ? (
                            <Tooltip
                                content="Refresh"
                                placement="bottom"
                                minimal
                            >
                                <Button
                                    outlined
                                    loading={loading}
                                    onClick={fetchMySessions}
                                    icon={faIcon({ icon: faRefresh })}
                                />
                            </Tooltip>
                        ) : null}
                    </ButtonGroup>
                    {!sessionListPanelCollapsed ? (
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
                {!sessionListPanelCollapsed ? (
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
                                className="border-top border-right"
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
                        className="full-parent-height border-right"
                        style={{ padding: 20 }}
                    >
                        {!isSocketOpen ? (
                            <div style={{ marginBottom: 10 }}>
                                <Tooltip
                                    minimal
                                    placement="right"
                                    content="Connect"
                                >
                                    <Button
                                        loading={
                                            (socket != null &&
                                                _.isEqual(
                                                    socket.readyState,
                                                    WebSocket.CONNECTING
                                                )) ||
                                            authenticating
                                        }
                                        onClick={reconnectWs}
                                        icon={faIcon({ icon: faSatelliteDish })}
                                        large
                                        intent={Intent.PRIMARY}
                                    />
                                </Tooltip>
                            </div>
                        ) : null}
                        {!_.isEmpty(unreadSessionIds) ? (
                            <Tooltip
                                minimal
                                placement="right"
                                content={`${_.size(
                                    unreadSessionIds
                                )} unread session${
                                    _.size(unreadSessionIds) > 1 ? "s" : ""
                                }`}
                            >
                                <Button
                                    style={{ cursor: "initial" }}
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
                    marginLeft: sessionListPanelCollapsed
                        ? 80
                        : SESSION_LIST_PANEL_WIDTH,
                    width: `calc(100vw - ${
                        (sessionListPanelCollapsed
                            ? 80
                            : SESSION_LIST_PANEL_WIDTH) + NAVIGATION_MENU_WIDTH
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
                        padding: "0px 20px",
                        zIndex: 1,
                        gap: 10,
                    }}
                >
                    {!_.isNil(sessionIdFocus) ? (
                        <Tooltip
                            content={`${
                                appState.session.showWorkspacePanel
                                    ? "Hide"
                                    : "Show"
                            } workspace`}
                            minimal
                            placement="bottom-start"
                        >
                            <Button
                                large
                                minimal
                                outlined
                                icon={faIcon({
                                    icon: !appState.session.showWorkspacePanel
                                        ? faTableColumns
                                        : faTableLayout,
                                })}
                                onClick={() =>
                                    appActions.session.setState({
                                        key: "showWorkspacePanel",
                                        value: !appState.session
                                            .showWorkspacePanel,
                                    })
                                }
                            />
                        </Tooltip>
                    ) : null}
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 30,
                            width: "calc(100% - 50px)",
                            justifyContent: "space-between",
                        }}
                    >
                        {!_.isNil(sessionIdFocus) ? (
                            <div
                                style={{
                                    maxWidth: "calc(100% - 175px)",
                                }}
                            >
                                <Tooltip
                                    openOnTargetFocus={false}
                                    minimal
                                    className="full-parent-width"
                                    content="Get session details"
                                    placement="bottom-start"
                                >
                                    <Button
                                        large={_.isEmpty(sessionDescription)}
                                        style={{ maxWidth: "100%" }}
                                        ellipsizeText
                                        minimal
                                        alignText={Alignment.LEFT}
                                        onClick={() =>
                                            setIsSessionDetailOpen(true)
                                        }
                                        rightIcon={faIcon({
                                            icon: faCaretDown,
                                        })}
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
                                {!_.isEmpty(sessionDescription) ? (
                                    <div
                                        className={
                                            Classes.TEXT_OVERFLOW_ELLIPSIS
                                        }
                                        style={{
                                            paddingLeft: 10,
                                            lineHeight: "25px",
                                            width: "100%",
                                        }}
                                    >
                                        {sessionDescription}
                                    </div>
                                ) : null}
                            </div>
                        ) : null}
                        <SessionMemberStack sessionId={sessionIdFocus} />
                    </div>
                </Card>
                {_.isNil(sessionIdFocus) ? (
                    <NonIdealState
                        icon={faIcon({ icon: faMessages, size: 50 })}
                        title="Messages"
                    />
                ) : (
                    <>
                        <div
                            style={{
                                height: "calc(100% - 131px)",
                                paddingTop: 1,
                                position: "relative",
                                paddingBottom: !_.isEmpty(progress) ? 31 : null,
                            }}
                        >
                            <Allotment
                                separator={appState.session.showWorkspacePanel}
                            >
                                <Allotment.Pane
                                    minSize={MIN_ALLOTMENT_PANE}
                                    visible={
                                        appState.session.showWorkspacePanel
                                    }
                                >
                                    <Workspace />
                                </Allotment.Pane>
                                <Allotment.Pane minSize={MIN_ALLOTMENT_PANE}>
                                    <SessionMessages />
                                </Allotment.Pane>
                            </Allotment>
                            {!_.isEmpty(progress) && (
                                <div
                                    className="border-top"
                                    style={{
                                        width: "100%",
                                        padding: "5px 20px 5px 10px",
                                        position: "absolute",
                                        left: 0,
                                        bottom: 0,
                                        overflowX: "hidden",
                                        overscrollBehavior: "contain",
                                        whiteSpace: "nowrap",
                                    }}
                                >
                                    {_.keys(progress).map((progress_id) => {
                                        const e = progress[progress_id];
                                        return (
                                            <Tag
                                                className="no-text-selection"
                                                onClick={() =>
                                                    appActions.session.removeProgress(
                                                        progress_id
                                                    )
                                                }
                                                interactive
                                                key={progress_id}
                                                style={{
                                                    marginLeft: 10,
                                                    backgroundColor:
                                                        "transparent",
                                                }}
                                                minimal
                                                id={progress_id}
                                                rightIcon={
                                                    <div
                                                        style={{
                                                            width: 40,
                                                        }}
                                                    >
                                                        <ProgressBar
                                                            stripes={
                                                                !_.isEqual(
                                                                    e.value,
                                                                    1
                                                                )
                                                            }
                                                            intent={
                                                                _.isEqual(
                                                                    e.value,
                                                                    1
                                                                )
                                                                    ? Intent.SUCCESS
                                                                    : null
                                                            }
                                                            value={e.value}
                                                        />
                                                    </div>
                                                }
                                            >
                                                {e.label}
                                            </Tag>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                        <div
                            className="border-top"
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
                                    id="session-message-text-area"
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
                                            const trimmedMessage =
                                                _.trim(message);
                                            if (_.isEmpty(trimmedMessage))
                                                return;
                                            sendSessionMessage(trimmedMessage);
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
