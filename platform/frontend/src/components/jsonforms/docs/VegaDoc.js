import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
    Callout,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function VegaDoc({ closePanel }) {
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
    return (
        <>
            <div className="border-bottom" style={{ padding: "10px 20px" }}>
                <Button
                    outlined
                    text="Back"
                    onClick={closePanel}
                    icon={faIcon({ icon: faArrowLeft })}
                />
            </div>
            <div
                className={Classes.RUNNING_TEXT}
                style={{
                    padding: 20,
                    overflowY: "auto",
                }}
            >
                <div style={{ marginBottom: 20 }}>
                    <H1 style={{ margin: 0 }}>Vega</H1>
                </div>
                <Callout icon={null} intent={Intent.SUCCESS}>
                    It is recommended to set <Code>width</Code> &#40;integer, in
                    pixels&#41; to mitigate unexpected rendering behaviors.
                </Callout>
                <H2>Example</H2>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(uiSchemaJson, null, 4)}
                        />
                    </div>
                    <div>
                        <Tag style={{ marginBottom: 13 }} minimal>
                            UI Schema
                        </Tag>
                    </div>
                    <JsonViewer json={uiSchemaJson} enableClipboard={false} />
                </pre>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(dataJson, null, 4)}
                        />
                    </div>
                    <div>
                        <Tag style={{ marginBottom: 13 }} minimal>
                            Data
                        </Tag>
                    </div>
                    <JsonViewer json={dataJson} enableClipboard={false} />
                </pre>
                <H2>Props</H2>
                <HTMLTable
                    className="docs-prop-table"
                    style={{ width: "100%" }}
                >
                    <thead>
                        <tr>
                            <th>Props</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>{docProps.style}</tbody>
                </HTMLTable>
            </div>
        </>
    );
}
