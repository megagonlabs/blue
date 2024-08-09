import { Classes, Overlay2, OverlaysProvider } from "@blueprintjs/core";
import classNames from "classnames";
import { useCallback, useEffect, useRef, useState } from "react";
import { RESIZE_DIRECTION } from "../constant";
import { useFloatingWindow } from "../hooks/useFloatingWindow";
import Resizer from "./Resizer";
const BASE_HEIGHT = 300;
export default function DebugPanel() {
    const handleDrag = useCallback(({ x, y }) => {
        return {
            x: Math.min(Math.max(0, x), window.innerWidth - 200),
            y: Math.min(Math.max(0, y), window.innerHeight - 200),
        };
    }, []);
    const [dragRef, reposition] = useFloatingWindow({ onDrag: handleDrag });
    const resizeRef = useRef(null);
    const handleResize = (direction, movementX, movementY) => {
        const dialog = resizeRef.current;
        if (!dialog) return;
        const { width, height } = dialog.getBoundingClientRect();
        const resizeRight = () => {
            dialog.style.width = `${Math.min(
                Math.max(BASE_HEIGHT * 1.5, width + movementX),
                window.innerWidth - 50
            )}px`;
        };
        const resizeBottom = () => {
            dialog.style.height = `${Math.min(
                Math.max(BASE_HEIGHT, height + movementY),
                window.innerHeight - 50
            )}px`;
        };
        switch (direction) {
            case RESIZE_DIRECTION.BottomRight:
                resizeBottom();
                resizeRight();
                break;
            default:
                break;
        }
    };
    const [isOpen, setIsOpen] = useState(true);
    const handleWindowResize = () => {
        handleResize(RESIZE_DIRECTION.BottomRight, 0, 0);
        reposition();
    };
    useEffect(() => {
        window.addEventListener("resize", handleWindowResize);
        return () => window.removeEventListener("resize", handleWindowResize);
    }, []);
    return (
        <OverlaysProvider>
            <Overlay2
                className="height-0"
                childRef={resizeRef}
                hasBackdrop={false}
                isOpen={isOpen}
                enforceFocus={false}
                autoFocus={false}
            >
                <div
                    className={classNames(Classes.DIALOG, "margin-0")}
                    ref={resizeRef}
                    style={{
                        transform: "translate(50px, 50px)",
                        position: "relative",
                        height: BASE_HEIGHT,
                        width: BASE_HEIGHT * 1.5,
                        paddingBottom: 0,
                        overflow: "hidden",
                    }}
                >
                    <Resizer onResize={handleResize} />
                    <div className={Classes.DIALOG_HEADER} ref={dragRef}></div>
                </div>
            </Overlay2>
        </OverlaysProvider>
    );
}
