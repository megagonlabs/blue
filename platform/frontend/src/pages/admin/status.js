import { AppContext } from "@/components/contexts/app-context";
import { mergeTrackerData } from "@/components/helper";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    Colors,
    Divider,
    H4,
    H5,
    Intent,
    Popover,
    PopoverInteractionKind,
    Tag,
} from "@blueprintjs/core";
import {
    faCircleDot,
    faCircleSmall,
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import { VegaLite } from "react-vega";
export default function Status() {
    const { appState, appActions } = useContext(AppContext);
    const [data, setData] = useState([]);
    const dataRef = useRef();
    const [isLive, setIsLive] = useState(false);
    const [details, setDetails] = useState({});
    useEffect(() => {
        dataRef.current = data;
    }, [data]);
    const cid = _.get(details, "cid", "");
    useEffect(() => {
        if (!_.isEmpty(cid)) {
            setData(
                mergeTrackerData(
                    _.get(appState, ["tracker", "data", cid], []),
                    data
                )
            );
        }
    }, [cid]);
    useEffect(() => {
        // opening a connection to the server to begin receiving events from it
        const eventSource = new EventSource(
            `${process.env.NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${process.env.NEXT_PUBLIC_PLATFORM_NAME}/status/platform`,
            { withCredentials: true }
        );
        eventSource.addEventListener("open", () => setIsLive(true));
        eventSource.addEventListener("error", () => setIsLive(false));
        // attaching a handler to receive message events
        eventSource.addEventListener("message", (event) => {
            const eventData = JSON.parse(event.data);
            setDetails({
                threads: _.orderBy(
                    Object.entries(eventData.threads).map((e) => e[1]),
                    "name"
                ),
                cid: eventData.cid,
                connection_factory_id: eventData.connection_factory_id,
            });
            setData(
                _.takeRight(
                    [
                        ...dataRef.current,
                        {
                            epoch: eventData.epoch * 1000,
                            created_connections:
                                eventData.num_created_connections,
                            in_use_connections:
                                eventData.num_in_use_connections,
                            available_connections:
                                eventData.num_available_connections,
                        },
                    ],
                    60
                )
            );
            setIsLive(true);
        });
        // terminating the connection on component unmount
        return () => {
            if (!_.isEmpty(cid))
                appActions.tracker.addTrackerData({
                    key: cid,
                    data: dataRef.current,
                });
            eventSource.close();
        };
    }, []);
    const CONNECTION_FIELDS = [
        "created_connections",
        "in_use_connections",
        "available_connections",
    ];
    const CONNECTION_VEGA_SPEC = {
        $schema: "https://vega.github.io/schema/vega-lite/v5.json",
        data: { name: "values" },
        width: "container",
        height: 100,
        layer: [
            {
                layer: [
                    {
                        encoding: {
                            y: {
                                axis: {
                                    format: ",.2f",
                                    orient: "left",
                                },
                                field: "value",
                            },
                        },
                        mark: {
                            type: "line",
                            interpolate: "step-after",
                        },
                        params: [
                            {
                                name: "legend_select",
                                bind: "legend",
                                select: {
                                    fields: ["key"],
                                    type: "point",
                                },
                            },
                        ],
                        transform: [
                            {
                                filter: {
                                    field: "key",
                                    oneOf: CONNECTION_FIELDS,
                                },
                            },
                        ],
                    },
                ],
                encoding: {
                    color: {
                        sort: CONNECTION_FIELDS,
                        field: "key",
                        title: null,
                        type: "nominal",
                        scale: {
                            range: [
                                Colors.BLUE3,
                                Colors.ORANGE3,
                                Colors.GREEN3,
                            ],
                        },
                    },
                    opacity: {
                        condition: {
                            param: "legend_select",
                            value: 1,
                        },
                        value: 0.2,
                    },
                },
            },
            {
                encoding: {
                    tooltip: [
                        {
                            format: "%X",
                            field: "epoch",
                            title: "timestamp",
                            type: "temporal",
                        },
                        {
                            field: "created_connections",
                            title: "created",
                            type: "quantitative",
                        },
                        {
                            field: "in_use_connections",
                            title: "in_use",
                            type: "quantitative",
                        },
                        {
                            field: "available_connections",
                            title: "available",
                            type: "quantitative",
                        },
                    ],
                    opacity: {
                        condition: { param: "hover", value: 0.3, empty: false },
                        value: 0,
                    },
                },
                params: [
                    {
                        name: "hover",
                        select: {
                            nearest: true,
                            fields: ["epoch"],
                            on: "mouseover",
                            type: "point",
                        },
                    },
                ],
                mark: { point: false, stroke: Colors.DARK_GRAY3, type: "rule" },
            },
        ],
        transform: [{ fold: CONNECTION_FIELDS }],
        encoding: {
            x: {
                axis: {
                    format: "%X",
                    labelSeparation: 5,
                    labelOverlap: "parity",
                    tickCount: 10,
                },
                type: "temporal",
                title: "",
                field: "epoch",
            },
            y: {
                title: "Connection",
                type: "quantitative",
            },
        },
    };
    const threads = _.get(details, "threads", []);
    const connectionFactoryId = _.get(details, "connection_factory_id", "");
    return (
        <>
            <Card
                interactive
                style={{
                    padding: 5,
                    borderRadius: 0,
                    position: "relative",
                    zIndex: 1,
                    cursor: "default",
                }}
            >
                <ButtonGroup large minimal>
                    <Button
                        disabled
                        style={{ cursor: "default" }}
                        text={<H4 className="margin-0">Status</H4>}
                    />
                </ButtonGroup>
            </Card>
            <div
                style={{
                    padding: 20,
                    overflowY: "auto",
                    height: "calc(100% - 50px)",
                }}
            >
                <Card>
                    <div
                        style={{
                            display: "flex",
                            gap: 10,
                            marginBottom: 10,
                            alignItems: "center",
                        }}
                    >
                        <H5
                            style={{ minWidth: 50 }}
                            className={classNames({
                                "margin-0": true,
                                [Classes.SKELETON]: _.isEmpty(details),
                            })}
                        >
                            {_.isEmpty(cid) ? "-" : cid}
                        </H5>
                        {isLive &&
                            faIcon({
                                icon: faCircleDot,
                                className: "fa-fade",
                                style: {
                                    "--fa-animation-duration": "5s",
                                    color: Colors.GREEN3,
                                },
                            })}
                    </div>
                    <div
                        className={_.isEmpty(details) && Classes.SKELETON}
                        style={{ display: "flex", gap: 5, marginBottom: 10 }}
                    >
                        <Popover
                            interactionKind={PopoverInteractionKind.CLICK}
                            placement="bottom-start"
                            content={
                                <div
                                    style={{
                                        padding: 15,
                                        maxWidth: 360,
                                        maxHeight: 360,
                                        overflowY: "auto",
                                    }}
                                >
                                    {threads.map((thread, index) => (
                                        <div
                                            key={index}
                                            style={{
                                                marginBottom:
                                                    _.size(threads) > index + 1
                                                        ? 10
                                                        : 0,
                                            }}
                                        >
                                            {index > 0 && <Divider />}
                                            <div
                                                style={{
                                                    marginBottom: 5,
                                                    display: "flex",
                                                    gap: 5,
                                                }}
                                            >
                                                {faIcon({
                                                    icon: faCircleSmall,
                                                    style: {
                                                        color: thread.alive
                                                            ? Colors.GREEN3
                                                            : Colors.RED3,
                                                        marginTop: 1,
                                                    },
                                                })}
                                                {_.get(thread, "name", "-")}
                                            </div>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    gap: 10,
                                                    alignItems: "center",
                                                }}
                                            >
                                                <Tag minimal>
                                                    ID:&nbsp;{thread.id}
                                                </Tag>
                                                {thread.daemon && (
                                                    <Tag
                                                        minimal
                                                        intent={Intent.SUCCESS}
                                                    >
                                                        daemon
                                                    </Tag>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            }
                        >
                            <Tag interactive minimal large>
                                Thread:&nbsp;
                                {_.size(threads)}
                            </Tag>
                        </Popover>
                        <Divider />
                        <Tag
                            rightIcon={faIcon({ icon: faCopy })}
                            onClick={() => {
                                copy(connectionFactoryId);
                                AppToaster.show({
                                    icon: faIcon({
                                        icon: faClipboard,
                                    }),
                                    message: `Copied "${connectionFactoryId}"`,
                                });
                            }}
                            interactive
                            minimal
                            large
                        >
                            Connection factory:&nbsp;
                            {_.isEmpty(connectionFactoryId)
                                ? "-"
                                : connectionFactoryId}
                        </Tag>
                    </div>
                    <VegaLite
                        className={_.isEmpty(data) && Classes.SKELETON}
                        data={{ values: data }}
                        style={{ width: "100%" }}
                        spec={CONNECTION_VEGA_SPEC}
                        actions={false}
                    />
                </Card>
            </div>
        </>
    );
}
