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
import SessionMemberStack from "@/components/sessions/SessionMemberStack";
import SessionMessages from "@/components/sessions/message/SessionMessages";
import Workspace from "@/components/sessions/message/workspace/Workspace";
import { AppToaster } from "@/components/toaster";
import {
    Alignment,
    Button,
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
    faCaretDown,
    faCircleA,
    faClipboard,
    faPlusLarge,
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
import { useRouter } from "next/router";
import { useContext, useEffect, useRef, useState } from "react";
export default function SessionMessagePage() {
    const router = useRouter();
    const { socket, reconnectWs, isSocketOpen } = useSocket();
    const { appState, appActions } = useContext(AppContext);
    const { sessionId } = router.query;
    const sessionDetails = _.get(
        appState,
        ["session", "sessionDetails", sessionId],
        {}
    );
    useEffect(() => {
        if (!router.isReady) return;
        axios
            .get(`/sessions/session/${sessionId}`)
            .then((response) => {
                appActions.session.setSessionDetails([
                    _.get(response, "data.result", {}),
                ]);
            })
            .catch(() => {});
        appActions.session.setSessionIdFocus(sessionId);
        return () => {
            appActions.session.setSessionIdFocus(null);
        };
    }, [router]);
    const { sessionAgentProgress, openAgentsDialogTrigger } = appState.session;
    const [message, setMessage] = useState("");
    const sessionMessageTextArea = useRef(null);
    const [isSessionDetailOpen, setIsSessionDetailOpen] = useState(false);
    const { settings } = useContext(AuthContext);
    const compactSidebar = _.get(settings, "compact_sidebar", false);
    const { authenticating } = useContext(SocketContext);
    const sendSessionMessage = (message) => {
        if (!isSocketOpen) return;
        setMessage("");
        sendSocketMessage(
            socket,
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: sessionId,
                message: message,
            })
        );
    };
    useEffect(() => {
        if (sessionMessageTextArea.current) {
            sessionMessageTextArea.current.focus();
        }
    }, []);
    const debugMode = _.get(settings, "debug_mode", false);
    // const initialFetchAll = useRef(true);
    useEffect(() => {
        if (!isSocketOpen) return;
        // if (initialFetchAll.current) {
        //     initialFetchAll.current = false;
        //     sendSocketMessage(
        //         socket,
        //         JSON.stringify({ type: "REQUEST_USER_AGENT_ID" })
        //     );
        // }
        appActions.session.observeSession({
            sessionId,
            socket,
        });
    }, [isSocketOpen]); // eslint-disable-line react-hooks/exhaustive-deps
    const [isAddAgentsOpen, setIsAddAgentsOpen] = useState(false);
    const [skippable, setSkippable] = useState(false);
    const sessionName = _.get(sessionDetails, "name", sessionId);
    const [sessionDisplayName, setSessionDisplayName] = useState(sessionName);
    useEffect(() => {
        if (_.isEqual(sessionId, sessionName)) {
            const utcSeconds = sessionDetails.created_date;
            let date = new Date(0); // The 0 here sets the date to the epoch
            date.setUTCSeconds(utcSeconds);
            setSessionDisplayName(date.toLocaleString());
        } else {
            setSessionDisplayName(sessionName);
        }
    }, [sessionName, sessionDetails, sessionId]);
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
    const progress = _.get(sessionAgentProgress, sessionId, {});
    if (!isSocketOpen)
        return (
            <NonIdealState
                icon={faIcon({ icon: faSignalStreamSlash, size: 50 })}
                title={
                    socket != null &&
                    _.isEqual(socket.readyState, WebSocket.CONNECTING)
                        ? "Connecting"
                        : "No connection"
                }
                action={
                    <Button
                        icon={faIcon({ icon: faSatelliteDish })}
                        onClick={reconnectWs}
                        intent={Intent.PRIMARY}
                        large
                        loading={
                            (!_.isNil(socket) &&
                                _.isEqual(
                                    socket.readyState,
                                    WebSocket.CONNECTING
                                )) ||
                            authenticating
                        }
                        text="Connect"
                    />
                }
            />
        );
    return (
        <>
            <div
                style={{
                    height: "calc(100% - 80px)",
                    width: `calc(100vw - ${
                        compactSidebar ? 80 : NAVIGATION_MENU_WIDTH
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
                    {debugMode && (
                        <Tooltip
                            content="Copy connection ID"
                            minimal
                            placement="bottom-start"
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
                    )}
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
                                    value: !appState.session.showWorkspacePanel,
                                })
                            }
                        />
                    </Tooltip>
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 30,
                            width: `calc(100% - 50px - ${
                                debugMode ? 90.13 : 0
                            }px)`,
                            justifyContent: "space-between",
                        }}
                    >
                        {!_.isNil(sessionId) ? (
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
                                                #&nbsp;{sessionDisplayName}
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
                        <SessionMemberStack sessionId={sessionId} />
                    </div>
                </Card>
                <div
                    style={{
                        height: "calc(100% - 131px)",
                        paddingTop: 1,
                        position: "relative",
                        paddingBottom: !_.isEmpty(progress) ? 31 : null,
                    }}
                >
                    <Allotment separator={appState.session.showWorkspacePanel}>
                        <Allotment.Pane
                            minSize={MIN_ALLOTMENT_PANE}
                            visible={appState.session.showWorkspacePanel}
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
                                            backgroundColor: "transparent",
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
                                                        !_.isEqual(e.value, 1)
                                                    }
                                                    intent={
                                                        _.isEqual(e.value, 1)
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
                                    />
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
                                    const trimmedMessage = _.trim(message);
                                    if (_.isEmpty(trimmedMessage)) return;
                                    sendSessionMessage(trimmedMessage);
                                    event.preventDefault();
                                }
                            }}
                        />
                    </ControlGroup>
                </div>
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
