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
    Card,
    Classes,
    Intent,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import { faMessage, faTrash } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import invariant from "tiny-invariant";
export default function MessageSnapshot({ content, hasError, index }) {
    const ref = useRef(null);
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    const stream = _.get(content, "message.stream", null);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(content, "message.contentType", null);
    const [dragging, setDragging] = useState(false);
    const IDLE_STATE = { type: "idle" };
    const [state, setState] = useState(IDLE_STATE);
    const dragData = { index, [WORKSAPCE_DRAGGABLE_SYMBOL]: true };
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
    }, [content]);
    return (
        <div style={{ position: "relative" }}>
            <Section
                ref={ref}
                collapseProps={{
                    isOpen:
                        !_.get(
                            appState,
                            ["session", "sessionWorkspaceCollapse", stream],
                            true
                        ) && !dragging,
                    onToggle: () =>
                        appActions.session.toggleWorkspaceCollapse(stream),
                }}
                style={{ opacity: dragging ? 0.54 : 1 }}
                collapsible
                title="Message"
                icon={faIcon({ icon: faMessage })}
                compact
                rightElement={
                    !dragging && (
                        <div onClick={(event) => event.stopPropagation()}>
                            <Popover
                                content={
                                    <div style={{ padding: 15 }}>
                                        <Button
                                            intent={Intent.DANGER}
                                            className={Classes.POPOVER_DISMISS}
                                            text="Confirm"
                                            onClick={() =>
                                                appActions.session.removeWorkspaceContent(
                                                    index
                                                )
                                            }
                                        />
                                    </div>
                                }
                                placement="bottom"
                            >
                                <Tooltip
                                    placement="bottom"
                                    minimal
                                    content="Remove"
                                >
                                    <Button
                                        minimal
                                        intent={Intent.DANGER}
                                        icon={faIcon({ icon: faTrash })}
                                    />
                                </Tooltip>
                            </Popover>
                        </div>
                    )
                }
            >
                <SectionCard
                    style={{
                        overflowX: "auto",
                        position: "relative",
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-all",
                    }}
                >
                    <MessageContent
                        contentType={contentType}
                        streamData={streamData}
                        hasError={hasError}
                    />
                </SectionCard>
            </Section>
            {_.isEqual(state.type, "isDraggingOver") && state.closestEdge ? (
                <DropIndicator edge={state.closestEdge} gap="20px" />
            ) : null}
        </div>
    );
}
