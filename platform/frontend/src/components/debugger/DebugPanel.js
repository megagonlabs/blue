import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    Classes,
    Intent,
    Overlay2,
    OverlaysProvider,
    Tooltip,
} from "@blueprintjs/core";
import { faMinus } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { RESIZE_DIRECTION } from "../constant";
import { useFloatingWindow } from "../hooks/useFloatingWindow";
import Debugger from "./Debugger";
import Resizer from "./Resizer";
const BASE_HEIGHT = 300;
export default function DebugPanel() {
    const handleDrag = useCallback(({ x, y }) => {
        return {
            x: Math.min(Math.max(40, x), window.innerWidth - 100),
            y: Math.min(Math.max(40, y), window.innerHeight - 100),
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
    const [isMinimized, setIsMinimized] = useState(false);
    return (
        <OverlaysProvider>
            <Overlay2
                className={classNames("height-0")}
                childRefs={{ debugger: resizeRef }}
                hasBackdrop={false}
                isOpen
                enforceFocus={false}
                autoFocus={false}
            >
                <div
                    key="debugger"
                    className={classNames(Classes.DIALOG, "margin-0")}
                    ref={resizeRef}
                    style={{
                        transform: "translate(40px, 40px)",
                        position: "relative",
                        display:
                            _.get(settings, "debug_mode", false) && !isMinimized
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
                        style={{
                            height: "calc(100% - 40px)",
                            overscrollBehavior: "contain",
                        }}
                        className={classNames(Classes.DIALOG_BODY, "margin-0")}
                    >
                        <Debugger />
                    </div>
                    <div style={{ position: "absolute", top: 5, right: 15 }}>
                        <Tooltip
                            content="Minimize"
                            placement="bottom-end"
                            minimal
                        >
                            <Button
                                variant="minimal"
                                intent={Intent.WARNING}
                                icon={faIcon({ icon: faMinus })}
                                onClick={() => setIsMinimized(true)}
                            />
                        </Tooltip>
                    </div>
                </div>
                <div
                    key="debugger-minimized"
                    className={`${Classes.DIALOG} margin-0`}
                    style={{
                        position: "absolute",
                        top: "calc(100vh - 40px)",
                        overflow: "hidden",
                        borderBottomLeftRadius: 0,
                        borderBottomRightRadius: 0,
                        width: 250,
                        right: 40,
                        display:
                            _.get(settings, "debug_mode", false) && isMinimized
                                ? null
                                : "none",
                        cursor: "pointer",
                    }}
                    onClick={() => setIsMinimized(false)}
                >
                    <div
                        className={classNames(
                            Classes.DIALOG_HEADER,
                            Classes.HEADING
                        )}
                    >
                        Debugger
                    </div>
                </div>
            </Overlay2>
        </OverlaysProvider>
    );
}
