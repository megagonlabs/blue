import { WORKSAPCE_DRAGGABLE_SYMBOL } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { useSessionStore } from "@/stores/session-store";
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
    ButtonVariant,
    Callout,
    Card,
    Classes,
    Collapse,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faMessage, faTrash } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import invariant from "tiny-invariant";
import MessageContent from "../messages/MessageContent";
const IDLE_STATE = { type: "idle" };
export default function WorkspaceMessage({ sessionId, content, index }) {
    const dragging = useRef(false);
    const [state, setState] = useState(IDLE_STATE);
    const dragData = { index, [WORKSAPCE_DRAGGABLE_SYMBOL]: true };
    const ref = useRef(null);
    const loading = _.get(content, "loading", false);
    const hasError = useRef(false);
    const streams = useSessionStore((state) =>
        _.get(state, ["sessions", sessionId, "streams"], {})
    );
    const stream = _.get(content, "message.stream", null);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(content, "message.contentType", null);
    useEffect(() => {
        const element = ref.current;
        invariant(element);
        return combine(
            draggable({
                element: element,
                getInitialData: () => dragData,
                onDragStart: () => (dragging.current = true),
                onDrop: () => (dragging.current = false),
                onGenerateDragPreview: ({ nativeSetDragImage }) => {
                    setCustomNativeDragPreview({
                        getOffset: pointerOutsideOfPreview({
                            x: "20px",
                            y: "0px",
                        }),
                        render: ({ container }) => {
                            const root = createRoot(container);
                            root.render(
                                <div>
                                    <Card
                                        style={{
                                            maxWidth: 200,
                                            maxHeight: 200,
                                            overflow: "hidden",
                                        }}
                                        className={
                                            Classes.TEXT_OVERFLOW_ELLIPSIS
                                        }
                                    >
                                        <MessageContent
                                            isPreview={true}
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
                    if (_.isEqual(source.element, element)) {
                        return false;
                    }
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
                    // only need to update react state if nothing has changed.
                    // prevents re-rendering.
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
    }, [content]);
    return (
        <div style={{ position: "relative" }}>
            <div ref={ref}>
                <Callout style={{ padding: 0, overflow: "hidden" }}>
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "10px 20px 10px 10px",
                        }}
                    >
                        <Tag
                            minimal
                            style={{ backgroundColor: "transparent" }}
                            intent={Intent.PRIMARY}
                            size={Size.LARGE}
                            icon={<FAIcon icon={faMessage} />}
                        >
                            Message
                        </Tag>
                        <div>
                            <ButtonGroup
                                variant={ButtonVariant.MINIMAL}
                                size={Size.LARGE}
                            >
                                <Tooltip content="Remove" placement="bottom">
                                    <Button icon={<FAIcon icon={faTrash} />} />
                                </Tooltip>
                            </ButtonGroup>
                        </div>
                    </div>
                    <Collapse keepChildrenMounted isOpen={!dragging.current}>
                        <div
                            className={loading ? Classes.SKELETON : null}
                            style={{ padding: "0px 20px 20px" }}
                        >
                            {hasError.current ? (
                                <Callout>
                                    Unable to parse the source data of this
                                    content
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
            {_.isEqual(state.type, "isDraggingOver") && state.closestEdge && (
                <DropIndicator edge={state.closestEdge} gap="20px" />
            )}
        </div>
    );
}
