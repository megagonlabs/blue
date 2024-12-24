import TrackerCard from "@/components/admin/TrackerCard";
import Series from "@/components/admin/trackers/Series";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import Timestamp from "@/components/Timestamp";
import {
    Blockquote,
    Button,
    ButtonGroup,
    Card,
    Classes,
    Colors,
    H4,
    H5,
    H6,
    Menu,
    MenuItem,
    Popover,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCircleDot,
    faMegaphone,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
export default function Status() {
    const { appState, appActions } = useContext(AppContext);
    const [isLive, setIsLive] = useState(false);
    const { list: trackerList } = appState.tracker;
    const appStateRef = useRef();
    useEffect(() => {
        appStateRef.current = appState;
    }, [appState.tracker]);
    const render = (
        time,
        object,
        path = [],
        graph = {},
        graphKeys = new Set()
    ) => {
        let result = [];
        let { id, type, data, label, visibility } = object;
        if (visibility) {
            if (_.isEqual(type, "tracker")) {
                let keys = Object.keys(data);
                result.push(
                    <H5 className={Classes.TEXT_OVERFLOW_ELLIPSIS}>{id}</H5>
                );
                for (let i = 0; i < _.size(keys); i++) {
                    const response = render(
                        time,
                        data[keys[i]],
                        [...path, id],
                        graph,
                        graphKeys
                    );
                    graph = response["graph"];
                    result = result.concat(response["result"]);
                }
            } else if (_.isEqual(type, "group")) {
                let keys = Object.keys(data);
                result.push(<H6>{label}</H6>);
                let group = [];
                for (let i = 0; i < _.size(keys); i++) {
                    const response = render(
                        time,
                        data[keys[i]],
                        [...path, id],
                        graph,
                        graphKeys
                    );
                    graph = response["graph"];
                    group = group.concat(response["result"]);
                }
                const GROUP_STYLE = {
                    width: "100%",
                    display: "flex",
                    gap: 10,
                    alignItems: "flex-start",
                    flexWrap: "wrap",
                };
                if (!_.isEmpty(group)) {
                    if (_.size(group) > 1)
                        result.push(
                            <Blockquote
                                style={{ ...GROUP_STYLE, paddingRight: 0 }}
                            >
                                {group.map((e) => e)}
                            </Blockquote>
                        );
                    else
                        result.push(
                            <div style={{ ...GROUP_STYLE, marginBottom: 10 }}>
                                {group.map((e) => e)}
                            </div>
                        );
                }
            } else if (["time", "number", "status", "text"].includes(type)) {
                let { value } = object;
                result.push(
                    <Card style={{ padding: 0, overflow: "hidden" }}>
                        <div
                            style={{ padding: "10px 10px 5px" }}
                            className={Classes.TEXT_MUTED}
                        >
                            {label}
                        </div>
                        <div
                            style={{
                                height: "50%",
                                padding: "5px 10px 10px",
                                backgroundColor: Colors.LIGHT_GRAY5,
                            }}
                        >
                            {_.isEqual(type, "time") ? (
                                <Timestamp timestamp={value * 1000} />
                            ) : (
                                value
                            )}
                        </div>
                    </Card>
                );
            } else if (_.isEqual(type, "series")) {
                let { label, value } = object;
                const graphKey = path.join(":");
                let temp = _.get(graph, [graphKey, _.toString(time)], {});
                temp[id] = { label, value };
                _.setWith(graph, [graphKey, time], temp, Object);
                if (!graphKeys.has(graphKey)) {
                    graphKeys.add(graphKey);
                    result.push(
                        <Series tracker={_.first(path)} graphKey={graphKey} />
                    );
                }
            }
        }
        return { result, graph, graphKeys };
    };
    useEffect(() => {
        // opening a connection to the server to begin receiving events from it
        const eventSource = new EventSource(
            `${process.env.NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${process.env.NEXT_PUBLIC_PLATFORM_NAME}/status`,
            { withCredentials: true }
        );
        eventSource.addEventListener("open", () => setIsLive(true));
        eventSource.addEventListener("error", () => setIsLive(false));
        // attaching a handler to receive message events
        eventSource.addEventListener("message", (event) => {
            const { data, channel } = JSON.parse(event.data);
            appActions.tracker.addTracker(channel);
            let time = _.get(data, "data.metadata.data.current.value", 0);
            if (_.isNumber(time)) time *= 1000;
            const trackerGraph = _.cloneDeep(
                _.get(appStateRef.current.tracker.data, [channel, "graph"], {})
            );
            const { result, graph } = render(time, data, [], trackerGraph);
            appActions.tracker.addTrackerData({
                key: channel,
                data: result,
                graph,
            });
        });
        // terminating the connection on component unmount
        return () => {
            eventSource.close();
        };
    }, []);
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
                    <Popover
                        placement="bottom-start"
                        minimal
                        content={
                            <Menu>
                                {trackerList.map((tracker, index) => (
                                    <MenuItem key={index} text={tracker} />
                                ))}
                            </Menu>
                        }
                    >
                        <Tooltip minimal placement="bottom" content="Trackers">
                            <Button
                                icon={faIcon({ icon: faMegaphone })}
                                text={_.size(trackerList)}
                            />
                        </Tooltip>
                    </Popover>
                </ButtonGroup>
            </Card>
            <div
                style={{
                    padding: 20,
                    overflowY: "auto",
                    height: "calc(100% - 50px)",
                }}
            >
                {trackerList.map((tracker, index) => (
                    <div key={index} style={{ marginTop: index > 0 ? 20 : 0 }}>
                        <TrackerCard tracker={tracker} />
                    </div>
                ))}
            </div>
        </>
    );
}
