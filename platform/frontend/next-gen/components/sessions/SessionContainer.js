import { useAppStore } from "@/stores/app-store";
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
import { MIN_ALLOTMENT_PANE_SIZE } from "../constants";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import { useRefDimensions } from "../hooks/useRefDimensions";
import SessionDetails from "./SessionDetails";
import SessionMessages from "./SessionMessages";
import Workspace from "./Workspace";
function SessionContainer({ width, height, sessionId }) {
    const darkMode = useAppStore((state) => state.darkMode);
    const [userMessage, setUserMessage] = useState("");
    const sessions = useSessionStore((state) => state.sessions);
    const sendMessage = useSocketStore((state) => state.sendMessage);
    const observeSession = useSocketStore((state) => state.observeSession);
    const details = _.get(sessions, [sessionId, "details"], {});
    const sessionName = _.get(details, "name", sessionId);
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
    const [showWorkspace, setShowWorkspace] = useState(false);
    const [showDetails, setShowDetails] = useState(false);
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
                    onClose={() => setShowDetails(false)}
                    isOpen={showDetails}
                    usePortal={false}
                    transitionDuration={0}
                >
                    <div
                        className="custom-card center-center"
                        style={{
                            width: 500,
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
                                            icon={
                                                <FAIcon
                                                    icon={faCircleA}
                                                    style={{ marginRight: 5 }}
                                                />
                                            }
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
