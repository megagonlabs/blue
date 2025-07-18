import { Intent, Tag } from "@blueprintjs/core";
import _ from "lodash";
import { useEffect, useState } from "react";
export default function ContainerLogViewer({ log }) {
    const { localeString, logMessage } = log;
    const [logElements, setLogElements] = useState([]);
    useEffect(() => {
        try {
            const jsonLogMessage = JSON.parse(logMessage);
            const outputFormat = _.get(jsonLogMessage, "output_format", null);
            if (_.isEqual(outputFormat, "json")) {
                const keys = _.keys(jsonLogMessage).filter(
                    (key) => !_.includes(["output_format", "time"], key)
                );
                let result = [];
                for (let i = 0; i < _.size(keys); i++) {
                    result.push(<Tag>{keys[i]}</Tag>);
                    result.push(jsonLogMessage[keys[i]]);
                }
                setLogElements(result);
            }
        } catch (error) {
            setLogElements([logMessage]);
        }
    }, [log]);
    return (
        <div
            style={{
                display: "flex",
                flexWrap: "wrap",
                gap: 5,
                alignItems: "center",
            }}
        >
            <Tag intent={Intent.PRIMARY}>{localeString}</Tag>
            {logElements.map((e) => e)}
        </div>
    );
}
