import { Callout } from "@blueprintjs/core";
import { useContext, useEffect, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { AppContext } from "../app-context";
export default function SessionMessages() {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus];
    function getRowHeight(index) {
        return (
            rowHeights.current[index] +
                (_.isEqual(index, messages.length - 1) ? 20 : 10) +
                (_.isEqual(index, 0) ? 20 : 0) || 51
        );
    }
    function setRowHeight(index, size, shouldForceUpdate = true) {
        variableSizeListRef.current.resetAfterIndex(0, shouldForceUpdate);
        rowHeights.current = { ...rowHeights.current, [index]: size };
    }
    function Row({ index, style }) {
        const rowRef = useRef({});
        useEffect(() => {
            if (rowRef.current) {
                setRowHeight(index, rowRef.current.clientHeight + 30);
            }
        }, [rowRef]);
        useEffect(() => {
            const handleResize = () => {
                // do magic for resize
                if (rowRef.current) {
                    setRowHeight(
                        index,
                        rowRef.current.clientHeight + 30,
                        false
                    );
                }
            };
            window.addEventListener("resize", handleResize);
            return () => {
                window.removeEventListener("resize", handleResize);
            };
        }, []);
        return (
            <div
                style={{
                    ...style,
                    padding: `${_.isEqual(index, 0) ? 20 : 0}px 20px ${
                        _.isEqual(index, messages.length - 1) ? 20 : 10
                    }px`,
                }}
            >
                <Callout
                    style={{
                        maxWidth: 602.2,
                        whiteSpace: "pre-wrap",
                        width: "fit-content",
                    }}
                >
                    <div ref={rowRef}>{messages[index]}</div>
                </Callout>
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
