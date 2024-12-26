import { Card } from "@blueprintjs/core";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
export default function TrackerCard({ tracker }) {
    const { appState } = useContext(AppContext);
    const trackerData = _.get(appState.tracker.data, [tracker, "data"], []);
    return (
        <Card>
            {trackerData.map((data, index) => (
                <div key={index}>{data}</div>
            ))}
        </Card>
    );
}
