import { END_OF_SSE_SIGNAL } from "@/components/constant";
import { faIcon } from "@/components/icon";
import { Button, ButtonGroup, Card, Colors, Tooltip } from "@blueprintjs/core";
import { faBan, faCircleDot } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
export default function DockerContainerLogs({ containerId }) {
    const [isLive, setIsLive] = useState(false);
    const [lines, setLines] = useState([]);
    const linesRef = useRef(lines);
    useEffect(() => {
        linesRef.current = lines;
    }, [lines]);
    useEffect(() => {
        if (_.isEmpty(containerId)) return;
        const eventSource = new EventSource(
            `${process.env.NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${process.env.NEXT_PUBLIC_PLATFORM_NAME}/containers/agents/container/${containerId}`,
            { withCredentials: true }
        );
        eventSource.addEventListener("open", () => setIsLive(true));
        eventSource.addEventListener("error", (error) => {
            setIsLive(false);
            console.log(error.data);
        });
        eventSource.addEventListener("message", (event) => {
            const { epoch, line } = JSON.parse(event.data);
            if (_.isEqual(line, END_OF_SSE_SIGNAL)) {
                setIsLive(false);
                eventSource.close();
            } else {
                setLines(
                    _.sortBy(
                        [
                            ...linesRef.current,
                            {
                                epoch,
                                line: (
                                    <div>
                                        <span
                                            style={{
                                                fontWeight: 600,
                                                backgroundColor:
                                                    Colors.LIGHT_GRAY4,
                                            }}
                                        >
                                            {new Date(
                                                line.slice(0, 30)
                                            ).toLocaleString()}
                                        </span>
                                        {line.substring(30)}
                                    </div>
                                ),
                            },
                        ],
                        "epoch"
                    )
                );
            }
        });
        return () => {
            eventSource.close();
        };
    }, [containerId]);
    return (
        <>
            <Card style={{ padding: 0 }} className="full-parent-height">
                <div className="border-bottom" style={{ padding: 5 }}>
                    <ButtonGroup variant="minimal" size="large">
                        {isLive && (
                            <Button
                                style={{ pointerEvents: "none" }}
                                icon={faIcon({
                                    icon: faCircleDot,
                                    className: "fa-fade",
                                    style: {
                                        "--fa-animation-duration": "2s",
                                        color: Colors.GREEN3,
                                    },
                                })}
                            />
                        )}
                        <Tooltip
                            content="Clear logs"
                            minimal
                            placement="bottom-start"
                        >
                            <Button
                                onClick={() => setLines([])}
                                icon={faIcon({ icon: faBan })}
                            />
                        </Tooltip>
                    </ButtonGroup>
                </div>
                <div
                    style={{
                        maxHeight: "calc(100% - 51px)",
                        overflowY: "auto",
                        padding: 5,
                    }}
                >
                    {lines.map(({ line }, index) => (
                        <div key={index}>{line}</div>
                    ))}
                </div>
            </Card>
        </>
    );
}
