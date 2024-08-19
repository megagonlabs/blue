import {
    Button,
    ButtonGroup,
    Card,
    Dialog,
    DialogBody,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCompassDrafting,
    faExpand,
} from "@fortawesome/pro-duotone-svg-icons";
import { Background, Panel, ReactFlow, useReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import _ from "lodash";
import { useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
import AgentNode from "./visualization/AgentNode";
import TransitionEdgeNode from "./visualization/TransitionEdgeNode";
const getNodeDimension = (node) => {
    if (_.isEqual(node.type, "agent-node")) {
        const label = _.get(node, "data.label", "");
        const NODE_PADDING = 10;
        return {
            nodeWidth: 8.45 * _.size(label) + NODE_PADDING * 2 + 40 + 15,
            nodeHeight: 40 + NODE_PADDING * 2,
        };
    } else if (_.isEqual(node.type, "transition-edge-node")) {
        const fromParam = _.get(node, "data.fromParam", null);
        const toParam = _.get(node, "data.toParam", null);
        return {
            nodeWidth:
                Math.max(_.size(fromParam), _.size(toParam)) * 10 + 12 + 10,
            nodeHeight: 55,
        };
    }
};
const getLayoutedElements = (nodes, edges, direction = "TB") => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    const isHorizontal = _.isEqual(direction, "LR");
    dagreGraph.setGraph({ rankdir: direction });
    for (let i = 0; i < _.size(nodes); i++) {
        const node = nodes[i];
        const { nodeWidth, nodeHeight } = getNodeDimension(node);
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
        _.set(nodes, [i, "style", "width"], nodeWidth);
        _.set(nodes, [i, "style", "height"], nodeHeight);
    }
    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });
    dagre.layout(dagreGraph);
    const newNodes = nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        const { nodeWidth, nodeHeight } = getNodeDimension(node);
        const newNode = {
            ...node,
            targetPosition: isHorizontal ? "left" : "top",
            sourcePosition: isHorizontal ? "right" : "bottom",
            // We are shifting the dagre node position (anchor=center center) to the top left
            // so it matches the React Flow node anchor point (top left).
            position: {
                x: nodeWithPosition.x - nodeWidth / 2,
                y: nodeWithPosition.y - nodeHeight / 2,
            },
        };
        return newNode;
    });
    return { nodes: newNodes, edges };
};
const TRANSITION_OPTION = { duration: 300 };
export default function PlanVisualizationPanel() {
    const { fitView } = useReactFlow();
    const { appState, appActions } = useContext(AppContext);
    const initialNodes = _.get(appState, "session.visualization.nodes", []);
    const initialEdges = _.get(appState, "session.visualization.edges", []);
    const [loading, setLoading] = useState(false);
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const nodeTypes = {
        "agent-node": AgentNode,
        "transition-edge-node": TransitionEdgeNode,
    };
    return (
        <Dialog
            onOpening={() => {
                setLoading(true);
            }}
            onOpened={() => {
                const { nodes: layoutedNodes, edges: layoutedEdges } =
                    getLayoutedElements(initialNodes, initialEdges);
                setNodes(layoutedNodes);
                setEdges(layoutedEdges);
                setLoading(false);
            }}
            onClose={() => {
                appActions.session.setState({
                    key: "visualization",
                    value: null,
                });
                setNodes([]);
                setEdges([]);
            }}
            isOpen={!_.isEmpty(initialNodes)}
            style={{ width: "100%", maxWidth: 795 }}
        >
            <DialogBody className="dialog-body">
                <div style={{ height: 500, width: "100%", padding: 15 }}>
                    <ReactFlow
                        nodeTypes={nodeTypes}
                        nodesDraggable={false}
                        nodesConnectable={false}
                        nodesFocusable={false}
                        fitView
                        nodes={nodes}
                        edges={edges}
                    >
                        <Background />
                        <Panel position="top-left">
                            {loading ? (
                                faIcon({
                                    icon: faCompassDrafting,
                                    className: "fa-fade",
                                    style: { color: "#999" },
                                    size: 40,
                                })
                            ) : (
                                <Card style={{ padding: 5 }}>
                                    <ButtonGroup vertical minimal>
                                        <Tooltip
                                            content="Fit view"
                                            minimal
                                            placement="right"
                                        >
                                            <Button
                                                onClick={() => {
                                                    fitView(TRANSITION_OPTION);
                                                }}
                                                icon={faIcon({
                                                    icon: faExpand,
                                                })}
                                            />
                                        </Tooltip>
                                    </ButtonGroup>
                                </Card>
                            )}
                        </Panel>
                    </ReactFlow>
                </div>
            </DialogBody>
        </Dialog>
    );
}
