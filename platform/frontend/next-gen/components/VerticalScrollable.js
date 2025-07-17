import { Alignment } from "@blueprintjs/core";
import {
    faCaretDown,
    faCaretUp,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { FAIcon } from "./FAIcon";
import withAutoSizer from "./hocs/withAutoSizer";
function VerticalScrollable({
    width,
    height,
    children,
    backgroundColor,
    showTopIndicator = true,
    showBottomIndicator = true,
    transitionDuration = 0,
    caretPaddingBottom = 0,
    caretPaddingTop = 0,
}) {
    const containerRef = useRef(null);
    const timeoutIdRef = useRef(null);
    const [showTop, setShowTop] = useState(false);
    const [showBottom, setShowBottom] = useState(false);
    const checkScroll = useCallback(() => {
        if (containerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } =
                containerRef.current;
            setShowBottom(_.ceil(scrollTop + clientHeight) < scrollHeight);
            setShowTop(scrollTop > 0);
        }
    }, [children]);
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
    const [visibleBottom, setVisibleBottom] = useState(false);
    const [visibleTop, setVisibleTop] = useState(false);
    useEffect(() => {
        if (showBottomIndicator) {
            timeoutIdRef.current = setTimeout(() => {
                setVisibleBottom(true);
            }, transitionDuration);
        } else {
            clearTimeout(timeoutIdRef.current);
            setVisibleBottom(false);
        }
    }, [showBottomIndicator]);
    useEffect(() => {
        if (showTopIndicator) {
            timeoutIdRef.current = setTimeout(() => {
                setVisibleTop(true);
            }, transitionDuration);
        } else {
            clearTimeout(timeoutIdRef.current);
            setVisibleTop(false);
        }
    }, [showTopIndicator]);
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
            {showTop && visibleTop && (
                <div
                    className="full-parent-width"
                    style={{
                        position: "absolute",
                        top: 0,
                        paddingTop: caretPaddingTop,
                        left: 0,
                        zIndex: 6,
                        height: 40 + caretPaddingTop,
                        width,
                        textAlign: Alignment.CENTER,
                        background: `linear-gradient(to bottom, ${backgroundColor} 0%, ${backgroundColor} 20px, transparent 99%, transparent 100%)`,
                        display: "flex",
                        justifyContent: "flex-start",
                        flexDirection: "column",
                        alignItems: "center",
                    }}
                >
                    <FAIcon icon={faCaretUp} />
                </div>
            )}
            {showBottom && visibleBottom && (
                <div
                    className="full-parent-width"
                    style={{
                        position: "absolute",
                        bottom: 0,
                        paddingBottom: caretPaddingBottom,
                        left: 0,
                        zIndex: 6,
                        height: 40 + caretPaddingBottom,
                        width,
                        textAlign: Alignment.CENTER,
                        background: `linear-gradient(to top, ${backgroundColor} 0%, ${backgroundColor} 20px, transparent 99%, transparent 100%)`,
                        display: "flex",
                        justifyContent: "flex-end",
                        flexDirection: "column",
                        alignItems: "center",
                    }}
                >
                    <FAIcon icon={faCaretDown} />
                </div>
            )}
        </div>
    );
}
export default withAutoSizer(VerticalScrollable);
