import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import { useSocketStore } from "@/stores/socket-store";
import {
    Button,
    ButtonVariant,
    Colors,
    Intent,
    Menu,
    MenuItem,
    Overlay2,
    Popover,
    ProgressBar,
    Size,
    Tag,
    TextArea,
} from "@blueprintjs/core";
import { faCircleA, faPlus } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { Allotment } from "allotment";
import _ from "lodash";
import { createRef, useEffect, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { MIN_ALLOTMENT_PANE_SIZE } from "../constants";
import { useGridContainerContext } from "../contexts/GridContainerContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import { useContainerDimensions } from "../hooks/useContainerDimensions";
import AddSessionAgent from "./AddSessionAgent";
import SessionDetails from "./SessionDetails";
import SessionMessages from "./SessionMessages";
import Workspace from "./Workspace";
function SessionContainer({ width, height, sessionId }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const [userMessage, setUserMessage] = useState("");
    const {
        sessions,
        triggers,
        resetTrigger,
        progress,
        removeSessionProgress,
    } = useSessionStore(
        useShallow((state) => ({
            sessions: state.sessions,
            triggers: state.triggers,
            resetTrigger: state.resetTrigger,
            progress: state.progress,
            removeSessionProgress: state.removeSessionProgress,
        }))
    );
    const sessionProgress = _.get(progress, sessionId, {});
    const { sendMessage, observeSession } = useSocketStore(
        useShallow((state) => ({
            sendMessage: state.sendMessage,
            observeSession: state.observeSession,
        }))
    );
    const details = _.get(sessions, [sessionId, "details"], {});
    const sessionName = _.get(details, "name", sessionId);
    const { gridContainerId } = useGridContainerContext();
    const removeContainer = useGridStore((state) => state.removeContainer);
    const displayName = useMemo(() => {
        if (_.isEqual(sessionId, sessionName)) {
            const utcSeconds = _.get(details, "created_date");
            let date = new Date(0);
            date.setUTCSeconds(utcSeconds);
            return date.toLocaleString();
        }
        return sessionName;
    }, [details]);
    useEffect(() => {
        observeSession(sessionId);
    }, []);
    useEffect(() => {
        if (!_.has(sessions, sessionId)) {
            removeContainer(gridContainerId);
        }
    }, [sessions, gridContainerId, removeContainer]);
    const sendSessionMessage = () => {
        const trimmedUserMessage = _.trim(userMessage);
        if (_.isEmpty(trimmedUserMessage)) return;
        sendMessage(
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: sessionId,
                message: trimmedUserMessage,
            })
        );
        setUserMessage("");
    };
    const controGroupRef = createRef();
    const { height: controlGroupHeight } =
        useContainerDimensions(controGroupRef);
    const { showWorkspace: defaultShowWorkspace } = useAppStore(
        useShallow((state) => ({ showWorkspace: state.show_workspace }))
    );
    const [showWorkspace, setShowWorkspace] = useState(defaultShowWorkspace);
    const [showDetails, setShowDetails] = useState(false);
    const [showAddSessionAgent, setShowAddSessionAgent] = useState(false);
    const [skippable, setSkippable] = useState(false);
    useEffect(() => {
        if (_.get(triggers, ["addSessionAgent", sessionId], false)) {
            setSkippable(true);
            setShowAddSessionAgent(true);
        }
    }, [triggers, sessionId]);
    useEffect(() => {
        if (!showAddSessionAgent) {
            resetTrigger(["addSessionAgent", sessionId]);
        }
    }, [showAddSessionAgent]);
    return (
        <div style={{ width, height }}>
            <div
                className="full-parent-dimension"
                style={{
                    position: "relative",
                    overflowY: "auto",
                    backgroundColor: darkMode ? Colors.BLACK : null,
                }}
            >
                <Overlay2
                    onClose={() => {
                        setShowAddSessionAgent(false);
                        setSkippable(false);
                    }}
                    isOpen={showAddSessionAgent}
                    usePortal={false}
                    enforceFocus={false}
                    transitionDuration={0}
                >
                    <div
                        className="custom-card center-center"
                        style={{
                            width: 650,
                            padding: 20,
                            height: "calc(100% - 40px)",
                            maxWidth: "calc(100% - 40px)",
                        }}
                    >
                        <AddSessionAgent
                            setShowAddSessionAgent={setShowAddSessionAgent}
                            setSkippable={setSkippable}
                            skippable={skippable}
                            sessionId={sessionId}
                        />
                    </div>
                </Overlay2>
                <Overlay2
                    onClose={() => {
                        setShowDetails(false);
                    }}
                    isOpen={showDetails}
                    usePortal={false}
                    enforceFocus={false}
                    transitionDuration={0}
                >
                    <div
                        className="custom-card center-center"
                        style={{
                            width: 650,
                            height: "calc(100% - 40px)",
                            maxWidth: "calc(100% - 40px)",
                        }}
                    >
                        <SessionDetails sessionId={sessionId} />
                    </div>
                </Overlay2>
                <div style={{ height: `calc(100% - ${controlGroupHeight}px)` }}>
                    <div
                        className="full-parent-dimension"
                        style={{
                            maxHeight: !_.isEmpty(sessionProgress)
                                ? "calc(100% - 31px)"
                                : null,
                        }}
                    >
                        <Allotment separator={showWorkspace}>
                            <Allotment.Pane
                                visible={showWorkspace}
                                minSize={MIN_ALLOTMENT_PANE_SIZE}
                            >
                                <Workspace sessionId={sessionId} />
                            </Allotment.Pane>
                            <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                                <SessionMessages
                                    setShowDetails={setShowDetails}
                                    sessionId={sessionId}
                                    showWorkspace={showWorkspace}
                                    setShowWorkspace={setShowWorkspace}
                                />
                            </Allotment.Pane>
                        </Allotment>
                    </div>
                    {!_.isEmpty(sessionProgress) && (
                        <div
                            className="border-top"
                            style={{
                                height: 31,
                                padding: "5px 20px 5px 10px",
                                overflowX: "hidden",
                                overscrollBehavior: "contain",
                                whiteSpace: "nowrap",
                            }}
                        >
                            {_.keys(sessionProgress).map((progressId) => {
                                const e = sessionProgress[progressId];
                                return (
                                    <Tag
                                        key={progressId}
                                        onClick={() => {
                                            removeSessionProgress(
                                                sessionId,
                                                progressId
                                            );
                                        }}
                                        className="no-text-selection"
                                        interactive
                                        minimal
                                        id={progressId}
                                        style={{
                                            marginLeft: 10,
                                            backgroundColor: "transparent",
                                        }}
                                        endIcon={
                                            <div style={{ width: 40 }}>
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
                    className="border-top full-parent-width"
                    ref={controGroupRef}
                    style={{ position: "fixed", bottom: 0, padding: 20 }}
                >
                    <div style={{ position: "relative" }}>
                        <div
                            style={{ position: "absolute", left: 10, top: 10 }}
                        >
                            <Popover
                                minimal
                                placement="top-start"
                                targetProps={{ style: { maxWidth: 40 } }}
                                content={
                                    <Menu size={Size.LARGE}>
                                        <MenuItem
                                            onClick={() => {
                                                setShowAddSessionAgent(true);
                                            }}
                                            icon={<FAIcon icon={faCircleA} />}
                                            text="Agents"
                                        />
                                    </Menu>
                                }
                            >
                                <Button
                                    size={Size.LARGE}
                                    variant={ButtonVariant.MINIMAL}
                                    icon={<FAIcon icon={faPlus} />}
                                />
                            </Popover>
                        </div>
                        <TextArea
                            fill
                            autoResize
                            autoFocus
                            style={{
                                resize: "none",
                                maxHeight: 74,
                                minHeight: 60,
                                paddingLeft: 60,
                            }}
                            value={userMessage}
                            placeholder={`Message # ${displayName}`}
                            onChange={(event) =>
                                setUserMessage(event.target.value)
                            }
                            onKeyDown={(event) => {
                                if (
                                    _.isEqual(event.key, "Enter") &&
                                    !event.shiftKey
                                ) {
                                    sendSessionMessage();
                                    event.preventDefault();
                                }
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(SessionContainer);
