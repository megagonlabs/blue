import {
    POPOVER_CONTENT_MAX_WIDTH,
    REACT_FLOW_NODE,
} from "@/components/constants";
import { useReactFlowCustomContext } from "@/components/contexts/ReactFlowCustomContext";
import { FAIcon } from "@/components/FAIcon";
import { Classes, Colors } from "@blueprintjs/core";
import { faMapLocationDot } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useUpdateNodeInternals } from "@xyflow/react";
import classNames from "classnames";
import _ from "lodash";
import { memo, useEffect, useRef, useState } from "react";
const BaseNode = memo(({ id, data, children, card = true }) => {
    const { selectedNodes, clickedNode } = useReactFlowCustomContext();
    const nodeRef = useRef(null);
    const updateNodeInternals = useUpdateNodeInternals();
    const [currentDimensions, setCurrentDimensions] = useState({
        width: null,
        height: null,
    });
    useEffect(() => {
        if (!nodeRef.current) return;
        const resizeObserver = new ResizeObserver((entries) => {
            for (let entry of entries) {
                if (_.isEqual(entry.target, nodeRef.current)) {
                    const { width, height } = entry.contentRect;
                    if (
                        width !== currentDimensions.width ||
                        height !== currentDimensions.height
                    ) {
                        setCurrentDimensions({ width, height });
                        setTimeout(() => {
                            updateNodeInternals(id);
                            if (_.isFunction(data.onDimensionsChange)) {
                                data.onDimensionsChange(id, width, height);
                            }
                        }, 0);
                    }
                }
            }
        });
        resizeObserver.observe(nodeRef.current);
        return () => {
            resizeObserver.disconnect();
        };
    }, [id, data.onDimensionsChange, updateNodeInternals, currentDimensions]);
    return (
        <div
            className={classNames({
                "custom-card": card,
                "interactive-card-border": card,
                [Classes.ELEVATION_4]: selectedNodes.has(id),
            })}
            ref={nodeRef}
            style={{
                width: "auto",
                height: "auto",
                minWidth: 1,
                minHeight: 1,
                maxWidth: POPOVER_CONTENT_MAX_WIDTH,
                display: "inline-block",
                boxSizing: "border-box",
                borderColor: selectedNodes.has(id) ? "transparent" : null,
                borderRadius: 5,
            }}
        >
            {_.isEqual(clickedNode?.id, id) &&
                !_.isEqual(clickedNode?.type, "tag") && (
                    <div style={{ position: "absolute", right: 10, top: 10 }}>
                        <FAIcon
                            icon={faMapLocationDot}
                            size={20}
                            style={{ "--fa-primary-color": Colors.RED3 }}
                        />
                    </div>
                )}
            <div style={{ padding: REACT_FLOW_NODE["padding"] }}>
                {children}
            </div>
        </div>
    );
});
BaseNode.displayName = "BaseNode";
export default BaseNode;
