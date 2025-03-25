import _ from "lodash";
import { useState } from "react";

const ExpandingBox = ({
    initialWidth,
    initialHeight,
    expandedWidth,
    expandedHeight,
    children,
}) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [width, setWidth] = useState(initialWidth);
    const [height, setHeight] = useState(initialHeight);
    const handleExpand = () => {
        setIsExpanded(true);
        setWidth(expandedWidth);
        setHeight(expandedHeight);
    };
    const handleReset = () => {
        setIsExpanded(false);
        setWidth(initialWidth);
        setHeight(initialHeight);
    };
    return (
        <div
            style={{
                width,
                height,
                maxWidth: "calc(100vw - 40px)",
                maxHeight: "calc(100vh - 40px)",
                transition: "width 0.15s ease-in-out, height 0.15s ease-in-out",
            }}
            onMouseEnter={handleExpand}
            onMouseLeave={handleReset}
        >
            {_.isFunction(children) ? children(isExpanded) : children}
        </div>
    );
};

export default ExpandingBox;
