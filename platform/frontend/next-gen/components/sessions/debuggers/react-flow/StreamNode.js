import { useSessionStore } from "@/stores/session-store";
import { Classes, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import BaseNode from "./BaseNode";
export default function StreamNode({ id, data }) {
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", data.sessionId], {}),
        }))
    );
    const stream = _.get(session, ["streams", data.label], null);
    const streamData = _.get(stream, "data", []);
    return (
        <BaseNode id={id} data={data}>
            <Tag intent={Intent.PRIMARY} minimal style={{ marginBottom: 10 }}>
                Stream
            </Tag>
            <div style={{ height: 18 }}>
                <Tooltip
                    className="full-parent-width"
                    content={
                        <div
                            style={{
                                maxWidth: 300,
                                wordBreak: "break-all",
                            }}
                        >
                            {data.label}
                        </div>
                    }
                >
                    <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                        {data.label}
                    </div>
                </Tooltip>
            </div>
            <div style={{ marginTop: 10 }}>
                {streamData.map((data, index) => (
                    <div key={index} className="multiline-ellipsis-5">
                        {JSON.stringify(data.content)}
                    </div>
                ))}
            </div>
            <Handle type="target" position={Position.Left} />
            <Handle type="source" position={Position.Right} />
        </BaseNode>
    );
}
