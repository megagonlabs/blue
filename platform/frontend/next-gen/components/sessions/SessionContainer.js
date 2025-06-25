import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import { useSocketStore } from "@/stores/socket-store";
import {
    Button,
    ButtonVariant,
    Colors,
    Menu,
    MenuItem,
    Overlay2,
    Popover,
    Size,
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
import { useRefDimensions } from "../hooks/useRefDimensions";
import AddSessionAgent from "./AddSessionAgent";
import SessionDetails from "./SessionDetails";
import SessionMessages from "./SessionMessages";
import Workspace from "./Workspace";
function SessionContainer({ width, height, sessionId }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const [userMessage, setUserMessage] = useState("");
    const { sessions, triggers, resetTrigger } = useSessionStore(
        useShallow((state) => ({
            sessions: state.sessions,
            triggers: state.triggers,
            resetTrigger: state.resetTrigger,
        }))
    );
    const sendMessage = useSocketStore((state) => state.sendMessage);
    const observeSession = useSocketStore((state) => state.observeSession);
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
    const { height: controlGroupHeight } = useRefDimensions(controGroupRef);
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
                        resetTrigger(["addSessionAgent", sessionId]);
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
