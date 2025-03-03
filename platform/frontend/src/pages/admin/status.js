import TrackerCard from "@/components/admin/TrackerCard";
import List from "@/components/admin/trackers/List";
import Series from "@/components/admin/trackers/Series";
import { END_OF_SSE_SIGNAL } from "@/components/constant";
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
    Divider,
    H4,
    H5,
    H6,
    InputGroup,
    Menu,
    MenuDivider,
    MenuItem,
    NonIdealState,
    Popover,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCircleDot,
    faForward,
    faSearch,
    faTimes,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useMemo, useRef, useState } from "react";
export default function Status() {
    const { appState, appActions } = useContext(AppContext);
    const [isLive, setIsLive] = useState(false);
    const { list: trackerList } = appState.tracker;
    const appStateTrackerRef = useRef();
    useEffect(() => {
        appStateTrackerRef.current = appState.tracker;
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
            } else if (_.isEqual(type, "list")) {
                result.push(<List label={label} object={object} />);
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
            const { data, channel, line } = JSON.parse(event.data);
            if (_.isEqual(line, END_OF_SSE_SIGNAL)) {
                setIsLive(false);
                eventSource.close();
            } else {
                appActions.tracker.addTracker(channel);
                let time = _.get(data, "data.metadata.data.current.value", 0);
                if (_.isNumber(time)) time *= 1000;
                const trackerGraph = _.cloneDeep(
                    _.get(
                        appStateTrackerRef.current.data,
                        [channel, "graph"],
                        {}
                    )
                );
                let { result, graph } = render(time, data, [], trackerGraph);
                const trackers = Object.keys(graph);
                for (let i = 0; i < _.size(trackers); i++) {
                    const content = Object.entries(
                        _.get(graph, trackers[i], {})
                    );
                    if (_.size(content) > 60) {
                        const sorted = _.sortBy(content, (e) =>
                            _.toNumber(e[0])
                        );
                        _.set(
                            graph,
                            trackers[i],
                            Object.fromEntries(_.takeRight(sorted, 60))
                        );
                    }
                }
                appActions.tracker.addTrackerData({
                    key: channel,
                    data: result,
                    graph,
                });
            }
        });
        // terminating the connection on component unmount
        return () => {
            eventSource.close();
        };
    }, []);
    const [keyword, setKeyword] = useState("");
    const filteredTrackerList = useMemo(
        () =>
            trackerList.filter((e) =>
                _.toLower(e).includes(_.toLower(keyword))
            ),
        [keyword, trackerList]
    );
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
                <ButtonGroup size="large" variant="minimal">
                    <Button
                        disabled
                        style={{ cursor: "default" }}
                        text={<H4 className="margin-0">Status</H4>}
                    />
                    {isLive && (
                        <>
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
                            <Divider />
                        </>
                    )}
                    <Popover
                        placement="bottom-start"
                        onClose={() => setKeyword("")}
                        minimal
                        content={
                            <Menu
                                size="large"
                                style={{
                                    maxWidth: 400,
                                    maxHeight: 400,
                                    overflowY: "auto",
                                }}
                            >
                                <InputGroup
                                    size="large"
                                    autoFocus
                                    value={keyword}
                                    onChange={(event) =>
                                        setKeyword(event.target.value)
                                    }
                                    style={{ marginBottom: 5 }}
                                    rightElement={
                                        !_.isEmpty(keyword) && (
                                            <Button
                                                onClick={() => setKeyword("")}
                                                variant="minimal"
                                                icon={faIcon({ icon: faTimes })}
                                            />
                                        )
                                    }
                                    leftIcon={faIcon({ icon: faSearch })}
                                />
                                {!_.isEmpty(filteredTrackerList) && (
                                    <MenuDivider title="To section" />
                                )}
                                {!_.isEmpty(filteredTrackerList) ? (
                                    filteredTrackerList.map(
                                        (tracker, index) => (
                                            <MenuItem
                                                text={tracker}
                                                key={index}
                                                onClick={() => {
                                                    const element = _.first(
                                                        document.getElementsByClassName(
                                                            `tracker-card-${tracker}`
                                                        )
                                                    );
                                                    if (element) {
                                                        element.scrollIntoView({
                                                            behavior: "smooth",
                                                        });
                                                    }
                                                }}
                                            />
                                        )
                                    )
                                ) : (
                                    <MenuItem disabled text="No results." />
                                )}
                            </Menu>
                        }
                    >
                        <Tooltip content="Jump" minimal placement="bottom">
                            <Button
                                disabled={_.isEmpty(trackerList)}
                                icon={faIcon({ icon: faForward })}
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
                {_.isEmpty(trackerList) ? (
                    <NonIdealState
                        title="No Status"
                        icon={faIcon({ icon: faWavePulse, size: 50 })}
                    />
                ) : (
                    trackerList.map((tracker, index) => (
                        <div
                            className={`tracker-card-${tracker}`}
                            key={index}
                            style={{
                                marginTop: index > 0 ? 21 : 0,
                                scrollMargin: 20,
                            }}
                        >
                            <TrackerCard tracker={tracker} />
                        </div>
                    ))
                )}
            </div>
        </>
    );
}
