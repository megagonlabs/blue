import {
    CIRCLE_DOT_WITH_FADE,
    END_OF_EVENT_SIGNAL,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Intent,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowDown,
    faBan,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef, useState } from "react";
import ContainerLogViewer from "./ContainerLogViewer";
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
export default function AgentLogs({
    containerId,
    setContainerId,
    setShow,
    sessionId = null,
    leftBoundary = false,
}) {
    const [isLive, setIsLive] = useState(false);
    const [logs, setLogs] = useState([]);
    const containerRef = useRef(null);
    useEffect(() => {
        if (_.isEmpty(containerId)) return;
        setLogs([]);
        const encodedJson = encodeURIComponent(
            JSON.stringify({ session: sessionId })
        );
        const eventSource = new EventSource(
            `${NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}/containers/agents/container/${containerId}?filter=${encodedJson}`,
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
                    const entry = {
                        epoch: timestamp.getTime(),
                        localeString: timestamp.toLocaleString(),
                        logMessage: _.trim(line.substring(30)),
                    };
                    return _.uniqBy(
                        _.sortBy([...current, entry], "epoch"),
                        "epoch"
                    );
                });
            }
        });
        return () => {
            eventSource.close();
        };
    }, [containerId, sessionId]);
    const elementRef = useRef(null);
    return (
        <div className="full-parent-dimension">
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
                            icon={CIRCLE_DOT_WITH_FADE}
                        />
                    )}
                    <Tooltip
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={leftBoundary ? elementRef.current : null}
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
                    <Tooltip
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={leftBoundary ? elementRef.current : null}
                        content="Scroll to bottom"
                        placement="bottom"
                    >
                        <Button
                            icon={<FAIcon icon={faArrowDown} />}
                            size={Size.LARGE}
                            onClick={() => {
                                if (containerRef.current) {
                                    containerRef.current.scrollTop =
                                        containerRef.current.scrollHeight;
                                }
                            }}
                            variant={ButtonVariant.MINIMAL}
                        />
                    </Tooltip>
                </ButtonGroup>
                {_.isFunction(setShow) && (
                    <Button
                        icon={<FAIcon icon={faXmarkLarge} />}
                        size={Size.LARGE}
                        variant={ButtonVariant.MINIMAL}
                        onClick={() => {
                            setShow(false);
                        }}
                    />
                )}
            </div>
            <div
                ref={containerRef}
                style={{
                    maxHeight: "calc(100% - 61px)",
                    overflowY: "auto",
                    padding: 20,
                    display: "flex",
                    flexDirection: "column",
                    gap: 10,
                }}
            >
                {logs.map((log, index) => (
                    <ContainerLogViewer key={index} log={log} />
                ))}
            </div>
        </div>
    );
}
