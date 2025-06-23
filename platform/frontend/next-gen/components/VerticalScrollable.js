import { Alignment } from "@blueprintjs/core";
import { faCaretDown } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { FAIcon } from "./FAIcon";
import withAutoSizer from "./hocs/withAutoSizer";
function VerticalScrollable({
    width,
    height,
    children,
    backgroundColor,
    show = true,
    transitionDuration = 0,
}) {
    const containerRef = useRef(null);
    const timeoutIdRef = useRef(null);
    const [showBottom, setShowBottom] = useState(false);
    const checkScroll = useCallback(() => {
        if (containerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } =
                containerRef.current;
            setShowBottom(_.ceil(scrollTop + clientHeight) < scrollHeight);
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
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        if (show) {
            timeoutIdRef.current = setTimeout(() => {
                setVisible(true);
            }, transitionDuration);
        } else {
            clearTimeout(timeoutIdRef.current);
            setVisible(false);
        }
    }, [show]);
    return (
        <div style={{ position: "relative", width, height }}>
            <div
                ref={containerRef}
                style={{
                    overflowY: "auto",
                    overflowX: "hidden",
                    scrollBehavior: "smooth",
                }}
                className="scrollbar-none full-parent-height"
            >
                {children}
            </div>
            {showBottom && visible && (
                <div
                    className="full-parent-width"
                    style={{
                        position: "absolute",
                        bottom: 0,
                        left: 0,
                        zIndex: 1,
                        height: 40,
                        width,
                        textAlign: Alignment.CENTER,
                        background: `linear-gradient(to top, ${backgroundColor} 0%, ${backgroundColor} 20px, transparent 99%, transparent 100%)`,
                    }}
                >
                    <FAIcon
                        icon={faCaretDown}
                        style={{
                            position: "absolute",
                            bottom: 0,
                            left: "50%",
                            transform: "translate(-16px, 0)",
                        }}
                    />
                </div>
            )}
        </div>
    );
}
export default withAutoSizer(VerticalScrollable);
