import { MIN_ALLOTMENT_PANE_SIZE } from "@/components/constants";
import { ReactFlowCustomProvider } from "@/components/contexts/ReactFlowCustomContext";
import { useToaster } from "@/components/contexts/ToasterContext";
import { FAIcon } from "@/components/FAIcon";
import { getReactFlowLayoutedElements } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Colors,
    Divider,
    NonIdealState,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowLeftArrowRight,
    faArrowsMaximize,
    faArrowUpArrowDown,
    faClipboard,
    faCompassDrafting,
    faDownload,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import {
    Background,
    getConnectedEdges,
    Panel,
    ReactFlow,
    useReactFlow,
    useStore,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Allotment } from "allotment";
import axios from "axios";
import copy from "copy-to-clipboard";
import _, { debounce } from "lodash";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useShallow } from "zustand/react/shallow";
import MessageViewer from "./MessageViewer";
import AgentNode from "./react-flow/AgentNode";
import StreamNode from "./react-flow/StreamNode";
import TagNode from "./react-flow/TagNode";
const NODE_TYPES = {
    stream: StreamNode,
    agent: AgentNode,
    tag: TagNode,
};
const traverseAndFindEdges = (
    startNode,
    allEdges,
    allNodes,
    targetNodeTypes,
    setSelectedNodes
) => {
    const visitedEdges = new Set();
    const queue = [startNode];
    const visitedNodes = new Set();
    visitedNodes.add(startNode.id);
    const selectedNodes = new Set();
    while (queue.length > 0) {
        const currentNode = queue.shift();
        const connectedEdges = getConnectedEdges([currentNode], allEdges);
        connectedEdges.forEach((edge) => {
            if (!visitedEdges.has(edge.id)) {
                const nextNodeId = _.isEqual(edge.source, currentNode.id)
                    ? edge.target
                    : edge.source;
                const nextNode = allNodes.find((n) =>
                    _.isEqual(n.id, nextNodeId)
                );
                if (nextNode && _.includes(targetNodeTypes, nextNode.type)) {
                    selectedNodes.add(nextNodeId);
                    visitedEdges.add(edge.id);
                } else if (nextNode && !visitedNodes.has(nextNodeId)) {
                    visitedEdges.add(edge.id);
                    visitedNodes.add(nextNodeId);
                    queue.push(nextNode);
                }
            }
        });
    }
    setSelectedNodes(selectedNodes);
    return Array.from(visitedEdges);
};
const selector = (state) => ({ edges: state.edges, nodes: state.nodes });
export default function StreamFlows({ sessionId }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const [direction, setDirection] = useState("TB");
    const [selectedEdges, setSelectedEdges] = useState(new Set());
    const [selectedNodes, setSelectedNodes] = useState(new Set());
    const [clickedNode, setClickedNode] = useState(null);
    const { edges: latestEdges, nodes: latestNodes } = useStore(selector);
    const onEdgeClick = useCallback((event, edge) => {
        setSelectedEdges((prevSelected) => {
            const newSelected = new Set(prevSelected);
            newSelected.delete(edge.id);
            return newSelected;
        });
    }, []);
    const { fitView, getNodes, getEdges, setViewport } = useReactFlow();
    const initialRender = useRef(true);
    const [lastViewport, setLastViewport] = useState(null);
    const [nodeInfo, setNodeInfo] = useState(null);
    const onNodeClick = useCallback(
        (event, node) => {
            if (node.type === "stream") {
                setNodeInfo({
                    type: node.type,
                    ...node.data,
                    stream: node.data.label,
                });
            }
            const targetNodeTypes = ["stream", "agent"];
            const foundEdges = traverseAndFindEdges(
                node,
                latestEdges,
                latestNodes,
                targetNodeTypes,
                setSelectedNodes
            );
            setClickedNode(node);
            setSelectedEdges(new Set(foundEdges));
        },
        [latestEdges, latestNodes]
    );
    useEffect(() => {
        setEdges((prevEdges) =>
            prevEdges.map((edge) => {
                const isSelected = selectedEdges.has(edge.id);
                const defaultStyle = { strokeWidth: 2 };
                return {
                    ...edge,
                    style: isSelected
                        ? { ...defaultStyle, stroke: "#2D72D2", strokeWidth: 4 }
                        : defaultStyle,
                    zIndex: isSelected ? 1000 : null,
                };
            })
        );
    }, [selectedEdges]);
    const [measuredDimensions, setMeasuredDimensions] = useState({});
    const nodesWithKnownDimensions = _.keys(measuredDimensions);
    const handleNodeDimensionsChange = useCallback((nodeId, width, height) => {
        setMeasuredDimensions((prev) => ({
            ...prev,
            [nodeId]: { width, height },
        }));
    }, []);
    const [layoutInitialized, setLayoutInitialized] = useState(false);
    const { appToaster } = useToaster();
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
                direction
            );
            setNodes(layoutedNodes);
            if (lastViewport && !initialRender.current) {
                setViewport(lastViewport);
            } else {
                setTimeout(() => {
                    fitView();
                }, 300);
            }
            initialRender.current = false;
            setTimeout(() => {
                setLayoutInitialized(true);
            }, 300);
        }
    }, [
        nodesWithKnownDimensions.length,
        direction,
        getNodes,
        getEdges,
        setNodes,
        layoutInitialized,
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
    const currentStreamDebugger = useRef({});
    const [streamDebugger, setStreamDebugger] = useState({});
    const handleViewportChange = useCallback(
        (event, viewport) => {
            if (layoutInitialized) {
                setLastViewport(viewport);
            }
        },
        [layoutInitialized]
    );
    const getSessionDebugger = useCallback(
        debounce(() => {
            axios
                .get(`/sessions/session/${sessionId}/debugger`)
                .then((response) => {
                    const results = _.get(response, "data.results", {});
                    if (!_.isEqual(currentStreamDebugger.current, results)) {
                        currentStreamDebugger.current = results;
                        setStreamDebugger(results);
                    }
                });
        }, 5000),
        []
    );
    useEffect(() => {
        getSessionDebugger();
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
                _.merge(
                    _.get(metadata, "consumers", {}),
                    _.get(streamDebugger, [stream, "consumers"], {})
                )
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
                    _.set(
                        nodes,
                        [nodeIndex[streamNodeId], "data", "consumed"],
                        true
                    );
                }
            }
            // producers
            const producers = _.keys(
                _.merge(
                    _.get(metadata, "producers", {}),
                    _.get(streamDebugger, [stream, "producers"], {})
                )
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
        setLayoutInitialized(false);
    }, [messages, streamDebugger]);
    return (
        <div className="full-parent-dimension" style={{ position: "relative" }}>
            <Allotment
                separator={!_.isEmpty(nodeInfo)}
                defaultSizes={[800, 400]}
            >
                <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                    {!layoutInitialized && (
                        <div
                            className="full-parent-dimension"
                            style={{
                                position: "absolute",
                                top: 0,
                                left: 0,
                                backgroundColor: darkMode
                                    ? Colors.BLACK
                                    : Colors.WHITE,
                                zIndex: 1,
                            }}
                        >
                            <NonIdealState
                                title={
                                    _.isEmpty(nodes) ? "No Data" : "Rendering"
                                }
                                icon={
                                    <FAIcon
                                        size={50}
                                        className={
                                            !_.isEmpty(nodes) && "fa-fade"
                                        }
                                        icon={faCompassDrafting}
                                    />
                                }
                            />
                        </div>
                    )}
                    <ReactFlowCustomProvider
                        value={{ direction, selectedNodes, clickedNode }}
                    >
                        <ReactFlow
                            elevateEdgesOnSelect
                            fitView
                            onMove={handleViewportChange}
                            nodesDraggable={false}
                            nodesConnectable={false}
                            nodesFocusable={false}
                            edgesFocusable={false}
                            nodes={nodesWithHandlers}
                            onNodeClick={onNodeClick}
                            onEdgeClick={onEdgeClick}
                            edges={edges}
                            nodeTypes={NODE_TYPES}
                        >
                            <Background />
                            <Panel position="top-left">
                                <Card style={{ padding: 5 }}>
                                    <ButtonGroup
                                        size={Size.LARGE}
                                        vertical
                                        variant={ButtonVariant.MINIMAL}
                                    >
                                        <Tooltip
                                            content="Fit view"
                                            placement="right"
                                        >
                                            <Button
                                                onClick={() => {
                                                    fitView({ duration: 300 });
                                                }}
                                                icon={
                                                    <FAIcon
                                                        icon={faArrowsMaximize}
                                                    />
                                                }
                                            />
                                        </Tooltip>
                                        <Tooltip
                                            content="Direction"
                                            placement="right"
                                        >
                                            <Button
                                                onClick={() => {
                                                    setDirection(
                                                        _.isEqual(
                                                            direction,
                                                            "TB"
                                                        )
                                                            ? "LR"
                                                            : "TB"
                                                    );
                                                    setTimeout(() => {
                                                        fitView();
                                                    }, 0);
                                                }}
                                                icon={
                                                    <FAIcon
                                                        icon={
                                                            _.isEqual(
                                                                direction,
                                                                "TB"
                                                            )
                                                                ? faArrowUpArrowDown
                                                                : faArrowLeftArrowRight
                                                        }
                                                    />
                                                }
                                            />
                                        </Tooltip>
                                        <Divider />
                                        <Tooltip
                                            content="Export"
                                            placement="right"
                                        >
                                            <Button
                                                onClick={() => {
                                                    copy(
                                                        JSON.stringify({
                                                            nodes: nodesWithHandlers,
                                                            edges,
                                                        })
                                                    );
                                                    appToaster.show({
                                                        icon: (
                                                            <FAIcon
                                                                icon={
                                                                    faClipboard
                                                                }
                                                            />
                                                        ),
                                                        message:
                                                            "Copied nodes and edges",
                                                    });
                                                }}
                                                icon={
                                                    <FAIcon icon={faDownload} />
                                                }
                                            />
                                        </Tooltip>
                                    </ButtonGroup>
                                </Card>
                            </Panel>
                        </ReactFlow>
                    </ReactFlowCustomProvider>
                </Allotment.Pane>
                <Allotment.Pane
                    visible={!_.isEmpty(nodeInfo)}
                    minSize={MIN_ALLOTMENT_PANE_SIZE}
                >
                    <div className="border-bottom" style={{ padding: 10 }}>
                        <Button
                            variant={ButtonVariant.MINIMAL}
                            size={Size.LARGE}
                            onClick={() => {
                                setNodeInfo(null);
                            }}
                            icon={<FAIcon icon={faXmarkLarge} />}
                        />
                    </div>
                    <MessageViewer
                        sessionId={sessionId}
                        message={nodeInfo}
                        showFullContent={true}
                    />
                </Allotment.Pane>
            </Allotment>
        </div>
    );
}
