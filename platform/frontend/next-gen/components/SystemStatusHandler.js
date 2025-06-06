import { useSystemStatusStore } from "@/stores/system-status-store";
import { Blockquote, Classes, H5, H6 } from "@blueprintjs/core";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import { EMPTY_OBJECT, END_OF_EVENT_SIGNAL } from "./constants";
import List from "./platforms/trackers/List";
import Series from "./platforms/trackers/Series";
import Tile from "./platforms/trackers/Tile";
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
const trackerRenderer = (
    time,
    object,
    path = [],
    graphs = {},
    graphKeys = new Set()
) => {
    let result = [],
        newGraphs = _.cloneDeep(graphs);
    let { id, type, data, label, visibility } = object;
    if (visibility) {
        if (_.isEqual(type, "tracker")) {
            let keys = Object.keys(data);
            result.push(
                <H5 className={Classes.TEXT_OVERFLOW_ELLIPSIS}>{id}</H5>
            );
            for (let i = 0; i < _.size(keys); i++) {
                const response = trackerRenderer(
                    time,
                    data[keys[i]],
                    [...path, id],
                    newGraphs,
                    graphKeys
                );
                newGraphs = response["graphs"];
                result = result.concat(response["result"]);
            }
        } else if (_.isEqual(type, "group")) {
            let keys = Object.keys(data);
            result.push(<H6>{label}</H6>);
            let group = [];
            for (let i = 0; i < _.size(keys); i++) {
                const response = trackerRenderer(
                    time,
                    data[keys[i]],
                    [...path, id],
                    newGraphs,
                    graphKeys
                );
                newGraphs = response["graphs"];
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
                if (_.size(group) > 1) {
                    result.push(
                        <Blockquote style={{ ...GROUP_STYLE, paddingRight: 0 }}>
                            {group.map((e) => e)}
                        </Blockquote>
                    );
                } else {
                    result.push(
                        <div style={{ ...GROUP_STYLE, marginBottom: 10 }}>
                            {group.map((e) => e)}
                        </div>
                    );
                }
            }
        } else if (["time", "number", "status", "text"].includes(type)) {
            result.push(<Tile type={type} label={label} object={object} />);
        } else if (_.isEqual(type, "list")) {
            result.push(<List label={label} object={object} />);
        } else if (_.isEqual(type, "series")) {
            let { label, value } = object;
            const graphKey = path.join(":");
            let temp = _.get(newGraphs, [graphKey, _.toString(time)], {});
            temp[id] = { label, value };
            _.setWith(newGraphs, [graphKey, time], temp, Object);
            if (!graphKeys.has(graphKey)) {
                graphKeys.add(graphKey);
                result.push(
                    <Series tracker={_.first(path)} graphKey={graphKey} />
                );
            }
        }
    }
    return { result, graphs: newGraphs, graphKeys };
};
export default function SystemStatusHandler({ children }) {
    const { setState, trackerData, addTracker, setTrackerData } =
        useSystemStatusStore(
            useShallow((state) => ({
                setState: state.setState,
                addTracker: state.addTracker,
                trackerData: state.trackerData,
                setTrackerData: state.setTrackerData,
            }))
        );
    const trackerDataRef = useRef();
    useEffect(() => {
        trackerDataRef.current = trackerData;
    }, [trackerData]);
    useEffect(() => {
        // opening a connection to the server to begin receiving events from it
        const eventSource = new EventSource(
            `${NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}/status`,
            { withCredentials: true }
        );
        eventSource.addEventListener("open", () => {
            setState({ key: "live", value: true });
        });
        eventSource.addEventListener("error", () => {
            setState({ key: "live", value: false });
        });
        eventSource.addEventListener("message", (event) => {
            const { data, channel, line } = JSON.parse(event.data);
            if (_.isEqual(line, END_OF_EVENT_SIGNAL)) {
                eventSource.close();
                setState({ key: "live", value: false });
            } else {
                addTracker(channel);
                let time = _.get(data, "data.metadata.data.current.value", 0);
                if (_.isNumber(time)) time *= 1000;
                const trackerGraph = _.get(
                    trackerDataRef.current,
                    [channel, "graphs"],
                    EMPTY_OBJECT
                );
                let { result, graphs } = trackerRenderer(
                    time,
                    data,
                    [],
                    trackerGraph
                );
                const trackers = Object.keys(graphs);
                for (let i = 0; i < _.size(trackers); i++) {
                    const content = Object.entries(
                        _.get(graphs, trackers[i], {})
                    );
                    if (_.size(content) > 60) {
                        const sorted = _.sortBy(content, (e) => {
                            return _.toNumber(e[0]);
                        });
                        _.set(
                            graphs,
                            trackers[i],
                            Object.fromEntries(_.takeRight(sorted, 60))
                        );
                    }
                }
                setTrackerData({ key: channel, data: result, graphs });
            }
        });
        return () => {
            eventSource.close();
            setState({ key: "live", value: false });
        };
    }, []);
    return children;
}
