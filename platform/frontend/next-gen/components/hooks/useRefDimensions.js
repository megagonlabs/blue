import _ from "lodash";
import { useEffect, useState } from "react";
export const useRefDimensions = (ref) => {
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    useEffect(() => {
        const currentElement = ref.current;
        if (!currentElement) {
            return;
        }
        function measureAndSetDimensions() {
            const boundingRect = currentElement.getBoundingClientRect();
            const { width, height } = boundingRect;
            const shouldUpdate =
                !_.isEqual(dimensions.width, width) ||
                !_.isEqual(dimensions.height, height);
            if (shouldUpdate) {
                setDimensions({ width: width, height: height });
            }
        }
        const resizeObserver = new ResizeObserver(() => {
            measureAndSetDimensions();
        });
        measureAndSetDimensions();
        resizeObserver.observe(currentElement);
        return () => {
            resizeObserver.disconnect();
        };
    }, [ref, dimensions]);
    return dimensions;
};
