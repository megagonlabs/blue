import { REACT_FLOW_NODE } from "@/components/constants";
import { Classes, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
export default function StreamNode({ data }) {
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
                Stream
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
            <Handle type="target" position={Position.Left} />
            <Handle type="source" position={Position.Right} />
        </div>
    );
}
