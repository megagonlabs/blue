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
import _ from "lodash";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
const initialNodes = [
    { id: "n1", position: { x: 0, y: 0 }, data: { label: "Node 1" } },
    { id: "n2", position: { x: 0, y: 100 }, data: { label: "Node 2" } },
];
const initialEdges = [{ id: "n1-n2", source: "n1", target: "n2" }];
export default function StreamFlows({ sessionId }) {
    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);
    const { fitView } = useReactFlow();
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], {}),
        }))
    );
    const { messages } = session;
    // const temp = [
    //     {
    //         id: "A",
    //         type: "group",
    //         data: { label: null },
    //         position: { x: 0, y: 0 },
    //         style: {
    //             width: 170,
    //             height: 140,
    //         },
    //     },
    //     {
    //         id: "B",
    //         type: "input",
    //         data: { label: "child node 1" },
    //         position: { x: 10, y: 10 },
    //         parentId: "A",
    //         extent: "parent",
    //     },
    //     {
    //         id: "C",
    //         data: { label: "child node 2" },
    //         position: { x: 10, y: 90 },
    //         parentId: "A",
    //         extent: "parent",
    //     },
    // ];
    useEffect(() => {
        let nextNodes = {};
        let nextEdges = {};
        for (let i = 0; i < _.size(messages); i++) {
            const consumers = _.entries(
                _.get(messages[i], "metadata.consumers", {})
            ).filter((entry) => !_.startsWith(entry[0], "OBSERVER:"));
            const producers = _.entries(
                _.get(messages[i], "metadata.producers", {})
            );
            // for (let j = 0; j < _.size(consumers); j++) {}
            // for (let j = 0; j < _.size(producers); j++) {}
            console.log(consumers, producers);
        }
    }, [messages]);
    return (
        <div className="full-parent-dimension">
            <ReactFlow
                fitView
                nodesDraggable={false}
                nodesConnectable={false}
                nodesFocusable={false}
                nodes={nodes}
                edges={edges}
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
