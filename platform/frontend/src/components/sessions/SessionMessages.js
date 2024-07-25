import { AppContext } from "@/components/contexts/app-context";
import {
    Callout,
    Classes,
    Colors,
    Intent,
    Tag,
    Tooltip,
    mergeRefs,
} from "@blueprintjs/core";
import { faEllipsisH } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { useResizeDetector } from "react-resize-detector";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { faIcon } from "../icon";
import JsonFormMessage from "./JsonFormMessage";
import MessageMetadata from "./MessageMetadata";
export default function SessionMessages() {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus].messages;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    function getRowHeight(index) {
        const own = _.includes(
            _.get(messages, [index, "stream"]),
            `USER:${appState.session.connectionId}`
        );
        return rowHeights.current[index] + 20 || 51 + (!own ? 15.43 : 0);
    }
    function setRowHeight(index, size) {
        variableSizeListRef.current.resetAfterIndex(0);
        rowHeights.current = { ...rowHeights.current, [index]: size };
    }
    function Row({ index, style }) {
        const rowRef = useRef({});
        const own = _.includes(
            _.get(messages, [index, "stream"]),
            `USER:${appState.session.connectionId}`
        );
        useEffect(() => {
            setTimeout(() => {
                if (rowRef.current) {
                    setRowHeight(
                        index,
                        rowRef.current.clientHeight + 30 + (!own ? 20.43 : 0)
                    );
                }
            }, 0);
        }, [rowRef]);
        const handleResize = useCallback(() => {
            // do magic for resize
            if (rowRef.current) {
                setRowHeight(
                    index,
                    rowRef.current.clientHeight + 30 + (!own ? 20.43 : 0)
                );
            }
        }, []);
        const data = _.get(streams, [messages[index].stream, "data"], []);
        const contentType = _.get(messages, [index, "contentType"], null);
        const { ref: resizeRef } = useResizeDetector({
            onResize: handleResize,
        });
        const complete = _.get(
            streams,
            [messages[index].stream, "complete"],
            false
        );
        const [hasError, setHasError] = useState(false);
        const timestamp = messages[index].timestamp;
        const stream = messages[index].stream;
        const [showActions, setShowActions] = useState(false);
        return (
            <div
                key={index}
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
                        width: "fit-content",
                        overflowX: "hidden",
                        overflowY: "visible",
                    }}
                >
                    {/* <div
                        style={{
                            position: "absolute",
                            left: 0,
                            top: -10,
                            display: showActions ? null : "none",
                        }}
                    >
                        <ButtonGroup large>
                            <Tooltip
                                content="Pin to this session"
                                minimal
                                placement="bottom-start"
                            >
                                <Button icon={faIcon({ icon: faThumbtack })} />
                            </Tooltip>
                        </ButtonGroup>
                    </div> */}
                    <div
                        ref={mergeRefs(rowRef, resizeRef)}
                        style={{
                            maxWidth: "min(802.2px, 100%)",
                            minWidth: 50,
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-all",
                            width: "fit-content",
                            minHeight: 21,
                        }}
                    >
                        {_.isEqual(contentType, "JSON_FORM") ? (
                            <JsonFormMessage
                                content={_.last(data).content}
                                setHasError={setHasError}
                            />
                        ) : (
                            data.map((e, index) => {
                                const { dataType, content, id } = e;
                                if (
                                    _.includes(
                                        ["STR", "INT", "FLOAT"],
                                        dataType
                                    )
                                ) {
                                    return (
                                        <span key={id}>
                                            {(index ? " " : "") + content}
                                        </span>
                                    );
                                } else if (_.isEqual(dataType, "JSON")) {
                                    return (
                                        <pre
                                            key={id}
                                            className="margin-0"
                                            style={{ overflowX: "auto" }}
                                        >
                                            {JSON.stringify(content, null, 4)}
                                        </pre>
                                    );
                                }
                                return null;
                            })
                        )}
                        {!complete ? (
                            <>
                                <div style={{ height: 20.5, marginTop: 7.5 }}>
                                    &nbsp;
                                </div>
                                <Tag
                                    minimal
                                    style={{
                                        position: "absolute",
                                        bottom: 15,
                                        left: 15,
                                    }}
                                    icon={faIcon({
                                        icon: faEllipsisH,
                                        size: 16.5,
                                        className: "fa-fade",
                                        style: { color: Colors.BLACK },
                                    })}
                                />
                            </>
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
