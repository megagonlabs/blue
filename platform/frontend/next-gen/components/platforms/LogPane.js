import { useAppStore } from "@/stores/app-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Colors,
    Intent,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowRight,
    faBan,
    faCircleDot,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { motion } from "framer-motion";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef, useState } from "react";
import { FAIcon } from "../FAIcon";
import {
    END_OF_EVENT_SIGNAL,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { AppToaster } from "../toaster";
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
export default function LogPane({
    show,
    setShow,
    containerId,
    setContainerId,
}) {
    const [isLive, setIsLive] = useState(false);
    const [logs, setLogs] = useState([]);
    useEffect(() => {
        if (_.isEmpty(containerId)) return;
        const eventSource = new EventSource(
            `${NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}/containers/agents/container/${containerId}`,
            { withCredentials: true }
        );
        eventSource.addEventListener("open", () => setIsLive(true));
        eventSource.addEventListener("error", (error) => {
            setIsLive(false);
            const errorData = error.data;
            if (!_.isEmpty(errorData)) {
                AppToaster.show({ message: errorData, intent: Intent.DANGER });
            } else {
                console.log(error);
            }
            if (_.startsWith(errorData, "No such instance:")) {
                eventSource.close();
                setContainerId(null);
            }
        });
        eventSource.addEventListener("message", (event) => {
            const { line } = JSON.parse(event.data);
            if (_.isEqual(line, END_OF_EVENT_SIGNAL)) {
                setIsLive(false);
                eventSource.close();
            } else {
                setLogs((current) => {
                    const timestamp = new Date(line.slice(0, 30));
                    const timestampEpoch = timestamp.getTime();
                    const newLineEntry = {
                        timestampEpoch,
                        line: (
                            <div>
                                <span
                                    style={{
                                        fontWeight: 600,
                                        backgroundColor: Colors.LIGHT_GRAY4,
                                    }}
                                >
                                    {timestamp.toLocaleString()}
                                </span>
                                {line.substring(30)}
                            </div>
                        ),
                    };
                    return _.uniqBy(
                        _.sortBy([...current, newLineEntry], "timestampEpoch"),
                        "timestampEpoch"
                    );
                });
            }
        });
        return () => {
            eventSource.close();
        };
    }, [containerId]);
    const darkMode = useAppStore((state) => state.dark_mode);
    const variants = {
        open: {
            x: 0,
            display: "block",
            transition: { duration: 0.15 },
        },
        closed: {
            x: 200,
            transition: { duration: 0.15 },
            display: "none",
        },
        initial: { x: 200, opacity: 1, display: "none" },
    };
    const elementRef = useRef(null);
    return (
        <motion.div
            variants={variants}
            initial="initial"
            animate={show ? "open" : "closed"}
            className="full-parent-height border-left border-raidus-20"
            style={{
                position: "fixed",
                maxHeight: "calc(100% - 45px)",
                top: 45,
                right: 0,
                zIndex: 10,
                width: "calc(100% + 1px)",
                maxWidth: "min(calc(100% + 1px), 600px)",
                backgroundColor: darkMode ? Colors.DARK_GRAY2 : Colors.WHITE,
                overflowY: "auto",
            }}
        >
            <div
                ref={elementRef}
                className="border-bottom"
                style={{
                    padding: 10,
                    display: "flex",
                    justifyContent: "space-between",
                }}
            >
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    {isLive && (
                        <Button
                            className="pointer-events-none"
                            icon={
                                <FAIcon
                                    icon={faCircleDot}
                                    className="fa-fade"
                                    style={{
                                        "--fa-animation-duration": "2s",
                                        color: Colors.GREEN3,
                                    }}
                                />
                            }
                        />
                    )}
                    <Tooltip
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={elementRef.current}
                        content="Clear logs"
                        placement="bottom"
                    >
                        <Button
                            icon={<FAIcon icon={faBan} />}
                            size={Size.LARGE}
                            onClick={() => {
                                setLogs([]);
                            }}
                            variant={ButtonVariant.MINIMAL}
                        />
                    </Tooltip>
                </ButtonGroup>
                <Button
                    icon={<FAIcon icon={faArrowRight} />}
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                    onClick={() => {
                        setShow(false);
                    }}
                />
            </div>
            <div
                style={{
                    maxHeight: "calc(100% - 61px)",
                    overflowY: "auto",
                    padding: 20,
                }}
            >
                {logs.map(({ line, timestampEpoch }) => (
                    <div key={timestampEpoch}>{line}</div>
                ))}
            </div>
        </motion.div>
    );
}
