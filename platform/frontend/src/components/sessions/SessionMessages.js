import { AppContext } from "@/components/contexts/app-context";
import {
    Button,
    ButtonGroup,
    Callout,
    Colors,
    Intent,
    Tag,
    Tooltip,
    mergeRefs,
} from "@blueprintjs/core";
import { faBinary, faEllipsisH } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useContext, useEffect, useMemo, useRef } from "react";
import { useResizeDetector } from "react-resize-detector";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { AuthContext } from "../contexts/auth-context";
import { faIcon } from "../icon";
import JsonFormMessage from "./JsonFormMessage";
import MessageIcon from "./MessageIcon";
import MessageMetadata from "./MessageMetadata";
const Row = ({ index, data, style }) => {
    const { messages, streams, appState, appActions, setRowHeight, settings } =
        data;
    const rowRef = useRef({});
    const debugMode = _.get(settings, "debug_mode", false);
    const own = useMemo(() => {
        const uid = _.get(messages, [index, "metadata", "id"], null);
        const created_by = _.get(
            messages,
            [index, "metadata", "created_by"],
            null
        );
        const hasUserProfile = _.has(appState, ["app", "users", uid]);
        if (_.isEqual(created_by, "USER")) {
            if (!hasUserProfile) {
                const pendingRquest = _.get(
                    appState,
                    ["app", "pendingRequests", `getUserProfile ${uid}`],
                    false
                );
                if (!pendingRquest) {
                    appActions.app.getUserProfile(uid);
                }
            }
        } else if (!_.has(appState, ["agent", "icon", created_by])) {
            appActions.agent.fetchAttributes(created_by);
        }
        return (
            _.isEqual(uid, appState.session.userId) &&
            _.isEqual(created_by, "USER")
        );
    }, [appState.session.userId]);
    const handleResize = useCallback(() => {
        // do magic for resize
        if (rowRef.current) {
            setRowHeight(
                index,
                rowRef.current.clientHeight + 75 + (debugMode ? 25 : 0)
            );
        }
    }, [rowRef, debugMode]);
    const message = messages[index];
    const stream = message.stream;
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(messages, [index, "contentType"], null);
    const { ref: resizeRef } = useResizeDetector({
        onResize: handleResize,
    });
    const complete = _.get(streams, [stream, "complete"], false);
    const hasError = useRef(false);
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
                alignItems: "flex-start",
                padding: "10px 20px",
                marginTop: 10,
                backgroundColor: showActions.current
                    ? Colors.LIGHT_GRAY5
                    : null,
            }}
        >
            <div
                className="full-parent-width"
                style={{ display: "flex", gap: 10, position: "relative" }}
            >
                <div
                    style={{
                        position: "absolute",
                        right: 0,
                        top: 0,
                        display: showActions.current ? null : "none",
                    }}
                >
                    <ButtonGroup large>
                        {_.get(settings, "debug_mode", false) ? (
                            <Tooltip
                                content="Raw"
                                minimal
                                placement="bottom-end"
                            >
                                <Button
                                    icon={faIcon({ icon: faBinary })}
                                    onClick={() =>
                                        appActions.debug.addMessage({
                                            type: "session",
                                            message,
                                            data: streams[stream],
                                        })
                                    }
                                />
                            </Tooltip>
                        ) : null}
                    </ButtonGroup>
                </div>
                <MessageIcon message={messages[index]} />
                <div style={{ width: "min(802.2px, 100% - 50px)" }}>
                    <MessageMetadata message={messages[index]} />
                    <Callout
                        intent={
                            hasError.current
                                ? Intent.DANGER
                                : own
                                ? Intent.PRIMARY
                                : null
                        }
                        icon={null}
                        style={{
                            maxWidth: "100%",
                            width: "fit-content",
                        }}
                    >
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
                                    hasError={hasError}
                                />
                            ) : (
                                streamData.map((e, index) => {
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
                                                {JSON.stringify(
                                                    content,
                                                    null,
                                                    4
                                                )}
                                            </pre>
                                        );
                                    }
                                    return null;
                                })
                            )}
                            {!complete ? (
                                <>
                                    <div
                                        style={{ height: 20.5, marginTop: 7.5 }}
                                    >
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
                </div>
            </div>
        </div>
    );
};
export default function SessionMessages() {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    const { appState, appActions } = useContext(AppContext);
    const { settings } = useContext(AuthContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus].messages;
    const debugMode = _.get(settings, "debug_mode", false);
    const streams = appState.session.sessions[sessionIdFocus].streams;
    function getRowHeight(index) {
        return rowHeights.current[index] || 96 + (debugMode ? 25 : 0);
    }
    function setRowHeight(index, size) {
        rowHeights.current = { ...rowHeights.current, [index]: size };
        if (variableSizeListRef.current) {
            variableSizeListRef.current.resetAfterIndex(0);
        }
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
                        appActions,
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
