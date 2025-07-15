import { REACT_FLOW_NODE } from "@/components/constants";
import { Classes, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
export default function AgentNode({ data, selected }) {
    return (
        <div
            className="custom-card interactive-card-border"
            style={{
                padding: REACT_FLOW_NODE["padding"],
                fontFamily: "monospace, monospace",
                maxWidth: 400,
            }}
        >
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
            {_.get(data, "producer", false) && (
                <Handle type="source" position={Position.Right} />
            )}
            {_.get(data, "consumer", false) && (
                <Handle type="target" position={Position.Left} />
            )}
        </div>
    );
}
