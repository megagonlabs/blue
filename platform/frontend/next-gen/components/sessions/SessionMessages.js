import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useDedupStore } from "@/stores/dedup-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Callout,
    Colors,
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
    faArrowLeftToLine,
    faBarsFilter,
    faEllipsisH,
    faTableColumns,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useEffect, useMemo, useRef } from "react";
import { useResizeDetector } from "react-resize-detector";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import { MESSAGE_OVERFLOW_THRESHOLD } from "../constants";
import MessageContent from "./messages/MessageContent";
const Row = ({ index, data, style }) => {
    const { setRowHeight, sessionId } = data;
    const darkMode = useAppStore((state) => state.darkMode);
    const { getUserProfile, getAgentMetadata } = useDedupStore(
        useShallow((state) => ({
            getUserProfile: state.getUserProfile,
            getAgentMetadata: state.getAgentMetadata,
        }))
    );
    const { jsonforms, streams, messages } = useSessionStore(
        useShallow((state) => ({
            jsonforms: state.jsonforms,
            streams: _.get(state, ["sessions", sessionId, "streams"], {}),
            messages: _.get(state, ["sessions", sessionId, "messages"], []),
        }))
    );
    const filteredMessages = messages.filter((message) => {
        if (_.get(message, "metadata.ags.WORKSPACE_ONLY")) {
            return false;
        }
        return true;
    });
    const rowRef = useRef({});
    const user = useAuthStore((state) => state.user);
    const own = useMemo(() => {
        const uid = _.get(filteredMessages, [index, "metadata", "id"], null);
        const createdBy = _.get(
            filteredMessages,
            [index, "metadata", "created_by"],
            null
        );
        const isUser = _.isEqual(createdBy, "USER");
        if (isUser) {
            getUserProfile(uid);
        } else {
            getAgentMetadata(createdBy);
        }
        return isUser && _.isEqual(user.uid, uid);
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
    }, [rowRef]);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(filteredMessages, [index, "contentType"], null);
    const { ref: resizeRef } = useResizeDetector({ onResize: handleResize });
    const complete = _.get(streams, [stream, "complete"], false);
    const hasError = useRef(false);
    const showActions = useRef(false);
    return (
        <div
            key={index}
            onMouseLeave={() => (showActions.current = false)}
            onMouseEnter={() => (showActions.current = true)}
            style={{
                ...style,
                display: "flex",
                alignItems: "flex-start",
                padding: "10px 20px",
                marginTop: 10,
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
                        style={{ maxHeight: MESSAGE_OVERFLOW_THRESHOLD }}
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
                        <Tag interactive minimal style={{ marginTop: 15 }}>
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
}) {
    const variableSizeListRef = useRef();
    const rowHeights = useRef({});
    function setRowHeight(index, size) {
        rowHeights.current = { ...rowHeights.current, [index]: size };
        if (variableSizeListRef.current) {
            variableSizeListRef.current.resetAfterIndex(0);
        }
    }
    const { messages, tags } = useSessionStore(
        useShallow((state) => ({
            messages: _.get(state, ["sessions", sessionId, "messages"], []),
            tags: _.get(state, ["sessions", sessionId, "tags"], []),
        }))
    );
    const filteredMessages = messages.filter((message) => {
        if (_.get(message, "metadata.ags.WORKSPACE_ONLY")) {
            return false;
        }
        return true;
    });
    function getRowHeight(index) {
        let height = 51 + 10;
        return rowHeights.current[index] || height;
    }
    useEffect(() => {
        setTimeout(() => {
            requestAnimationFrame(() => {
                if (variableSizeListRef.current) {
                    variableSizeListRef.current.scrollToItem(
                        filteredMessages.length,
                        "end"
                    );
                }
            });
        }, 0);
    }, [variableSizeListRef]);
    return (
        <>
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip
                        minimal
                        placement="bottom-start"
                        content={`${showWorkspace ? "Hide" : "Show"} workspace`}
                    >
                        <Button
                            icon={
                                <FAIcon
                                    icon={
                                        showWorkspace
                                            ? faArrowLeftToLine
                                            : faTableColumns
                                    }
                                />
                            }
                            onClick={() => setShowWorkspace(!showWorkspace)}
                        />
                    </Tooltip>
                    <Popover
                        minimal
                        placement="bottom"
                        content={
                            <Menu size={Size.LARGE}>
                                <MenuItem text="Clear all" />
                                {!_.isEmpty(tags) && (
                                    <>
                                        <MenuDivider title="By tag" />
                                        {tags.map((tag, index) => {
                                            return (
                                                <MenuItem
                                                    key={index}
                                                    text={tag}
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
                            minimal
                            placement="bottom-start"
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
            </div>
            <AutoSizer>
                {({ width, height }) => (
                    <VariableSizeList
                        itemData={{ setRowHeight, sessionId }}
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
