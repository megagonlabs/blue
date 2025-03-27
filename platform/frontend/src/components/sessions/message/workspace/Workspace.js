import { WORKSAPCE_DRAGGABLE_SYMBOL } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageSnapshot from "@/components/sessions/message/workspace/MessageSnapshot";
import { extractClosestEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge";
import { monitorForElements } from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import {
    Button,
    ButtonGroup,
    Divider,
    NonIdealState,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsToLine,
    faBan,
    faLampDesk,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect } from "react";
export default function Workspace() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionWorkspace, sessionIdFocus } = appState.session;
    const contents = _.get(sessionWorkspace, sessionIdFocus, []);
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
                appActions.session.reorderWorkspace({
                    indexOfSource,
                    indexOfTarget,
                    closestEdgeOfTarget,
                });
            },
        });
    }, [contents]); // eslint-disable-line react-hooks/exhaustive-deps
    if (_.isEmpty(contents)) {
        return (
            <NonIdealState
                icon={faIcon({ icon: faLampDesk, size: 50 })}
                title="Workspace"
            />
        );
    }
    return (
        <div className="full-parent-height">
            <div className="border-bottom" style={{ padding: "5px 20px" }}>
                <ButtonGroup size="large" variant="minimal">
                    <Tooltip
                        minimal
                        content="Clear workspace"
                        placement="bottom-start"
                    >
                        <Button
                            onClick={() =>
                                appActions.session.clearCurrentWorkspace()
                            }
                            icon={faIcon({
                                icon: faBan,
                                className: "fa-rotate-by",
                                style: { "--fa-rotate-angle": "90deg" },
                            })}
                        />
                    </Tooltip>
                    <Divider />
                    <Tooltip content="Collapse all" minimal placement="bottom">
                        <Button
                            icon={faIcon({ icon: faArrowsToLine })}
                            variant="minimal"
                            onClick={() =>
                                appActions.session.collapseAllWorkspace(
                                    sessionIdFocus
                                )
                            }
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div
                style={{
                    padding: 20,
                    overflowY: "auto",
                    height: "calc(100% - 51px)",
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
                                <MessageSnapshot
                                    index={index}
                                    content={content}
                                />
                            </div>
                        );
                    }
                    return null;
                })}
            </div>
        </div>
    );
}
