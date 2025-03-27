import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import MessageContent from "@/components/sessions/message/MessageContent";
import MessageIcon from "@/components/sessions/message/MessageIcon";
import MessageMetadata from "@/components/sessions/message/MessageMetadata";
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
import {
    faBinary,
    faEllipsisH,
    faSidebar,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useContext, useEffect, useMemo, useRef } from "react";
import { useResizeDetector } from "react-resize-detector";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
const Row = ({ index, data, style }) => {
    const { setRowHeight } = data;
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const messages = appState.session.sessions[sessionIdFocus].messages;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    const { user, settings } = useContext(AuthContext);
    const rowRef = useRef({});
    const debugMode = _.get(settings, "debug_mode", false);
    const expandMessage = _.get(settings, "expand_message", false);
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
                let pendingRquest = _.get(
                    appState,
                    ["app", "pendingRequests", `getUserProfile ${uid}`],
                    false
                );
                if (!pendingRquest) {
                    appActions.app.getUserProfile(uid);
                }
            }
        } else if (
            !_.has(appState, ["agent", "icon", created_by]) ||
            !_.has(appState, ["agent", "systemAgents", created_by])
        ) {
            let pendingAttributesRquest = _.get(
                appState,
                [
                    "agent",
                    "pendingAttributesRequests",
                    `fetchAttributes ${created_by}`,
                ],
                false
            );
            if (!pendingAttributesRquest) {
                appActions.agent.fetchAttributes(created_by);
            }
        }
        return _.isEqual(uid, user.uid) && _.isEqual(created_by, "USER");
    }, [user.uid]); // eslint-disable-line react-hooks/exhaustive-deps
    const isOverflown = useRef(false);
    const message = messages[index];
    const stream = message.stream;
    const MESSAGE_OVERFLOW_THRESHOLD = 200;
    const handleResize = useCallback(() => {
        // do magic for resize
        if (rowRef.current) {
            const { clientWidth, clientHeight, scrollWidth, scrollHeight } =
                rowRef.current;
            isOverflown.current = false;
            if (!expandMessage) {
                if (scrollHeight > clientHeight || scrollWidth > clientWidth) {
                    isOverflown.current = true;
                }
            }
            setRowHeight(
                index,
                (isOverflown.current
                    ? MESSAGE_OVERFLOW_THRESHOLD
                    : rowRef.current.clientHeight) +
                    75 +
                    (debugMode ? 25 : 0) +
                    (isOverflown.current ? 35 : 0)
            );
        }
    }, [rowRef, debugMode, expandMessage]); // eslint-disable-line react-hooks/exhaustive-deps
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
                        <Tooltip
                            content="Add to workspace"
                            minimal
                            placement={`bottom${
                                _.get(settings, "debug_mode", false)
                                    ? ""
                                    : "-end"
                            }`}
                        >
                            <Button
                                icon={faIcon({ icon: faSidebar })}
                                onClick={() => {
                                    appActions.session.addToWorkspace({
                                        type: "session",
                                        message,
                                    });
                                    appActions.session.setState({
                                        key: "showWorkspacePanel",
                                        value: true,
                                    });
                                    appActions.session.toggleWorkspaceCollapse({
                                        stream,
                                        value: false,
                                    });
                                }}
                            />
                        </Tooltip>
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
                <div style={{ width: "calc(100% - 50px)" }}>
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
                                maxWidth: "100%",
                                minWidth: 50,
                                whiteSpace: "pre-wrap",
                                wordBreak: "break-word",
                                width: "fit-content",
                                minHeight: 21,
                                overflow: "hidden",
                                padding: 1,
                                maxHeight:
                                    expandMessage ||
                                    appState.session.expandedMessageStream.has(
                                        stream
                                    )
                                        ? null
                                        : MESSAGE_OVERFLOW_THRESHOLD,
                            }}
                        >
                            <MessageContent
                                contentType={contentType}
                                streamData={streamData}
                                hasError={hasError}
                            />
                            {!complete ? (
                                <div style={{ marginTop: 7.5 }}>
                                    <Tag
                                        minimal
                                        icon={faIcon({
                                            icon: faEllipsisH,
                                            size: 16.5,
                                            className: "fa-fade",
                                            style: { color: Colors.BLACK },
                                        })}
                                    />
                                </div>
                            ) : null}
                        </div>
                        {isOverflown.current ? (
                            <Tag
                                onClick={() => {
                                    appActions.session.expandMessageStream(
                                        stream
                                    );
                                }}
                                interactive
                                minimal
                                style={{ marginTop: 15 }}
                            >
                                Show more
                            </Tag>
                        ) : null}
                    </Callout>
                </div>
            </div>
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
    const debugMode = _.get(settings, "debug_mode", false);
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
    }, [variableSizeListRef, sessionIdFocus]); // eslint-disable-line react-hooks/exhaustive-deps
    return (
        <AutoSizer>
            {({ width, height }) => (
                <VariableSizeList
                    itemData={{ setRowHeight }}
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
