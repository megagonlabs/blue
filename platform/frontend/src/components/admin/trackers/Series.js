import { AppContext } from "@/components/contexts/app-context";
import { Card, Colors } from "@blueprintjs/core";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { VegaLite } from "react-vega";
export default function Series({ tracker, graphKey }) {
    const { appState } = useContext(AppContext);
    const [data, setData] = useState([]);
    const [fields, setFields] = useState([]);
    const trackerGraph = _.get(
        appState.tracker.data,
        [tracker, "graph", graphKey],
        {}
    );
    useEffect(() => {
        let newFields = [],
            newData = [];
        const entries = Object.entries(trackerGraph);
        for (let i = 0; i < _.size(entries); i++) {
            let data = { epoch: _.toInteger(entries[i][0]) };
            const entry = entries[i][1],
                entryKeys = Object.keys(entry);
            for (let j = 0; j < _.size(entryKeys); j++) {
                const key = entryKeys[j];
                data[key] = entry[key]["value"];
                newFields.push({
                    field: key,
                    title: entry[key]["label"],
                });
            }
            newData.push(data);
        }
        setData(newData);
        setFields(_.uniqBy(newFields, "field"));
    }, [trackerGraph]);
    const fieldKeys = fields.map((field) => field["field"]);
    const VEGA_SPEC = {
        $schema: "https://vega.github.io/schema/vega-lite/v5.json",
        data: { name: "values" },
        width: "container",
        height: 93,
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
                                    oneOf: fieldKeys,
                                },
                            },
                        ],
                    },
                ],
                encoding: {
                    color: {
                        sort: fieldKeys,
                        field: "key",
                        title: null,
                        type: "nominal",
                        scale: {
                            range: [
                                Colors.VERMILION3,
                                Colors.VIOLET3,
                                Colors.CERULEAN3,
                                Colors.FOREST3,
                                Colors.GOLD3,
                                Colors.ROSE3,
                                Colors.INDIGO3,
                                Colors.TURQUOISE3,
                                Colors.LIME3,
                                Colors.SEPIA3,
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
                        ...fields.map((field) => ({
                            ...field,
                            type: "quantitative",
                        })),
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
        transform: [{ fold: fieldKeys }],
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
            y: { title: "", type: "quantitative" },
        },
    };
    return (
        <Card style={{ padding: 10 }} className="full-parent-width">
            <VegaLite
                data={{ values: data }}
                spec={VEGA_SPEC}
                className="full-parent-width"
                actions={false}
            />
        </Card>
    );
}
