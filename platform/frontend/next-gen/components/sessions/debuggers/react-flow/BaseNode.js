import { useReactFlowCustomContext } from "@/components/contexts/ReactFlowCustomContext";
import { FAIcon } from "@/components/FAIcon";
import { Classes, Colors } from "@blueprintjs/core";
import { faMapLocationDot } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useUpdateNodeInternals } from "@xyflow/react";
import classNames from "classnames";
import _ from "lodash";
import { memo, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
const MAP_PIN_ICON = (
    <FAIcon
        icon={faMapLocationDot}
        size={20}
        style={{ "--fa-primary-color": Colors.RED3 }}
    />
);
const BaseNode = memo(({ id, data, children, card = true }) => {
    const { selectedNodes, clickedNode } = useReactFlowCustomContext();
    const nodeRef = useRef(null);
    const updateNodeInternals = useUpdateNodeInternals();
    const [mapPinTarget, setMapPinTarget] = useState(null);
    const dimensionsRef = useRef({ width: null, height: null });
    useEffect(() => {
        if (!nodeRef.current) return;
        const pinElement = nodeRef.current.querySelector(".map-pin");
        setMapPinTarget(pinElement);
        const resizeObserver = new ResizeObserver((entries) => {
            for (let entry of entries) {
                if (_.isEqual(entry.target, nodeRef.current)) {
                    const { width, height } = entry.contentRect;
                    if (
                        width !== dimensionsRef.current.width ||
                        height !== dimensionsRef.current.height
                    ) {
                        dimensionsRef.current = { width, height };
                        setTimeout(() => {
                            requestAnimationFrame(() => {
                                updateNodeInternals(id);
                                if (_.isFunction(data.onDimensionsChange)) {
                                    data.onDimensionsChange(id, width, height);
                                }
                            });
                        }, 0);
                    }
                }
            }
        });
        resizeObserver.observe(nodeRef.current);
        return () => {
            resizeObserver.disconnect();
        };
    }, [id, data.onDimensionsChange, updateNodeInternals]);
    const showLocationIcon =
        _.isEqual(clickedNode?.id, id) && !_.isEqual(clickedNode?.type, "tag");
    return (
        <div
            className={classNames({
                [Classes.CARD]: card,
                "interactive-card-border": card,
                [Classes.ELEVATION_4]: selectedNodes.has(id),
            })}
            ref={nodeRef}
            style={{
                width: "auto",
                height: "auto",
                minWidth: 95.27,
                minHeight: 1,
                padding: 0,
                display: "inline-block",
                boxSizing: "border-box",
                borderRadius: 5,
                overflow: "hidden",
            }}
        >
            {showLocationIcon && mapPinTarget
                ? createPortal(MAP_PIN_ICON, mapPinTarget)
                : showLocationIcon && (
                      <div style={{ position: "absolute", right: 10, top: 10 }}>
                          {MAP_PIN_ICON}
                      </div>
                  )}
            {children}
        </div>
    );
});
BaseNode.displayName = "BaseNode";
export default BaseNode;
