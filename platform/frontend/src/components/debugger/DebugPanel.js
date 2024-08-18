import { Classes, Overlay2, OverlaysProvider } from "@blueprintjs/core";
import classNames from "classnames";
import { useCallback, useContext, useEffect, useRef } from "react";
import { RESIZE_DIRECTION } from "../constant";
import { AuthContext } from "../contexts/auth-context";
import { useFloatingWindow } from "../hooks/useFloatingWindow";
import Debugger from "./Debugger";
import Resizer from "./Resizer";
const BASE_HEIGHT = 300;
export default function DebugPanel() {
    const handleDrag = useCallback(({ x, y }) => {
        return {
            x: Math.min(Math.max(100, x), window.innerWidth - 100),
            y: Math.min(Math.max(100, y), window.innerHeight - 100),
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
                window.innerWidth - 200
            )}px`;
        };
        const resizeBottom = () => {
            dialog.style.height = `${Math.min(
                Math.max(BASE_HEIGHT, height + movementY),
                window.innerHeight - 200
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
    const handleWindowResize = () => {
        handleResize(RESIZE_DIRECTION.BottomRight, 0, 0);
        reposition();
    };
    useEffect(() => {
        window.addEventListener("resize", handleWindowResize);
        return () => window.removeEventListener("resize", handleWindowResize);
    }, []);
    const { settings } = useContext(AuthContext);
    return (
        <OverlaysProvider>
            <Overlay2
                className={classNames("height-0")}
                childRef={resizeRef}
                hasBackdrop={false}
                isOpen
                enforceFocus={false}
                autoFocus={false}
            >
                <div
                    className={classNames(Classes.DIALOG, "margin-0")}
                    ref={resizeRef}
                    style={{
                        transform: "translate(100px, 100px)",
                        position: "relative",
                        display: _.get(settings, "debug_mode", false)
                            ? null
                            : "none",
                        height: BASE_HEIGHT,
                        width: BASE_HEIGHT * 1.5,
                        paddingBottom: 0,
                        overflow: "hidden",
                    }}
                >
                    <Resizer onResize={handleResize} />
                    <div
                        className={classNames(
                            Classes.DIALOG_HEADER,
                            Classes.HEADING,
                            "margin-0"
                        )}
                        style={{ cursor: "move" }}
                        ref={dragRef}
                    >
                        Debugger
                    </div>
                    <div
                        style={{ height: "calc(100% - 40px)" }}
                        className={classNames(Classes.DIALOG_BODY, "margin-0")}
                    >
                        <Debugger />
                    </div>
                </div>
            </Overlay2>
        </OverlaysProvider>
    );
}
