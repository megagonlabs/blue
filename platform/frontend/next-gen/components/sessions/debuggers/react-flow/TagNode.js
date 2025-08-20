import { useReactFlowCustomContext } from "@/components/contexts/ReactFlowCustomContext";
import { Size, Tag } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
import BaseNode from "./BaseNode";
export default function TagNode({ id, data }) {
    const { direction } = useReactFlowCustomContext();
    return (
        <BaseNode card={false} id={id} data={data}>
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-evenly",
                }}
            >
                <Handle
                    type="target"
                    position={
                        _.isEqual(direction, "TB")
                            ? Position.Top
                            : Position.Left
                    }
                />
                <Tag size={Size.LARGE} minimal>
                    {_.get(data, "label", null)}
                </Tag>
                <Handle
                    type="source"
                    position={
                        _.isEqual(direction, "TB")
                            ? Position.Bottom
                            : Position.Right
                    }
                />
            </div>
        </BaseNode>
    );
}
