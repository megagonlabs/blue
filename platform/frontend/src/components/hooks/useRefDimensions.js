import _ from "lodash";
import { useEffect, useState } from "react";
export const useRefDimensions = (ref) => {
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    useEffect(() => {
        function handleResize() {
            // set window width/height to state
            if (ref.current) {
                const { current } = ref;
                const boundingRect = current.getBoundingClientRect();
                const { width, height } = boundingRect;
                const shouldUpdate =
                    !_.isEqual(dimensions.width, width) ||
                    !_.isEqual(dimensions.height, height);
                if (shouldUpdate) {
                    setDimensions({ width: width, height: height });
                }
            }
        }
        // add event listener
        window.addEventListener("resize", handleResize);
        // call handler right away so state gets updated with initial window size
        handleResize();
        // remove event listener on cleanup
        return () => window.removeEventListener("resize", handleResize);
    }, [ref, dimensions]);
    return dimensions;
};
