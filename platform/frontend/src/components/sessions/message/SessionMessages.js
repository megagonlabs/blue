import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import MessageContent from "@/components/sessions/message/MessageContent";
import MessageIcon from "@/components/sessions/message/MessageIcon";
import MessageMetadata from "@/components/sessions/message/MessageMetadata";
import {
    Alignment,
    Button,
    ButtonGroup,
    Callout,
    Colors,
    Icon,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Tag,
    Tooltip,
    mergeRefs,
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faBinary,
    faCheck,
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
    const { expandedMessageStream, jsonformSpecs, sessionIdFocus } =
        appState.session;
    const sessionMessageFilterTags = _.get(
        appState,
        ["session", "sessionMessageFilterTags", sessionIdFocus],
        []
    );
    const messages = _.get(
        appState,
        ["session", "sessions", sessionIdFocus, "messages"],
        []
    ).filter((message) => {
        if (_.get(message, "metadata.tags.WORKSPACE_ONLY")) return false;
        let include = false;
        for (let i = 0; i < _.size(sessionMessageFilterTags); i++) {
            const tag = sessionMessageFilterTags[i];
            if (_.get(message, ["metadata", "tags", tag])) {
                include = true;
                break;
            }
        }
        return _.isEmpty(sessionMessageFilterTags) || include;
    });
    const streams = _.get(
        appState,
        ["session", "sessions", sessionIdFocus, "streams"],
        {}
    );
    const { user, settings } = useContext(AuthContext);
    const conversationView = _.get(settings, "conversation_view", false);
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
    }, [user.uid, messages]); // eslint-disable-line react-hooks/exhaustive-deps
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
            // 53: 1 line message height
            // 20: gap space between messages
            // 25: message metadata height
            let height =
                30 +
                20 +
                (isOverflown.current
                    ? MESSAGE_OVERFLOW_THRESHOLD
                    : rowRef.current.clientHeight);
            if (isOverflown.current) height += 35;
            if (!conversationView) {
                height += 25; // message metadata height
                if (debugMode) height += 25;
            }
            setRowHeight(index, height);
        }
    }, [rowRef, debugMode, expandMessage, conversationView]); // eslint-disable-line react-hooks/exhaustive-deps
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
                style={{
                    display: "flex",
                    gap: 10,
                    position: "relative",
                    flexDirection:
                        conversationView && own ? "row-reverse" : null,
                }}
            >
                <div
                    style={{
                        position: "absolute",
                        right: 0,
                        top: 0,
                        zIndex: 22,
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
                                    onClick={() => {
                                        const isJsonForm = _.isEqual(
                                            _.get(message, "contentType", null),
                                            "JSON_FORM"
                                        );
                                        let debugMessage = {
                                            type: "session",
                                            message,
                                            stream: streams[stream],
                                        };
                                        if (isJsonForm) {
                                            const lastForm = _.last(
                                                streams[stream].data
                                            );
                                            const formId = _.get(
                                                lastForm,
                                                "content.form_id"
                                            );
                                            _.set(
                                                debugMessage,
                                                "form",
                                                _.get(jsonformSpecs, formId, {})
                                            );
                                        }
                                        appActions.debug.addMessage(
                                            debugMessage
                                        );
                                    }}
                                />
                            </Tooltip>
                        ) : null}
                    </ButtonGroup>
                </div>
                {!conversationView && <MessageIcon message={messages[index]} />}
                <div
                    style={{
                        maxWidth: "100%",
                        width: conversationView
                            ? null
                            : `calc(100% - ${conversationView ? 0 : 50}px)`,
                    }}
                >
                    {!conversationView && (
                        <MessageMetadata message={messages[index]} />
                    )}
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
                            overflow: "hidden",
                            ...(conversationView
                                ? {
                                      borderRadius: own
                                          ? "20px 20px 2px 20px"
                                          : "20px 20px 20px 2px",
                                      paddingLeft: 20,
                                      paddingRight: 20,
                                  }
                                : {}),
                        }}
                    >
                        <div
                            ref={mergeRefs(rowRef, resizeRef)}
                            className="message-bubble-callout"
                            style={{
                                maxHeight:
                                    expandMessage ||
                                    expandedMessageStream.has(stream)
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
    const { appState, appActions } = useContext(AppContext);
    const { settings } = useContext(AuthContext);
    const conversationView = _.get(settings, "conversation_view", false);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const sessionMessageTags = _.get(
        appState,
        ["session", "sessionMessageTags", sessionIdFocus],
        new Set()
    );
    const sessionMessageFilterTags = _.get(
        appState,
        ["session", "sessionMessageFilterTags", sessionIdFocus],
        []
    );
    const messages = _.get(
        appState,
        ["session", "sessions", sessionIdFocus, "messages"],
        []
    ).filter((message) => {
        if (_.get(message, "metadata.tags.WORKSPACE_ONLY")) return false;
        let include = false;
        for (let i = 0; i < _.size(sessionMessageFilterTags); i++) {
            const tag = sessionMessageFilterTags[i];
            if (_.get(message, ["metadata", "tags", tag])) {
                include = true;
                break;
            }
        }
        return _.isEmpty(sessionMessageFilterTags) || include;
    });
    const debugMode = _.get(settings, "debug_mode", false);
    function getRowHeight(index) {
        // 53: 1 line message height
        // 20: gap space between messages
        // 25: message metadata height
        let height = 53 + 20;
        if (!conversationView) {
            height += 25; // message metadata height
            if (debugMode) height += 25;
        }
        return rowHeights.current[index] || height;
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
        <>
            <div className="border-bottom" style={{ padding: "5px 20px" }}>
                <Popover
                    minimal
                    content={
                        <div>
                            <Menu>
                                <MenuItem
                                    text="Clear all"
                                    onClick={() =>
                                        appActions.session.clearSessionMessageFilterTag()
                                    }
                                />
                                <MenuDivider title="By tags" />
                                {_.toArray(sessionMessageTags).map(
                                    (tag, index) => {
                                        const selected = _.includes(
                                            sessionMessageFilterTags,
                                            tag
                                        );
                                        return (
                                            <MenuItem
                                                key={index}
                                                icon={
                                                    selected ? (
                                                        faIcon({
                                                            icon: faCheck,
                                                            style: {
                                                                color: Colors.GREEN3,
                                                            },
                                                        })
                                                    ) : (
                                                        <Icon icon="blank" />
                                                    )
                                                }
                                                onClick={() => {
                                                    if (selected)
                                                        appActions.session.removeSessionMessageFilterTag(
                                                            tag
                                                        );
                                                    else
                                                        appActions.session.addSessionMessageFilterTag(
                                                            tag
                                                        );
                                                }}
                                                shouldDismissPopover={false}
                                                text={tag}
                                            />
                                        );
                                    }
                                )}
                            </Menu>
                        </div>
                    }
                    placement="bottom-start"
                >
                    <Tooltip
                        openOnTargetFocus={false}
                        minimal
                        placement="bottom-start"
                        content="Filter"
                    >
                        <ButtonGroup minimal>
                            <Button
                                alignText={Alignment.LEFT}
                                icon={faIcon({ icon: faBarsFilter })}
                                text={_.size(sessionMessageFilterTags)}
                            />
                        </ButtonGroup>
                    </Tooltip>
                </Popover>
            </div>
            <AutoSizer>
                {({ width, height }) => (
                    <VariableSizeList
                        itemData={{ setRowHeight }}
                        height={height - 40}
                        itemCount={messages.length}
                        itemSize={getRowHeight}
                        ref={variableSizeListRef}
                        width={width}
                    >
                        {Row}
                    </VariableSizeList>
                )}
            </AutoSizer>
        </>
    );
}
