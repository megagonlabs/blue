import {
    Button,
    ButtonGroup,
    Colors,
    Dialog,
    DialogBody,
    Tooltip,
} from "@blueprintjs/core";
import { faExpand, faMinus, faPlus } from "@fortawesome/pro-duotone-svg-icons";
import { Background, Panel, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { faIcon } from "../icon";
export default function PlanVisualizationPanel() {
    return (
        <Dialog>
            <DialogBody className="dialog-body">
                <div style={{ height: 500, padding: 15 }}>
                    <ReactFlow fitView>
                        <Background />
                        <Panel
                            position="bottom-left"
                            style={{ backgroundColor: Colors.LIGHT_GRAY5 }}
                        >
                            <ButtonGroup large vertical>
                                <Tooltip
                                    minimal
                                    placement="right"
                                    content="Zoom in"
                                >
                                    <Button
                                        minimal
                                        icon={faIcon({ icon: faPlus })}
                                    />
                                </Tooltip>
                                <Tooltip
                                    minimal
                                    placement="right"
                                    content="Zoom out"
                                >
                                    <Button
                                        minimal
                                        icon={faIcon({ icon: faMinus })}
                                    />
                                </Tooltip>
                                <Tooltip
                                    minimal
                                    placement="right"
                                    content="Fit view"
                                >
                                    <Button
                                        minimal
                                        icon={faIcon({ icon: faExpand })}
                                    />
                                </Tooltip>
                            </ButtonGroup>
                        </Panel>
                    </ReactFlow>
                </div>
            </DialogBody>
        </Dialog>
    );
}
