import { AppContext } from "@/components/contexts/app-context";
import InteractiveMessage from "@/components/sessions/InteractiveMessage";
import { Callout, Classes, Intent } from "@blueprintjs/core";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
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
        return (
            rowHeights.current[index] +
                (_.isEqual(index, messages.length - 1) ? 20 : 10) +
                (_.isEqual(index, 0) ? 20 : 0) || 51 + (!own ? 15.43 : 0)
        );
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
                    rowRef.current.clientHeight + 30 + (!own ? 15.43 : 0)
                );
            }
        }, [rowRef]); // eslint-disable-line react-hooks/exhaustive-deps
        useEffect(() => {
            const handleResize = () => {
                // do magic for resize
                if (rowRef.current) {
                    setRowHeight(
                        index,
                        rowRef.current.clientHeight + 30 + (!own ? 15.43 : 0),
                        false
                    );
                }
            };
            window.addEventListener("resize", handleResize);
            return () => {
                window.removeEventListener("resize", handleResize);
            };
        }, []); // eslint-disable-line react-hooks/exhaustive-deps
        const messageType = _.get(messages[index].message, "type", "STRING"),
            messageContent = _.get(messages[index].message, "content", null);
        const [hasError, setHasError] = useState(false);
        return (
            <div
                style={{
                    ...style,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: `flex-${own ? "end" : "start"}`,
                    padding: `${_.isEqual(index, 0) ? 20 : 0}px 20px ${
                        _.isEqual(index, messages.length - 1) ? 20 : 10
                    }px`,
                }}
            >
                <Callout
                    intent={
                        hasError ? Intent.DANGER : own ? Intent.PRIMARY : null
                    }
                    icon={null}
                    style={{
                        backgroundColor: "rgba(143, 153, 168, 0.1)",
                        maxWidth: "min(802.2px, 100%)",
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-all",
                        width: "fit-content",
                        overflow: "hidden",
                    }}
                >
                    <div ref={rowRef}>
                        {_.isEqual(messageType, "STRING") ? (
                            messageContent
                        ) : _.isEqual(messageType, "INTERACTION") ? (
                            <InteractiveMessage
                                stream={messages[index].stream}
                                setHasError={setHasError}
                                content={messageContent}
                            />
                        ) : null}
                    </div>
                </Callout>
                {!own ? (
                    <div
                        style={{ maxWidth: "100%" }}
                        className={`${Classes.TEXT_DISABLED} ${Classes.TEXT_SMALL} ${Classes.TEXT_OVERFLOW_ELLIPSIS}`}
                    >
                        {messages[index].stream}
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
    }, [variableSizeListRef, sessionIdFocus]); // eslint-disable-line react-hooks/exhaustive-deps
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
