import { Tag } from "@blueprintjs/core";
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from "@xyflow/react";
import _ from "lodash";
export default function AgentParamEdge({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    data,
}) {
    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });
    return (
        <>
            <BaseEdge id={id} path={edgePath} />
            <EdgeLabelRenderer>
                <div
                    style={{
                        position: "absolute",
                        transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            flexDirection: `column${
                                sourceY > targetY ? "-reverse" : ""
                            }`,
                            alignItems: "center",
                            gap: 5,
                        }}
                    >
                        <Tag minimal>{_.get(data, "fromParam", null)}</Tag>
                        <Tag minimal>{_.get(data, "toParam", null)}</Tag>
                    </div>
                </div>
            </EdgeLabelRenderer>
        </>
    );
}
