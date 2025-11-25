import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useDedupStore } from "@/stores/dedup-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Callout,
    Colors,
    Icon,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faAngleRight,
    faArrowLeft,
    faBarcodeRead,
    faBarsFilter,
    faBrowsers,
    faEllipsisH,
    faEllipsisV,
    faEraser,
    faSidebar,
    faTableColumns,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useResizeDetector } from "react-resize-detector";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { useShallow } from "zustand/react/shallow";
import {
    EMPTY_ARRAY,
    EMPTY_OBJECT,
    GREEN_CHECK,
    MESSAGE_OVERFLOW_THRESHOLD,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import UITip from "../ux/UITip";
import DebuggerContainer from "./debuggers/DebuggerContainer";
import MessageContent from "./messages/MessageContent";
import MessageIcon from "./messages/MessageIcon";
import MessageMetadata from "./messages/MessageMetadata";
import SessionDisplayName from "./SessionDisplayName";
import SessionMemberStack from "./SessionMemberStack";
const Row = ({ index, data, style }) => {
    const {
        setRowHeight,
        sessionId,
        addInspectionContainer,
        setShowWorkspace,
        filteredMessages,
    } = data;
    const message = filteredMessages[index];
    const { darkMode, autoExpandMessage, detailedMessage } = useAppStore(
        useShallow((state) => ({
            darkMode: state.dark_mode,
            autoExpandMessage: state.expand_message,
            detailedMessage: state.detailed_message,
        }))
    );
    const { showAxiosErrorToast } = useToaster();
    const { getUserProfileById, getAgentMetadata } = useDedupStore(
        useShallow((state) => ({
            getUserProfileById: state.getUserProfileById,
            getAgentMetadata: state.getAgentMetadata,
        }))
    );
    const {
        streams,
        addToWorkspace,
        setInspectionFocusStream,
        expandMessage,
        expandedMessages,
    } = useSessionStore(
        useShallow((state) => ({
            streams: _.get(
                state,
                ["sessions", sessionId, "streams"],
                EMPTY_OBJECT
            ),
            messages: _.get(
                state,
                ["sessions", sessionId, "messages"],
                EMPTY_ARRAY
            ),
            messageFilterTags: state.messageFilterTags,
            addToWorkspace: state.addToWorkspace,
            setInspectionFocusStream: state.setInspectionFocusStream,
            expandMessage: state.expandMessage,
            expandedMessages: state.expandedMessages,
        }))
    );
    const rowRef = useRef({});
    const user = useAuthStore((state) => state.user);
    const own = useMemo(() => {
        const id = _.get(message, "metadata.id", null);
        const createdBy = _.get(message, "metadata.created_by", null);
        const isUser = _.isEqual(createdBy, "USER");
        if (isUser) {
            getUserProfileById(id, showAxiosErrorToast);
        } else {
            getAgentMetadata(createdBy);
        }
        return isUser && _.isEqual(user.uid, id);
    }, [user, message]);
    const isOverflow = useRef(false);
    const stream = message.stream;
    const handleResize = useCallback(() => {
        // do magic for resize
        if (rowRef.current) {
            const { clientWidth, clientHeight, scrollWidth, scrollHeight } =
                rowRef.current;
            isOverflow.current =
                scrollHeight > clientHeight || scrollWidth > clientWidth;
            let height =
                61 +
                (isOverflow.current
                    ? MESSAGE_OVERFLOW_THRESHOLD
                    : rowRef.current.clientHeight);
            if (isOverflow.current) height += 35;
            if (detailedMessage) height += 30;
            setRowHeight(index, height);
        }
    }, [rowRef, index, setRowHeight, expandMessage, detailedMessage]);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(message, "contentType", null);
    const { ref: resizeRef } = useResizeDetector({ onResize: handleResize });
    const complete = _.get(streams, [stream, "complete"], false);
    const hasError = useRef(false);
    const [showActions, setShowActions] = useState(false);
    useEffect(() => {
        if (autoExpandMessage) {
            expandMessage(sessionId, stream);
        }
    }, [autoExpandMessage]);
    const expanded = _.get(expandedMessages, [sessionId, stream], false);
    useEffect(() => {
        handleResize();
    }, [expanded, detailedMessage]);
    if (!message) {
        return null;
    }
    return (
        <div
            key={index}
            onMouseLeave={() => {
                setShowActions(false);
            }}
            onMouseEnter={() => {
                setShowActions(true);
            }}
            style={{
                ...style,
                display: "flex",
                alignItems: "flex-start",
                padding: "10px 20px",
                backgroundColor: showActions
                    ? darkMode
                        ? Colors.DARK_GRAY1
                        : Colors.LIGHT_GRAY4
                    : null,
            }}
        >
            <div
                className="full-parent-width"
                style={{
                    display: "flex",
                    gap: 10,
                    flexDirection: own ? "row-reverse" : null,
                }}
            >
                <div
                    style={{
                        borderRadius: 2,
                        position: "absolute",
                        right: detailedMessage ? 70 : 20,
                        top: detailedMessage ? 40 : 10,
                        display: showActions ? null : "none",
                    }}
                >
                    <ButtonGroup size={Size.LARGE}>
                        {!_.isEqual(contentType, "ERROR") && (
                            <Tooltip
                                placement="bottom"
                                content="Add to Workspace"
                            >
                                <Button
                                    icon={<FAIcon icon={faSidebar} />}
                                    onClick={() => {
                                        addToWorkspace({
                                            type: "session",
                                            message,
                                            sessionId,
                                        });
                                        setShowWorkspace(true);
                                    }}
                                />
                            </Tooltip>
                        )}
                        <Tooltip placement="bottom-end" content="Inspect">
                            <Button
                                onClick={() => {
                                    addInspectionContainer();
                                    setInspectionFocusStream(sessionId, stream);
                                }}
                                icon={<FAIcon icon={faBarcodeRead} />}
                            />
                        </Tooltip>
                    </ButtonGroup>
                </div>
                {detailedMessage && <MessageIcon metadata={message.metadata} />}
                <div
                    style={{
                        display: "flex",
                        gap: 10,
                        width: `calc(100% - ${detailedMessage ? 50 : 0}px)`,
                        flexDirection: "column",
                        alignItems: own ? "flex-end" : null,
                    }}
                >
                    {detailedMessage && <MessageMetadata message={message} />}
                    <Callout
                        intent={
                            hasError.current || _.isEqual(contentType, "ERROR")
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
                            borderRadius: own
                                ? "15px 2px 15px 15px"
                                : "2px 15px 15px 15px",
                        }}
                    >
                        <div
                            ref={rowRef}
                            className="message-bubble-callout-content"
                            style={{
                                maxHeight: expanded
                                    ? null
                                    : MESSAGE_OVERFLOW_THRESHOLD,
                            }}
                        >
                            <div ref={resizeRef}>
                                <MessageContent
                                    contentType={contentType}
                                    streamData={streamData}
                                    hasError={hasError}
                                />
                                {!complete && (
                                    <div style={{ marginTop: 10 }}>
                                        <Tag
                                            minimal
                                            icon={
                                                <FAIcon
                                                    icon={faEllipsisH}
                                                    className="fa-fade"
                                                />
                                            }
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                        {isOverflow.current && (
                            <Tag
                                onClick={() => {
                                    expandMessage(sessionId, stream);
                                }}
                                interactive
                                minimal
                                style={{ marginTop: 15 }}
                            >
                                Show more
                            </Tag>
                        )}
                    </Callout>
                </div>
            </div>
        </div>
    );
};
export default function SessionMessages({
    sessionId,
    showWorkspace,
    setShowWorkspace,
    setShowDetails,
}) {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    function setRowHeight(index, size) {
        rowHeights.current = { ...rowHeights.current, [index]: size };
        if (variableSizeListRef.current) {
            variableSizeListRef.current.resetAfterIndex(0);
        }
    }
    const {
        messages,
        tags,
        messageFilterTags,
        toggleMessageFilterTag,
        clearMessageFilterTags,
    } = useSessionStore(
        useShallow((state) => ({
            messages: _.get(
                state,
                ["sessions", sessionId, "messages"],
                EMPTY_ARRAY
            ),
            tags: _.get(state, ["sessions", sessionId, "tags"], EMPTY_ARRAY),
            messageFilterTags: state.messageFilterTags,
            toggleMessageFilterTag: state.toggleMessageFilterTag,
            clearMessageFilterTags: state.clearMessageFilterTags,
        }))
    );
    const filterTags = _.get(messageFilterTags, sessionId, EMPTY_ARRAY);
    const filteredMessages = useMemo(() => {
        return messages.filter((message) => {
            const stream = _.get(message, "stream", null);
            if (
                _.get(message, "metadata.ags.WORKSPACE_ONLY") ||
                _.endsWith(stream, "PROGRESS:STREAM")
            ) {
                return false;
            }
            let include = false;
            for (let i = 0; i < _.size(filterTags); i++) {
                if (_.get(message, ["metadata", "tags", filterTags[i]])) {
                    include = true;
                    break;
                }
            }
            return _.isEmpty(filterTags) || include;
        });
    }, [messages, filterTags]);
    function getRowHeight(index) {
        let height = 81;
        return rowHeights.current[index] || height;
    }
    const addContainer = useGridStore((state) => state.addContainer);
    const addInspectionContainer = () => {
        addContainer({
            icon: faBarcodeRead,
            title: <SessionDisplayName sessionId={sessionId} />,
            content: <DebuggerContainer sessionId={sessionId} />,
            uniqueId: `DebuggerContainer-${sessionId}`,
        });
    };
    useEffect(() => {
        if (variableSizeListRef.current) {
            variableSizeListRef.current.resetAfterIndex(0);
        }
        setTimeout(() => {
            requestAnimationFrame(() => {
                if (variableSizeListRef.current) {
                    variableSizeListRef.current.scrollToItem(
                        _.size(filteredMessages),
                        "end"
                    );
                }
            });
        }, 0);
    }, [variableSizeListRef, filteredMessages]);
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    return (
        <>
            <div
                ref={elementRef}
                className="border-bottom"
                style={{
                    padding: 10,
                    display: "flex",
                    justifyContent: "space-between",
                }}
            >
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        content="Workspace"
                        boundary={popoverBoundary}
                    >
                        <Button
                            icon={
                                <FAIcon
                                    icon={
                                        showWorkspace
                                            ? faArrowLeft
                                            : faTableColumns
                                    }
                                />
                            }
                            onClick={() => {
                                setShowWorkspace(!showWorkspace);
                            }}
                        />
                    </Tooltip>
                    <Popover
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={popoverBoundary}
                        minimal
                        content={
                            <Menu size={Size.LARGE}>
                                <MenuItem
                                    text="Deselect all"
                                    onClick={() => {
                                        clearMessageFilterTags(sessionId);
                                    }}
                                    icon={<FAIcon icon={faEraser} />}
                                />
                                {!_.isEmpty(tags) && (
                                    <>
                                        <MenuDivider title="By tag" />
                                        {tags.map((tag, index) => {
                                            const selected = _.includes(
                                                filterTags,
                                                tag
                                            );
                                            return (
                                                <MenuItem
                                                    icon={
                                                        selected ? (
                                                            GREEN_CHECK
                                                        ) : (
                                                            <Icon icon="blank" />
                                                        )
                                                    }
                                                    key={index}
                                                    text={tag}
                                                    onClick={() => {
                                                        toggleMessageFilterTag(
                                                            sessionId,
                                                            tag
                                                        );
                                                    }}
                                                    shouldDismissPopover={false}
                                                />
                                            );
                                        })}
                                    </>
                                )}
                            </Menu>
                        }
                    >
                        <Tooltip
                            openOnTargetFocus={false}
                            placement="bottom"
                            content="Filter"
                        >
                            <Button
                                intent={Intent.PRIMARY}
                                alignText={Alignment.START}
                                icon={<FAIcon icon={faBarsFilter} />}
                                text={_.size()}
                            />
                        </Tooltip>
                    </Popover>
                </ButtonGroup>
                <div
                    style={{
                        display: "flex",
                        flexDirection: "row-reverse",
                        alignItems: "center",
                        gap: 10,
                    }}
                >
                    <ButtonGroup
                        size={Size.LARGE}
                        variant={ButtonVariant.MINIMAL}
                    >
                        <Popover
                            {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                            boundary={popoverBoundary}
                            minimal
                            content={
                                <Menu size={Size.LARGE}>
                                    <MenuItem
                                        onClick={() => {
                                            setShowDetails(true);
                                        }}
                                        text="Open session details"
                                    />
                                    <MenuItem
                                        labelElement={
                                            <FAIcon
                                                icon={faBrowsers}
                                                style={{ marginLeft: 3 }}
                                            />
                                        }
                                        icon={<FAIcon icon={faBarcodeRead} />}
                                        onClick={addInspectionContainer}
                                        text="Inspect"
                                    />
                                </Menu>
                            }
                        >
                            <Tooltip
                                {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                                boundary={popoverBoundary}
                                content="More actions"
                            >
                                <Button icon={<FAIcon icon={faEllipsisV} />} />
                            </Tooltip>
                        </Popover>
                    </ButtonGroup>
                    <div style={{ width: 200, height: 40 }}>
                        <SessionMemberStack
                            style={{ justifyContent: "flex-end" }}
                            sessionId={sessionId}
                        />
                    </div>
                    <div style={{ marginLeft: 20 }}>
                        <UITip
                            id="session_inspection_debugger"
                            content={
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        flexWrap: "wrap",
                                    }}
                                >
                                    To debug a session, open the debugger&nbsp;
                                    <span>by clicking on</span>
                                    <Button
                                        className="pointer-events-none"
                                        icon={<FAIcon icon={faEllipsisV} />}
                                        variant={ButtonVariant.MINIMAL}
                                    />
                                    <FAIcon icon={faAngleRight} />
                                    <Tag
                                        style={{
                                            marginLeft: 5,
                                            marginRight: 5,
                                        }}
                                        minimal
                                        icon={<FAIcon icon={faBarcodeRead} />}
                                        size={Size.LARGE}
                                        endIcon={<FAIcon icon={faBrowsers} />}
                                    >
                                        Inspect
                                    </Tag>
                                    <span>.</span> This action also activates
                                    debug mode for the session, which enables
                                    the reception of hidden data streams.
                                </div>
                            }
                        />
                    </div>
                </div>
            </div>
            <AutoSizer>
                {({ width, height }) => (
                    <VariableSizeList
                        itemData={{
                            setRowHeight,
                            sessionId,
                            addInspectionContainer,
                            setShowWorkspace,
                            variableSizeListRef,
                            filteredMessages,
                        }}
                        itemSize={getRowHeight}
                        itemCount={_.size(filteredMessages)}
                        width={width}
                        height={height - 61}
                        ref={variableSizeListRef}
                    >
                        {Row}
                    </VariableSizeList>
                )}
            </AutoSizer>
        </>
    );
}
