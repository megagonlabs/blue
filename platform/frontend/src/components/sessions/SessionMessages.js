import { AppContext } from "@/components/contexts/app-context";
import {
    Button,
    ButtonGroup,
    Callout,
    Classes,
    Colors,
    Intent,
    Tag,
    Tooltip,
    mergeRefs,
} from "@blueprintjs/core";
import { faBinary, faEllipsisH } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { useResizeDetector } from "react-resize-detector";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { AuthContext } from "../contexts/auth-context";
import { faIcon } from "../icon";
import JsonFormMessage from "./JsonFormMessage";
import MessageMetadata from "./MessageMetadata";
const Row = ({ index, data, style }) => {
    const { messages, streams, appState, setRowHeight, settings } = data;
    const rowRef = useRef({});
    const own = _.includes(
        _.get(messages, [index, "stream"]),
        `USER:${appState.session.connectionId}`
    );
    useEffect(() => {
        if (rowRef.current) {
            setRowHeight(
                index,
                rowRef.current.clientHeight + 30 + (!own ? 20.43 : 0) + 20
            );
        }
    }, [rowRef]);
    const handleResize = useCallback(() => {
        // do magic for resize
        if (rowRef.current) {
            setRowHeight(
                index,
                rowRef.current.clientHeight + 30 + (!own ? 20.43 : 0) + 20
            );
        }
    }, []);
    const message = messages[index];
    const stream = message.stream;
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(messages, [index, "contentType"], null);
    const { ref: resizeRef } = useResizeDetector({
        onResize: handleResize,
    });
    const complete = _.get(streams, [stream, "complete"], false);
    const [hasError, setHasError] = useState(false);
    const timestamp = message.timestamp;
    const showActions = useRef(false);
    return (
        <div
            key={index}
            onMouseEnter={() => {
                showActions.current = true;
            }}
            onMouseLeave={() => {
                showActions.current = false;
            }}
            style={{
                ...style,
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                padding: "10px 20px",
                marginTop: 10,
                backgroundColor: showActions.current
                    ? Colors.LIGHT_GRAY5
                    : null,
            }}
        >
            <Callout
                intent={hasError ? Intent.DANGER : own ? Intent.PRIMARY : null}
                icon={null}
                style={{
                    position: "relative",
                    maxWidth: "min(802.2px, 100%)",
                    width: "fit-content",
                }}
            >
                <div
                    style={{
                        position: "absolute",
                        left: 0,
                        top: -10,
                        display: showActions.current ? null : "none",
                    }}
                >
                    <ButtonGroup large>
                        {_.get(settings, "debug_mode", false) ? (
                            <Tooltip
                                content="Raw"
                                minimal
                                placement="bottom-start"
                            >
                                <Button
                                    icon={faIcon({ icon: faBinary })}
                                    onClick={() =>
                                        console.log(message, streams[stream])
                                    }
                                />
                            </Tooltip>
                        ) : null}
                    </ButtonGroup>
                </div>
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
                            content={_.last(streamData).content}
                            setHasError={setHasError}
                        />
                    ) : (
                        streamData.map((e, index) => {
                            const { dataType, content, id } = e;
                            if (_.includes(["STR", "INT", "FLOAT"], dataType)) {
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
};
export default function SessionMessages() {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    const { appState } = useContext(AppContext);
    const { settings } = useContext(AuthContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus].messages;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    function getRowHeight(index) {
        const own = _.includes(
            _.get(messages, [index, "stream"]),
            `USER:${appState.session.connectionId}`
        );
        return rowHeights.current[index] || 71 + (!own ? 15.43 : 0);
    }
    function setRowHeight(index, size) {
        variableSizeListRef.current.resetAfterIndex(0);
        rowHeights.current = { ...rowHeights.current, [index]: size };
    }
    useEffect(() => {
        setTimeout(() => {
            requestAnimationFrame(() => {
                if (variableSizeListRef.current) {
                    variableSizeListRef.current.scrollToItem(
                        messages.length,
                        "end"
                    );
                }
            });
        }, 0);
    }, [variableSizeListRef, sessionIdFocus]);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <VariableSizeList
                    itemData={{
                        messages,
                        streams,
                        appState,
                        setRowHeight,
                        settings,
                    }}
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
