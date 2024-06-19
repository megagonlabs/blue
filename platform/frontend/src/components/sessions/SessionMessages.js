import { AppContext } from "@/components/contexts/app-context";
import InteractiveMessage from "@/components/sessions/InteractiveMessage";
import { Callout, Classes, Colors, Intent, Tooltip } from "@blueprintjs/core";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import MessageMetadata from "./MessageMetadata";
export default function SessionMessages() {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus];
    function getRowHeight(index) {
        const own = _.includes(
            _.get(messages, [index, "stream"]),
            `USER:${appState.session.connectionId}`
        );
        return rowHeights.current[index] + 20 || 51 + (!own ? 15.43 : 0);
    }
    function setRowHeight(index, size, shouldForceUpdate = true) {
        variableSizeListRef.current.resetAfterIndex(0, shouldForceUpdate);
        rowHeights.current = { ...rowHeights.current, [index]: size };
    }
    function Row({ index, style }) {
        const rowRef = useRef({});
        const own = _.includes(
            _.get(messages, [index, "stream"]),
            `USER:${appState.session.connectionId}`
        );
        useEffect(() => {
            if (rowRef.current) {
                setRowHeight(
                    index,
                    rowRef.current.clientHeight + 30 + (!own ? 20.43 : 0)
                );
            }
        }, [rowRef]);
        useEffect(() => {
            const handleResize = () => {
                // do magic for resize
                if (rowRef.current) {
                    setRowHeight(
                        index,
                        rowRef.current.clientHeight + 30 + (!own ? 20.43 : 0),
                        false
                    );
                }
            };
            window.addEventListener("resize", handleResize);
            return () => {
                window.removeEventListener("resize", handleResize);
            };
        }, []);
        const messageLabel = _.get(messages[index].message, "label", "STRING"),
            messageContent = _.get(messages[index].message, "content", null);
        const [hasError, setHasError] = useState(false);
        const timestamp = messages[index].timestamp;
        const stream = messages[index].stream;
        const [showActions, setShowActions] = useState(false);
        return (
            <div
                key={`session-message-${index}`}
                onMouseEnter={() => {
                    setShowActions(true);
                }}
                onMouseLeave={() => {
                    setShowActions(false);
                }}
                style={{
                    ...style,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    padding: "10px 20px",
                    marginTop: 10,
                    backgroundColor: showActions ? Colors.LIGHT_GRAY5 : null,
                }}
            >
                <Callout
                    intent={
                        hasError ? Intent.DANGER : own ? Intent.PRIMARY : null
                    }
                    icon={null}
                    style={{
                        position: "relative",
                        maxWidth: "min(802.2px, 100%)",
                        minWidth: 50,
                        width: "fit-content",
                    }}
                >
                    <div
                        style={{
                            position: "absolute",
                            left: 0,
                            top: -10,
                            display: showActions ? null : "none",
                        }}
                    >
                        {/* <ButtonGroup large>
                            <Tooltip
                                content="Pin to this session"
                                minimal
                                placement="bottom-start"
                            >
                                <Button icon={faIcon({ icon: faThumbtack })} />
                            </Tooltip>
                        </ButtonGroup> */}
                    </div>
                    <div
                        ref={rowRef}
                        style={{
                            maxWidth: "min(802.2px, 100%)",
                            minWidth: 50,
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-all",
                            width: "fit-content",
                            overflow: "hidden",
                        }}
                    >
                        {_.isEqual(messageLabel, "TEXT") ? (
                            messageContent
                        ) : _.isEqual(messageLabel, "JSON") ? (
                            <pre
                                className="margin-0"
                                style={{ overflowX: "auto" }}
                            >
                                {JSON.stringify(messageContent, null, 4)}
                            </pre>
                        ) : _.isEqual(messageLabel, "INTERACTION") ? (
                            <InteractiveMessage
                                stream={stream}
                                setHasError={setHasError}
                                content={messageContent}
                            />
                        ) : null}
                    </div>
                </Callout>
                {!own ? (
                    <div
                        style={{ maxWidth: "100%", marginTop: 5 }}
                        className={`${Classes.TEXT_DISABLED} ${Classes.TEXT_SMALL} ${Classes.TEXT_OVERFLOW_ELLIPSIS}`}
                    >
                        <Tooltip
                            targetProps={{ className: "full-parent-width" }}
                            minimal
                            placement="bottom-start"
                            content={
                                <MessageMetadata
                                    timestamp={timestamp}
                                    stream={stream}
                                />
                            }
                        >
                            {stream}
                        </Tooltip>
                    </div>
                ) : null}
            </div>
        );
    }
    useEffect(() => {
        setTimeout(() => {
            if (variableSizeListRef.current) {
                variableSizeListRef.current.scrollToItem(
                    messages.length,
                    "end"
                );
            }
        }, 0);
    }, [variableSizeListRef, sessionIdFocus]);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <VariableSizeList
                    height={height}
                    itemCount={messages.length}
                    itemSize={getRowHeight}
                    ref={variableSizeListRef}
                    width={width}
                >
                    {Row}
                </VariableSizeList>
            )}
        </AutoSizer>
    );
}
