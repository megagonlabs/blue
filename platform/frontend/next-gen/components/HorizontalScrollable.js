import { Alignment } from "@blueprintjs/core";
import {
    faCaretLeft,
    faCaretRight,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { FAIcon } from "./FAIcon";
import withAutoSizer from "./hocs/withAutoSizer";
function HorizontalScrollable({ width, height, children, backgroundColor }) {
    const containerRef = useRef(null);
    const [showLeft, setShowLeft] = useState(false);
    const [showRight, setShowRight] = useState(false);
    const checkScroll = useCallback(() => {
        if (containerRef.current) {
            const { scrollLeft, scrollWidth, clientWidth } =
                containerRef.current;
            setShowLeft(scrollLeft > 0);
            setShowRight(_.ceil(scrollLeft + clientWidth) < scrollWidth);
        }
    }, []);
    useEffect(() => {
        const container = containerRef.current;
        if (container) {
            container.addEventListener("scroll", checkScroll);
            checkScroll();
            const resizeObserver = new ResizeObserver(checkScroll);
            resizeObserver.observe(container);
            return () => {
                container.removeEventListener("scroll", checkScroll);
                resizeObserver.disconnect();
            };
        }
    }, [checkScroll]);
    const handleScroll = (direction) => {
        if (containerRef.current) {
            const { scrollLeft } = containerRef.current;
            const newScrollLeft = _.isEqual(direction, "left")
                ? Math.max(scrollLeft - scrollStep, 0)
                : scrollLeft + width / 2;
            containerRef.current.scrollTo({
                left: newScrollLeft,
                behavior: "smooth",
            });
        }
    };
    return (
        <div style={{ position: "relative", width, height }}>
            {showLeft && (
                <div
                    className="full-parent-height"
                    style={{
                        width: 40,
                        position: "absolute",
                        left: 0,
                        top: "50%",
                        transform: "translate(0, -10px)",
                        height,
                        zIndex: 1,
                        textAlign: Alignment.START,
                        background: `linear-gradient(to right, ${backgroundColor} 0%, ${backgroundColor} 20px, transparent 99%, transparent 100%)`,
                    }}
                >
                    <FAIcon icon={faCaretLeft} />
                </div>
            )}
            <div
                ref={containerRef}
                style={{
                    overflowX: "auto",
                    scrollBehavior: "smooth",
                }}
                className="scrollbar-none full-parent-width"
            >
                {children}
            </div>
            {showRight && (
                <div
                    className="full-parent-height"
                    style={{
                        width: 40,
                        position: "absolute",
                        right: 0,
                        top: "50%",
                        transform: "translate(0, -10px)",
                        height,
                        zIndex: 1,
                        textAlign: Alignment.END,
                        background: `linear-gradient(to left, ${backgroundColor} 0%, ${backgroundColor} 20px, transparent 99%, transparent 100%)`,
                    }}
                >
                    <FAIcon icon={faCaretRight} />
                </div>
            )}
        </div>
    );
}
export default withAutoSizer(HorizontalScrollable);
