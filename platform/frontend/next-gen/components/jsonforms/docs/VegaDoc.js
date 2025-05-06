import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Callout,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
    Size,
    Tag,
} from "@blueprintjs/core";
import CopyDocJSONButton from "./CopyDocJSONButton";
const uiSchemaJson = {
    type: "Vega",
    scope: "#/properties/vega-spec",
    props: { style: {} },
};
const dataJson = {
    "vega-spec": {
        $schema: "https://vega.github.io/schema/vega-lite/v2.json",
        description: "Bar Chart with Negative values",
        width: 400,
        height: 400,
        data: {
            values: [
                { a: "A", b: -118 },
                { a: "B", b: -125 },
                { a: "C", b: -163 },
                { a: "D", b: -131 },
                { a: "E", b: 181 },
                { a: "F", b: 153 },
                { a: "G", b: 119 },
                { a: "H", b: 187 },
            ],
        },
        mark: "bar",
        encoding: {
            x: { field: "b", type: "quantitative" },
            y: {
                field: "a",
                type: "ordinal",
                axis: { offset: -200, title: null },
            },
            color: {
                condition: {
                    test: "datum.b < 0",
                    value: "#F29135",
                },
                value: "#4F81B2",
            },
        },
    },
};
export default function VegaDoc() {
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <H1 style={{ margin: 0 }}>Vega</H1>
            </div>
            <Callout icon={null} intent={Intent.SUCCESS}>
                It is recommended to set <Code>width</Code> &#40;integer, in
                pixels&#41; to mitigate unexpected rendering behaviors.
            </Callout>
            <H2>Example</H2>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(uiSchemaJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        UI Schema
                    </Tag>
                </div>
                <JSONViewer json={uiSchemaJson} enableClipboard={false} />
            </Pre>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(dataJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        Data
                    </Tag>
                </div>
                <JSONViewer json={dataJson} enableClipboard={false} />
            </Pre>
            <H2>Props</H2>
            <HTMLTable className="docs-prop-table" style={{ width: "100%" }}>
                <thead>
                    <tr>
                        <th>Props</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>{docProps.style}</tbody>
            </HTMLTable>
        </div>
    );
}
