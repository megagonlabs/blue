import { WORKSAPCE_DRAGGABLE_SYMBOL } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageContent from "@/components/sessions/message/MessageContent";
import {
    attachClosestEdge,
    extractClosestEdge,
} from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge";
import { DropIndicator } from "@atlaskit/pragmatic-drag-and-drop-react-drop-indicator/box";
import { combine } from "@atlaskit/pragmatic-drag-and-drop/combine";
import {
    draggable,
    dropTargetForElements,
} from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import { pointerOutsideOfPreview } from "@atlaskit/pragmatic-drag-and-drop/element/pointer-outside-of-preview";
import { setCustomNativeDragPreview } from "@atlaskit/pragmatic-drag-and-drop/element/set-custom-native-drag-preview";
import {
    Button,
    ButtonGroup,
    Callout,
    Card,
    Classes,
    Collapse,
    Intent,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faChevronDown,
    faChevronUp,
    faMessage,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import invariant from "tiny-invariant";
const IDLE_STATE = { type: "idle" };
export default function MessageSnapshot({ content, index }) {
    const ref = useRef(null);
    const hasError = useRef(false);
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    const stream = _.get(content, "message.stream", null);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(content, "message.contentType", null);
    const [dragging, setDragging] = useState(false);
    const [state, setState] = useState(IDLE_STATE);
    const dragData = { index, [WORKSAPCE_DRAGGABLE_SYMBOL]: true };
    const loading = _.get(content, "loading", false);
    const isCollapsed = _.get(
        appState,
        ["session", "sessionWorkspaceCollapse", stream],
        true
    );
    useEffect(() => {
        const element = ref.current;
        invariant(element);
        return combine(
            draggable({
                element: element,
                getInitialData: () => dragData,
                onDragStart: () => setDragging(true),
                onDrop: () => setDragging(false),
                onGenerateDragPreview: ({ nativeSetDragImage }) => {
                    setCustomNativeDragPreview({
                        getOffset: pointerOutsideOfPreview({
                            x: "20px",
                            y: "0px",
                        }),
                        render: ({ container }) => {
                            const root = createRoot(container);
                            root.render(
                                <div style={{ padding: 1 }}>
                                    <Card
                                        compact
                                        style={{
                                            maxWidth: 200,
                                            maxHeight: 200,
                                            overflow: "hidden",
                                            padding: 15,
                                        }}
                                        className={
                                            Classes.TEXT_OVERFLOW_ELLIPSIS
                                        }
                                    >
                                        <MessageContent
                                            isDragPreview={true}
                                            contentType={contentType}
                                            streamData={streamData}
                                            hasError={hasError}
                                        />
                                    </Card>
                                </div>
                            );
                            return () => root.unmount();
                        },
                        nativeSetDragImage,
                    });
                },
            }),
            dropTargetForElements({
                element,
                canDrop({ source }) {
                    // not allowing dropping on yourself
                    if (_.isEqual(source.element, element)) return false;
                    return true;
                },
                getData({ input }) {
                    return attachClosestEdge(dragData, {
                        element,
                        input,
                        allowedEdges: ["top", "bottom"],
                    });
                },
                getIsSticky() {
                    return true;
                },
                onDragEnter({ self }) {
                    const closestEdge = extractClosestEdge(self.data);
                    setState({ type: "isDraggingOver", closestEdge });
                },
                onDrag({ self }) {
                    const closestEdge = extractClosestEdge(self.data);
                    // Only need to update react state if nothing has changed.
                    // Prevents re-rendering.
                    setState((current) => {
                        if (
                            _.isEqual(current.type, "isDraggingOver") &&
                            _.isEqual(current.closestEdge, closestEdge)
                        )
                            return current;
                        return { type: "isDraggingOver", closestEdge };
                    });
                },
                onDragLeave() {
                    setState(IDLE_STATE);
                },
                onDrop() {
                    setState(IDLE_STATE);
                },
            })
        );
    }, [content]); // eslint-disable-line react-hooks/exhaustive-deps
    return (
        <div style={{ position: "relative" }}>
            <div ref={ref}>
                <Callout
                    style={{
                        opacity: dragging ? 0.54 : 1,
                        padding: 0,
                        overflow: "hidden",
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            cursor: "pointer",
                            padding: `10px 20px ${
                                !isCollapsed &&
                                !dragging &&
                                !_.isEqual(contentType, "JSON_FORM")
                                    ? 0
                                    : 10
                            }px 10px`,
                        }}
                        onClick={() =>
                            appActions.session.toggleWorkspaceCollapse({
                                stream,
                            })
                        }
                    >
                        <Tag
                            intent={Intent.PRIMARY}
                            size="large"
                            minimal
                            style={{ backgroundColor: "transparent" }}
                            icon={faIcon({ icon: faMessage })}
                        >
                            Message
                        </Tag>
                        {!dragging && (
                            <div onClick={(event) => event.stopPropagation()}>
                                <ButtonGroup variant="minimal" size="large">
                                    <Tooltip
                                        placement="bottom"
                                        minimal
                                        content="Remove"
                                    >
                                        <Button
                                            onClick={() =>
                                                appActions.session.removeWorkspaceContent(
                                                    index
                                                )
                                            }
                                            icon={faIcon({ icon: faTrash })}
                                        />
                                    </Tooltip>
                                    <Button
                                        style={{ pointerEvents: "none" }}
                                        icon={faIcon({
                                            icon: isCollapsed
                                                ? faChevronDown
                                                : faChevronUp,
                                        })}
                                    />
                                </ButtonGroup>
                            </div>
                        )}
                    </div>
                    <Collapse
                        keepChildrenMounted
                        isOpen={!isCollapsed && !dragging}
                    >
                        <div
                            className={loading ? Classes.SKELETON : null}
                            style={{
                                overflowX: "auto",
                                position: "relative",
                                whiteSpace: "pre-wrap",
                                wordBreak: "break-word",
                                padding: "15px 20px",
                            }}
                        >
                            {hasError.current ? (
                                <Callout
                                    intent={Intent.DANGER}
                                    icon={null}
                                    title="Unable to display the content"
                                >
                                    We&apos;re unable to parse the source data
                                    of this content
                                </Callout>
                            ) : (
                                <MessageContent
                                    contentType={contentType}
                                    streamData={streamData}
                                    hasError={hasError}
                                />
                            )}
                        </div>
                    </Collapse>
                </Callout>
            </div>
            {_.isEqual(state.type, "isDraggingOver") && state.closestEdge ? (
                <DropIndicator edge={state.closestEdge} gap="20px" />
            ) : null}
        </div>
    );
}
