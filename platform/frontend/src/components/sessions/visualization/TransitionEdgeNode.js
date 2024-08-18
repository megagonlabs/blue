import { Tag } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
export default function TransitionEdgeNode({ data }) {
    return (
        <>
            <Handle type="target" position={Position.Top} />
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 5,
                    padding: 5,
                }}
            >
                <Tag minimal>{_.get(data, "fromParam", null)}</Tag>
                <Tag minimal>{_.get(data, "toParam", null)}</Tag>
            </div>
            <Handle type="source" position={Position.Bottom} />
        </>
    );
}
