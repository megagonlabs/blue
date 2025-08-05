import {
    POPOVER_CONTENT_MAX_WIDTH,
    REACT_FLOW_NODE,
} from "@/components/constants";
import { useUpdateNodeInternals } from "@xyflow/react";
import _ from "lodash";
import { memo, useEffect, useRef, useState } from "react";
const BaseNode = memo(({ id, data, children, card = true }) => {
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
                            if (data.onDimensionsChange) {
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
            className={card && "custom-card interactive-card-border"}
            ref={nodeRef}
            style={{
                width: "auto",
                height: "auto",
                minWidth: 1,
                minHeight: 1,
                maxWidth: POPOVER_CONTENT_MAX_WIDTH,
                display: "inline-block",
                boxSizing: "border-box",
            }}
        >
            <div style={{ padding: REACT_FLOW_NODE["padding"] }}>
                {children}
            </div>
        </div>
    );
});
BaseNode.displayName = "BaseNode";
export default BaseNode;
