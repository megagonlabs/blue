import { Classes, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
import BaseNode from "./BaseNode";
export default function AgentNode({ id, data }) {
    const consumer = _.get(data, "consumer", false);
    const producer = _.get(data, "producer", false);
    return (
        <BaseNode id={id} data={data}>
            <Tag intent={Intent.PRIMARY} minimal style={{ marginBottom: 10 }}>
                Agent
            </Tag>
            <div style={{ height: 18 }}>
                <Tooltip
                    className="full-parent-width"
                    content={
                        <div style={{ maxWidth: 300, wordBreak: "break-all" }}>
                            {data.label}
                        </div>
                    }
                >
                    <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                        {data.label}
                    </div>
                </Tooltip>
            </div>

            {consumer && (
                <Handle id="consumer" type="target" position={Position.Left} />
            )}
            {producer && (
                <Handle id="producer" type="source" position={Position.Right} />
            )}
        </BaseNode>
    );
}
