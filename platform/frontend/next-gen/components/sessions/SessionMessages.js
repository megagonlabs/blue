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
    mergeRefs,
    Popover,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowLeft,
    faBarcodeRead,
    faBarsFilter,
    faBrowsers,
    faEllipsisH,
    faEllipsisV,
    faSidebar,
    faTableColumns,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useEffect, useMemo, useRef } from "react";
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
import { FAIcon } from "../FAIcon";
import DebuggerContainer from "./debuggers/DebuggerContainer";
import MessageContent from "./messages/MessageContent";
import SessionDisplayName from "./SessionDisplayName";
import SessionMemberStack from "./SessionMemberStack";
const Row = ({ index, data, style }) => {
    const { setRowHeight, sessionId, addInspectionContainer } = data;
    const { darkMode, autoExpandMessage } = useAppStore(
        useShallow((state) => ({
            darkMode: state.dark_mode,
            autoExpandMessage: state.expand_message,
        }))
    );
    const { getUserProfileById, getAgentMetadata } = useDedupStore(
        useShallow((state) => ({
            getUserProfileById: state.getUserProfileById,
            getAgentMetadata: state.getAgentMetadata,
        }))
    );

    const {
        streams,
        messages,
        addToWorkspace,
        setInspectionFocusStream,
        expandMessage,
        expandedMessages,
        messageFilterTags,
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
    const filterTags = _.get(messageFilterTags, sessionId, []);
    const filteredMessages = messages.filter((message) => {
        if (_.get(message, "metadata.ags.WORKSPACE_ONLY")) {
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
    const rowRef = useRef({});
    const user = useAuthStore((state) => state.user);
    const own = useMemo(() => {
        const id = _.get(filteredMessages, [index, "metadata", "id"], null);
        const createdBy = _.get(
            filteredMessages,
            [index, "metadata", "created_by"],
            null
        );
        const isUser = _.isEqual(createdBy, "USER");
        if (isUser) {
            getUserProfileById(id);
        } else {
            getAgentMetadata(createdBy);
        }
        return isUser && _.isEqual(user.uid, id);
    }, [user, filteredMessages]);
    const isOverflow = useRef(false);
    const message = filteredMessages[index];
    const stream = message.stream;
    const handleResize = useCallback(() => {
        // do magic for resize
        if (rowRef.current) {
            const { clientWidth, clientHeight, scrollWidth, scrollHeight } =
                rowRef.current;
            isOverflow.current =
                scrollHeight > clientHeight || scrollWidth > clientWidth;
            let height =
                50 +
                (isOverflow.current
                    ? MESSAGE_OVERFLOW_THRESHOLD
                    : rowRef.current.clientHeight);
            if (isOverflow.current) height += 35;
            setRowHeight(index, height);
        }
    }, [rowRef, index, setRowHeight]);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(filteredMessages, [index, "contentType"], null);
    const { ref: resizeRef } = useResizeDetector({ onResize: handleResize });
    const complete = _.get(streams, [stream, "complete"], false);
    const hasError = useRef(false);
    const showActions = useRef(false);
    useEffect(() => {
        if (autoExpandMessage) {
            expandMessage(sessionId, stream);
        }
    }, [autoExpandMessage]);
    return (
        <div
            key={index}
            onMouseLeave={() => {
                showActions.current = false;
            }}
            onMouseEnter={() => {
                showActions.current = true;
            }}
            style={{
                ...style,
                display: "flex",
                alignItems: "flex-start",
                padding: "10px 20px",
                backgroundColor: showActions.current
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
                        right: 20,
                        top: 10,
                        display: showActions.current ? null : "none",
                    }}
                >
                    <ButtonGroup size={Size.LARGE}>
                        <Tooltip placement="bottom" content="Add to Workspace">
                            <Button
                                icon={<FAIcon icon={faSidebar} />}
                                onClick={() =>
                                    addToWorkspace({
                                        type: "session",
                                        message,
                                        sessionId,
                                    })
                                }
                            />
                        </Tooltip>
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
                        borderRadius: own
                            ? "15px 15px 2px 15px"
                            : "15px 15px 15px 2px",
                    }}
                >
                    <div
                        ref={mergeRefs(rowRef, resizeRef)}
                        className="message-bubble-callout-content"
                        style={{
                            maxHeight: _.get(
                                expandedMessages,
                                [sessionId, stream],
                                false
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
    const filterTags = _.get(messageFilterTags, sessionId, []);
    const filteredMessages = messages.filter((message) => {
        if (_.get(message, "metadata.ags.WORKSPACE_ONLY")) {
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
    function getRowHeight(index) {
        let height = 71;
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
                                    text="Clear all"
                                    onClick={() => {
                                        clearMessageFilterTags(sessionId);
                                    }}
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
                </div>
            </div>
            <AutoSizer>
                {({ width, height }) => (
                    <VariableSizeList
                        itemData={{
                            setRowHeight,
                            sessionId,
                            addInspectionContainer,
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
