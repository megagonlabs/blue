import {
    EMPTY_OBJECT,
    POPOVER_CONTENT_MAX_WIDTH,
} from "@/components/constants";
import { useReactFlowCustomContext } from "@/components/contexts/ReactFlowCustomContext";
import { useSessionStore } from "@/stores/session-store";
import { Classes, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import classNames from "classnames";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import BaseNode from "./BaseNode";
export default function StreamNode({ id, data }) {
    const { direction } = useReactFlowCustomContext();
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", data.sessionId], EMPTY_OBJECT),
        }))
    );
    const stream = _.get(session, ["streams", data.label], null);
    const streamData = _.get(stream, "data", []);
    return (
        <BaseNode id={id} data={data}>
            <div style={{ padding: 10, maxWidth: POPOVER_CONTENT_MAX_WIDTH }}>
                <Tag
                    intent={Intent.PRIMARY}
                    minimal
                    style={{ marginBottom: 10 }}
                >
                    Stream
                </Tag>
                <div style={{ height: 18 }}>
                    <Tooltip
                        className="full-parent-width"
                        content={
                            <div
                                style={{
                                    maxWidth: POPOVER_CONTENT_MAX_WIDTH,
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
                        <div
                            key={index}
                            className={classNames(
                                "multiline-ellipsis-5",
                                Classes.TEXT_MUTED
                            )}
                        >
                            {JSON.stringify(data.content)}
                        </div>
                    ))}
                </div>
                <Handle
                    type="target"
                    position={
                        _.isEqual(direction, "TB")
                            ? Position.Top
                            : Position.Left
                    }
                />
                {_.get(data, "consumed", false) && (
                    <Handle
                        type="source"
                        position={
                            _.isEqual(direction, "TB")
                                ? Position.Bottom
                                : Position.Right
                        }
                    />
                )}
            </div>
        </BaseNode>
    );
}
