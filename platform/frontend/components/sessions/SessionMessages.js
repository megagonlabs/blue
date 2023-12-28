import { Callout, Card, Classes, H4 } from "@blueprintjs/core";
import { useContext, useEffect, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { AppContext } from "../app-context";
export default function SessionMessages() {
    const listRef = useRef({});
    const rowHeights = useRef({});
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus];
    function getRowHeight(index) {
        return rowHeights.current[index] + 15 || 51;
    }
    function setRowHeight(index, size) {
        listRef.current.resetAfterIndex(0);
        rowHeights.current = { ...rowHeights.current, [index]: size };
    }
    function Row({ index, style }) {
        const rowRef = useRef({});
        useEffect(() => {
            if (rowRef.current) {
                setRowHeight(index, rowRef.current.clientHeight + 30);
            }
        }, [rowRef]);
        return (
            <div style={{ ...style, padding: "15px 15px 0px" }}>
                <Callout
                    style={{
                        maxWidth: 602,
                        whiteSpace: "pre-wrap",
                        width: "fit-content",
                    }}
                >
                    <div ref={rowRef}>{messages[index]}</div>
                </Callout>
            </div>
        );
    }
    return (
        <>
            <Card style={{ padding: 15, borderRadius: 0 }}>
                <H4
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{ margin: 0 }}
                >
                    {sessionIdFocus}
                </H4>
            </Card>
            <AutoSizer>
                {({ width, height }) => (
                    <VariableSizeList
                        style={{ paddingBottom: 15 }}
                        height={height - 51}
                        itemCount={messages.length}
                        itemSize={getRowHeight}
                        ref={listRef}
                        width={width}
                    >
                        {Row}
                    </VariableSizeList>
                )}
            </AutoSizer>
        </>
    );
}
