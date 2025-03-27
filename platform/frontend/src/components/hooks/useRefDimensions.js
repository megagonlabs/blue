import _ from "lodash";
import { useEffect, useState } from "react";
export const useRefDimensions = (ref) => {
    const [dimensions, setDimensions] = useState({});
    useEffect(() => {
        function handleResize() {
            // Set window width/height to state
            if (ref.current) {
                const { current } = ref;
                const boundingRect = current.getBoundingClientRect();
                const { width, height } = boundingRect;
                if (
                    !_.isEqual(dimensions.width, width) ||
                    !_.isEqual(dimensions.height, height)
                )
                    setDimensions({
                        width: width,
                        height: height,
                    });
            }
        }
        // Add event listener
        window.addEventListener("resize", handleResize);
        // Call handler right away so state gets updated with initial window size
        handleResize();
        // Remove event listener on cleanup
        return () => window.removeEventListener("resize", handleResize);
    }, [ref]); // eslint-disable-line react-hooks/exhaustive-deps
    return dimensions;
};
