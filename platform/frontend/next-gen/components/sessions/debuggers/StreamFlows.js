import { REACT_FLOW_NODE } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Tooltip,
} from "@blueprintjs/core";
import { faExpand } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { Background, Panel, ReactFlow, useReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import _ from "lodash";
import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useShallow } from "zustand/react/shallow";
import AgentNode from "./react-flow/AgentNode";
import StreamNode from "./react-flow/StreamNode";
import TransitionNode from "./react-flow/TransitionNode";
const NODE_TYPES = {
    stream: StreamNode,
    agent: AgentNode,
    transitionNode: TransitionNode,
};
const getNodeDimension = (node) => {
    const label = _.get(node, "data.label", "");
    const nodeType = _.get(node, "type", null);
    if (_.includes(["agent", "stream"], nodeType)) {
        const padding = REACT_FLOW_NODE["padding"] * 2;
        return {
            nodeWidth: Math.min(400, 9 * _.size(label) + padding),
            nodeHeight: 48 + padding,
        };
    } else if (_.isEqual(nodeType, "transitionNode")) {
        const transitionNodePadding =
            REACT_FLOW_NODE["transitionNodePadding"] * 2;
        return {
            nodeWidth: 7.5 * _.size(label) + 12 + transitionNodePadding,
            nodeHeight: 20 + transitionNodePadding,
        };
    }
};
const getLayoutedElements = (nodes, edges, direction = "LR") => {
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
            // we are shifting the dagre node position (anchor=center center) to the top left
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
export default function StreamFlows({ sessionId }) {
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const { fitView } = useReactFlow();
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], {}),
        }))
    );
    const { messages } = session;
    useEffect(() => {
        const nodes = [];
        const edges = [];
        const seenNodeIds = new Set();
        const seenEdges = new Set();
        for (let i = 0; i < _.size(messages); i++) {
            const { stream, timestamp, metadata, contentType } = messages[i];
            const streamNodeId = `stream_${stream}`;
            if (!seenNodeIds.has(streamNodeId)) {
                nodes.push({
                    id: streamNodeId,
                    type: "stream",
                    data: { label: stream, timestamp, metadata, contentType },
                });
                seenNodeIds.add(streamNodeId);
            }
            // consumers
            const consumers = _.keys(
                _.get(messages, [i, "metadata", "consumers"], {})
            ).filter((key) => !_.startsWith(key, "OBSERVER:"));
            for (let j = 0; j < _.size(consumers); j++) {
                const agent = consumers[j];
                const consumerNodeId = `consumer_${agent}`;
                if (!seenNodeIds.has(consumerNodeId)) {
                    nodes.push({
                        id: consumerNodeId,
                        type: "agent",
                        data: {
                            label: agent,
                            consumer: true,
                            timestamp,
                            metadata,
                            contentType,
                        },
                    });
                    seenNodeIds.add(consumerNodeId);
                }
                // create edge: stream -> consumer
                const edge = `edge_${streamNodeId}_${consumerNodeId}`;
                if (!seenEdges.has(edge)) {
                    const transitionNodeId = uuidv4();
                    nodes.push({
                        id: transitionNodeId,
                        data: { label: "consumed by" },
                        type: "transitionNode",
                    });
                    edges.push({
                        id: `edge_${streamNodeId}_${transitionNodeId}`,
                        source: streamNodeId,
                        target: transitionNodeId,
                        animated: true,
                        type: "smoothstep",
                        style: { strokeWidth: 2 },
                    });
                    edges.push({
                        id: `edge_${transitionNodeId}_${consumerNodeId}`,
                        source: transitionNodeId,
                        target: consumerNodeId,
                        animated: true,
                        type: "smoothstep",
                        style: { strokeWidth: 2 },
                    });
                    seenEdges.add(edge);
                }
            }
            // producers
            const producers = _.keys(
                _.get(messages, [i, "metadata", "producers"], {})
            );
            for (let j = 0; j < _.size(producers); j++) {
                const agent = producers[j];
                const producerNodeId = `producer_${agent}`;
                if (!seenNodeIds.has(producerNodeId)) {
                    nodes.push({
                        id: producerNodeId,
                        type: "agent",
                        data: {
                            label: agent,
                            producer: true,
                            timestamp,
                            metadata,
                            contentType,
                        },
                    });
                    seenNodeIds.add(producerNodeId);
                }
                // create edge: producer -> stream
                const edge = `edge_${producerNodeId}_${streamNodeId}`;
                if (!seenEdges.has(edge)) {
                    const transitionNodeId = uuidv4();
                    nodes.push({
                        id: transitionNodeId,
                        data: { label: "produced" },
                        type: "transitionNode",
                    });
                    edges.push({
                        id: `edge_${producerNodeId}_${transitionNodeId}`,
                        source: producerNodeId,
                        target: transitionNodeId,
                        animated: true,
                        type: "smoothstep",
                        style: { strokeWidth: 2 },
                    });
                    edges.push({
                        id: `edge_${transitionNodeId}_${streamNodeId}`,
                        source: transitionNodeId,
                        target: streamNodeId,
                        animated: true,
                        type: "smoothstep",
                        style: { strokeWidth: 2 },
                    });
                    seenEdges.add(edge);
                }
            }
        }
        const { nodes: layoutedNodes, edges: layoutedEdges } =
            getLayoutedElements(nodes, edges);
        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
    }, [messages]);
    return (
        <div className="full-parent-dimension">
            <ReactFlow
                elevateEdgesOnSelect
                fitView
                nodesDraggable={false}
                nodesConnectable={false}
                nodesFocusable={false}
                nodes={nodes}
                edges={edges}
                nodeTypes={NODE_TYPES}
            >
                <Background />
                <Panel position="top-left">
                    <Card style={{ padding: 5 }}>
                        <ButtonGroup vertical variant={ButtonVariant.MINIMAL}>
                            <Tooltip content="Fit view" placement="right">
                                <Button
                                    onClick={() => {
                                        fitView({ duration: 300 });
                                    }}
                                    icon={<FAIcon icon={faExpand} />}
                                />
                            </Tooltip>
                        </ButtonGroup>
                    </Card>
                </Panel>
            </ReactFlow>
        </div>
    );
}
