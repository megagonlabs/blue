import {
    END_OF_EVENT_SIGNAL,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Colors,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowDown,
    faBan,
    faCircleDot,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef, useState } from "react";
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
export default function AgentLogs({
    containerId,
    setContainerId,
    setShow,
    leftBoundary = false,
}) {
    const [isLive, setIsLive] = useState(false);
    const [logs, setLogs] = useState([]);
    const containerRef = useRef(null);
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
                                <Tag
                                    minimal
                                    style={{ fontWeight: 600, borderRadius: 0 }}
                                >
                                    {timestamp.toLocaleString()}
                                </Tag>
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
                }}
            >
                {logs.map(({ line, timestampEpoch }) => (
                    <div key={timestampEpoch}>{line}</div>
                ))}
            </div>
        </div>
    );
}
