import { FAIcon } from "@/components/FAIcon";
import { getReactFlowLayoutedElements } from "@/components/helper";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Tooltip,
} from "@blueprintjs/core";
import { faArrowsMaximize } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { Background, Panel, ReactFlow, useReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import _ from "lodash";
import { useCallback, useEffect, useMemo, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useShallow } from "zustand/react/shallow";
import AgentNode from "./react-flow/AgentNode";
import StreamNode from "./react-flow/StreamNode";
import TagNode from "./react-flow/TagNode";
const NODE_TYPES = {
    stream: StreamNode,
    agent: AgentNode,
    tag: TagNode,
};
export default function StreamFlows({ sessionId }) {
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const { fitView, getNodes, getEdges } = useReactFlow();
    const [measuredDimensions, setMeasuredDimensions] = useState({});
    const nodesWithKnownDimensions = _.keys(measuredDimensions);
    const handleNodeDimensionsChange = useCallback((nodeId, width, height) => {
        setMeasuredDimensions((prev) => ({
            ...prev,
            [nodeId]: { width, height },
        }));
    }, []);
    useEffect(() => {
        const allCurrentNodes = getNodes();
        const allNodesMeasured = allCurrentNodes.every((node) => {
            return !!measuredDimensions[node.id];
        });
        if (allNodesMeasured && !_.isEmpty(allCurrentNodes)) {
            const nodesToLayout = allCurrentNodes.map((node) => {
                if (measuredDimensions[node.id]) {
                    return {
                        ...node,
                        width: measuredDimensions[node.id].width,
                        height: measuredDimensions[node.id].height,
                    };
                }
            });
            const { nodes: layoutedNodes } = getReactFlowLayoutedElements(
                nodesToLayout,
                getEdges(),
                "LR"
            );
            setNodes(layoutedNodes);
        }
    }, [
        nodesWithKnownDimensions.length,
        getNodes,
        getEdges,
        setNodes,
        measuredDimensions,
    ]);
    const nodesWithHandlers = useMemo(() => {
        return nodes.map((node) => {
            return {
                ...node,
                data: {
                    ...node.data,
                    onDimensionsChange: handleNodeDimensionsChange,
                },
            };
        });
    }, [nodes, handleNodeDimensionsChange]);
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
        const nodeIndex = {};
        for (let i = 0; i < _.size(messages); i++) {
            const { stream, timestamp, metadata, contentType } = messages[i];
            const streamNodeId = `stream_${stream}`;
            if (!seenNodeIds.has(streamNodeId)) {
                nodes.push({
                    id: streamNodeId,
                    type: "stream",
                    data: {
                        label: stream,
                        timestamp,
                        metadata,
                        contentType,
                        sessionId,
                    },
                });
                seenNodeIds.add(streamNodeId);
                nodeIndex[streamNodeId] = _.size(nodes) - 1;
            }
            // consumers
            const consumers = _.keys(
                _.get(messages, [i, "metadata", "consumers"], {})
            ).filter((key) => !_.startsWith(key, "OBSERVER:"));
            for (let j = 0; j < _.size(consumers); j++) {
                const agent = consumers[j];
                const agentNodeId = `agent_${agent}`;
                if (!seenNodeIds.has(agentNodeId)) {
                    nodes.push({
                        id: agentNodeId,
                        type: "agent",
                        data: { label: agent, consumer: true },
                    });
                    seenNodeIds.add(agentNodeId);
                    nodeIndex[agentNodeId] = _.size(nodes) - 1;
                } else {
                    _.set(
                        nodes,
                        [nodeIndex[agentNodeId], "data", "consumer"],
                        true
                    );
                }
                // create edge: stream -> consumer
                const edge = `edge_${streamNodeId}_${agentNodeId}`;
                if (!seenEdges.has(edge)) {
                    const transitionNodeId = uuidv4();
                    nodes.push({
                        id: transitionNodeId,
                        data: { label: "consumed by" },
                        type: "tag",
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
                        id: `edge_${transitionNodeId}_${agentNodeId}`,
                        source: transitionNodeId,
                        target: agentNodeId,
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
                const agentNodeId = `agent_${agent}`;
                if (!seenNodeIds.has(agentNodeId)) {
                    nodes.push({
                        id: agentNodeId,
                        type: "agent",
                        data: { label: agent, producer: true },
                    });
                    seenNodeIds.add(agentNodeId);
                    nodeIndex[agentNodeId] = _.size(nodes) - 1;
                } else {
                    _.set(
                        nodes,
                        [nodeIndex[agentNodeId], "data", "producer"],
                        true
                    );
                }
                // create edge: producer -> stream
                const edge = `edge_${agentNodeId}_${streamNodeId}`;
                if (!seenEdges.has(edge)) {
                    const transitionNodeId = uuidv4();
                    nodes.push({
                        id: transitionNodeId,
                        data: { label: "produced" },
                        type: "tag",
                    });
                    edges.push({
                        id: `edge_${agentNodeId}_${transitionNodeId}`,
                        source: agentNodeId,
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
            getReactFlowLayoutedElements(nodes, edges);
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
                nodes={nodesWithHandlers}
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
                                    icon={<FAIcon icon={faArrowsMaximize} />}
                                />
                            </Tooltip>
                        </ButtonGroup>
                    </Card>
                </Panel>
            </ReactFlow>
        </div>
    );
}
