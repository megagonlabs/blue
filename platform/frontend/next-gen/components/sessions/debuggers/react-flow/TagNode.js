import { Tag } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
import BaseNode from "./BaseNode";
export default function TagNode({ id, data }) {
    return (
        <BaseNode card={false} id={id} data={data}>
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-evenly",
                }}
            >
                <Handle type="target" position={Position.Left} />
                <Tag minimal>{_.get(data, "label", null)}</Tag>
                <Handle type="source" position={Position.Right} />
            </div>
        </BaseNode>
    );
}
