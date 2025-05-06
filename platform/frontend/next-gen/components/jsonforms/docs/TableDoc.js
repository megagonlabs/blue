import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Card,
    Checkbox,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Pre,
    Size,
} from "@blueprintjs/core";
import classNames from "classnames";
import { useState } from "react";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
        type: "Table",
        scope: "#/properties/...",
        columns: [],
        rowCells: [],
        props: {
            compact: false,
            bordered: false,
            striped: false,
            style: {},
        },
    },
    exampleJson = {
        type: "Table",
        scope: "...",
        columns: ["Column 1", "Column 2"],
        rowCells: [
            {
                type: "Label",
                label: "Cell 1",
            },
            {
                type: "Label",
                label: "Cell 2",
            },
        ],
    };
export default function TableDoc() {
    const [compact, setCompact] = useState(false);
    const [bordered, setBordered] = useState(false);
    const [striped, setStriped] = useState(false);
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <H1 style={{ margin: 0 }}>Table</H1>
            </div>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Tab JSON"
                    />
                </div>
                <JSONViewer json={docJson} enableClipboard={false} />
            </Pre>
            <H2>Example</H2>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(exampleJson, null, 4)}
                    />
                </div>
                <JSONViewer json={exampleJson} enableClipboard={false} />
            </Pre>
            <div
                style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 20,
                    marginTop: 20,
                }}
            >
                <HTMLTable
                    compact={compact}
                    striped={striped}
                    bordered={bordered}
                    style={{ width: "100%", maxWidth: 250 }}
                >
                    <thead>
                        <tr>
                            <th>Column 1</th>
                            <th>Column 2</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Cell 1</td>
                            <td>Cell 2</td>
                        </tr>
                        <tr>
                            <td>Cell 1</td>
                            <td>Cell 2</td>
                        </tr>
                    </tbody>
                </HTMLTable>
                <Card style={{ padding: 10 }}>
                    <Checkbox
                        onChange={(event) => setCompact(event.target.checked)}
                        size={Size.LARGE}
                    >
                        Compact
                    </Checkbox>
                    <Checkbox
                        onChange={(event) => setBordered(event.target.checked)}
                        size={Size.LARGE}
                    >
                        Bordered
                    </Checkbox>
                    <Checkbox
                        className="margin-0"
                        onChange={(event) => setStriped(event.target.checked)}
                        size={Size.LARGE}
                    >
                        Striped
                    </Checkbox>
                </Card>
            </div>
            <H2>Props</H2>
            <HTMLTable className="docs-prop-table" style={{ width: "100%" }}>
                <thead>
                    <tr>
                        <th>Props</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <Code>columns</Code>
                        </td>
                        <td>
                            <strong>array</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                &#91;at least 1 element&#93;
                            </em>
                            <div>Consists of table column headers.</div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>rowCells</Code>
                        </td>
                        <td>
                            <strong>array</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                &#91;at least 1 element&#93;
                            </em>
                            <div>
                                Consists of layout definition for table cells
                                &#40;repeats for each row of data&#41;.
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>compact</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>Use compact appearance with less padding.</div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>bordered</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>Enable borders between rows and cells.</div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>striped</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>
                                Use an alternate background color on
                                odd-numbered rows.
                            </div>
                        </td>
                    </tr>
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
