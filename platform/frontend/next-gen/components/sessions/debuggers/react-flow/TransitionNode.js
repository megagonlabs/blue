import { Tag } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
export default function TransitionNode({ data }) {
    return (
        <div
            style={{
                padding: 5,
                fontFamily: "monospace, monospace",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-evenly",
            }}
        >
            <Handle type="target" position={Position.Left} />
            <Tag minimal>{_.get(data, "label", null)}</Tag>
            <Handle type="source" position={Position.Right} />
        </div>
    );
}
