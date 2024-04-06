import { AppContext } from "@/components/app-context";
import { Callout, Classes, Intent } from "@blueprintjs/core";
import _ from "lodash";
import { useContext, useEffect, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import InteractiveMessage from "./InteractiveMessage";
export default function SessionMessages() {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus];
    function getRowHeight(index) {
        const own =
            !_.isEmpty(messages) &&
            _.startsWith(
                messages[index].stream,
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
        const own = _.startsWith(
            messages[index].stream,
            `USER:${appState.session.connectionId}`
        );
        useEffect(() => {
            if (rowRef.current) {
                setRowHeight(
                    index,
                    rowRef.current.clientHeight + 30 + (!own ? 15.43 : 0)
                );
            }
        }, [rowRef]);
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
        }, []);
        const messageType = _.get(messages[index].message, "type", "STRING"),
            messageContent = _.get(messages[index].message, "content", null);
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
                    intent={own ? Intent.PRIMARY : null}
                    icon={null}
                    style={{
                        maxWidth: "min(802.2px, 100%)",
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-all",
                        width: "fit-content",
                    }}
                >
                    <div ref={rowRef}>
                        {_.isEqual(messageType, "STRING") ? (
                            messageContent
                        ) : _.isEqual(messageType, "INTERACTIVE") ? (
                            <InteractiveMessage content={messageContent} />
                        ) : null}
                    </div>
                </Callout>
                {!own ? (
                    <div
                        className={`${Classes.TEXT_DISABLED} ${Classes.TEXT_SMALL}`}
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
