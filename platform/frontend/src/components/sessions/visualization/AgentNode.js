import { Card } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
export default function AgentNode({ data }) {
    return (
        <Card style={{ padding: 10, fontFamily: "monospace, monospace" }}>
            {_.get(data, "output", false) ? (
                <Handle type="target" position={Position.Top} />
            ) : null}
            {data.label}
            {_.get(data, "input", false) ? (
                <Handle type="source" position={Position.Bottom} />
            ) : null}
        </Card>
    );
}
