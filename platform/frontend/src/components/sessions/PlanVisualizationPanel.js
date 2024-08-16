import { Dialog, DialogBody } from "@blueprintjs/core";
import { faCompassDrafting } from "@fortawesome/pro-duotone-svg-icons";
import { Background, Panel, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import _ from "lodash";
import { useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
import AgentParamEdge from "./visualization/AgentParamEdge";
const getLayoutedElements = (nodes, edges, direction = "TB") => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    const NODE_WIDTH = 150;
    const NODE_HEIGHT = 75;
    const isHorizontal = _.isEqual(direction, "LR");
    dagreGraph.setGraph({ rankdir: direction });
    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
    });
    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });
    dagre.layout(dagreGraph);
    const newNodes = nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        const newNode = {
            ...node,
            targetPosition: isHorizontal ? "left" : "top",
            sourcePosition: isHorizontal ? "right" : "bottom",
            // We are shifting the dagre node position (anchor=center center) to the top left
            // so it matches the React Flow node anchor point (top left).
            position: {
                x: nodeWithPosition.x - NODE_WIDTH / 2,
                y: nodeWithPosition.y - NODE_HEIGHT / 2,
            },
        };
        return newNode;
    });
    return { nodes: newNodes, edges };
};
export default function PlanVisualizationPanel() {
    const { appState, appActions } = useContext(AppContext);
    const initialNodes = _.get(appState, "session.visualization.nodes", []);
    const initialEdges = _.get(appState, "session.visualization.edges", []);
    const [loading, setLoading] = useState(false);
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const edgeTypes = {
        "agent-param-edge": AgentParamEdge,
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
                        edgeTypes={edgeTypes}
                        nodesDraggable={false}
                        nodesConnectable={false}
                        nodesFocusable={false}
                        fitView
                        nodes={nodes}
                        edges={edges}
                    >
                        <Background />
                        {loading ? (
                            <Panel position="top-left">
                                {faIcon({
                                    icon: faCompassDrafting,
                                    className: "fa-fade",
                                    style: { color: "#999" },
                                    size: 40,
                                })}
                            </Panel>
                        ) : null}
                    </ReactFlow>
                </div>
            </DialogBody>
        </Dialog>
    );
}
