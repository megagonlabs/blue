import { useSessionStore } from "@/stores/session-store";
import { extractClosestEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge";
import { monitorForElements } from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    NonIdealState,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faBan, faLampDesk } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import { EMPTY_ARRAY, WORKSAPCE_DRAGGABLE_SYMBOL } from "../constants";
import WorkspaceMessage from "./workspace/WorkspaceMessage";
export default function Workspace({ sessionId }) {
    const { reorderWorkspace, clearWorkspace, contents } = useSessionStore(
        useShallow((state) => ({
            contents: _.get(
                state,
                ["sessions", sessionId, "workspace"],
                EMPTY_ARRAY
            ),
            reorderWorkspace: state.reorderWorkspace,
            clearWorkspace: state.clearWorkspace,
        }))
    );
    const [extraPadding, setExtraPadding] = useState(false);
    useEffect(() => {
        return monitorForElements({
            canMonitor({ source }) {
                return source.data[WORKSAPCE_DRAGGABLE_SYMBOL];
            },
            onDrop({ location, source }) {
                const target = location.current.dropTargets[0];
                if (!target) return;
                const sourceData = source.data;
                const targetData = target.data;
                if (
                    !sourceData[WORKSAPCE_DRAGGABLE_SYMBOL] ||
                    !targetData[WORKSAPCE_DRAGGABLE_SYMBOL]
                )
                    return;
                const indexOfSource = sourceData.index;
                const indexOfTarget = targetData.index;
                if (indexOfSource < 0 || indexOfTarget < 0) return;
                const closestEdgeOfTarget = extractClosestEdge(targetData);
                reorderWorkspace({
                    sessionId,
                    indexOfSource,
                    indexOfTarget,
                    closestEdgeOfTarget,
                });
            },
        });
    }, [contents, reorderWorkspace]);
    if (_.isEmpty(contents)) {
        return (
            <NonIdealState
                icon={<FAIcon icon={faLampDesk} size={50} />}
                title="Workspace"
            />
        );
    }
    return (
        <>
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip content="Clear workspace" placement="bottom-start">
                        <Button
                            onClick={() => {
                                clearWorkspace(sessionId);
                            }}
                            icon={
                                <FAIcon
                                    icon={faBan}
                                    className="fa-rotate-by"
                                    style={{ "--fa-rotate-angle": "90deg" }}
                                />
                            }
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div
                className="full-parent-dimension"
                style={{
                    maxHeight: "calc(100% - 61px)",
                    overflowY: "auto",
                    padding: `${extraPadding ? 20 : 10}px 20px`,
                }}
            >
                {contents.map((content, index) => {
                    const { type } = content;
                    if (_.isEqual(type, "session")) {
                        return (
                            <div
                                key={index}
                                style={{ marginTop: index > 0 ? 20 : 0 }}
                            >
                                <WorkspaceMessage
                                    setExtraPadding={setExtraPadding}
                                    sessionId={sessionId}
                                    content={content}
                                    index={index}
                                />
                            </div>
                        );
                    }
                    return null;
                })}
            </div>
        </>
    );
}
