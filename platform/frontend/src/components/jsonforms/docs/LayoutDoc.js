import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
    Callout,
    Card,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function LayoutDoc({ closePanel }) {
    const docJsonVertical = {
        type: "VerticalLayout",
        elements: [],
    };
    const docJSonHorizontal = {
        type: "HorizontalLayout",
        props: { spaceEvenly: true, style: {} },
        elements: [],
    };
    return (
        <>
            <div className="border-bottom" style={{ padding: "10px 20px" }}>
                <Button
                    variant="outlined"
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
                    <H1 style={{ margin: 0 }}>Layout</H1>
                </div>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(docJsonVertical, null, 4)}
                            copyMessage="Copied Layout JSON"
                        />
                    </div>
                    <JsonViewer
                        json={docJsonVertical}
                        enableClipboard={false}
                    />
                </pre>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(docJSonHorizontal, null, 4)}
                            copyMessage="Copied Layout JSON"
                        />
                    </div>
                    <JsonViewer
                        json={docJSonHorizontal}
                        enableClipboard={false}
                    />
                </pre>
                <H2>Vertical vs. Horizontal</H2>
                <Callout
                    style={{
                        display: "flex",
                        rowGap: 15,
                        flexDirection: "column",
                    }}
                >
                    <Card compact>1</Card>
                    <Card compact>2</Card>
                </Callout>
                <Callout
                    style={{
                        display: "flex",
                        columnGap: 15,
                        flexDirection: "row",
                    }}
                >
                    <Card compact style={{ flex: 1 }}>
                        1
                    </Card>
                    <Card compact style={{ flex: 1 }}>
                        2
                    </Card>
                </Callout>
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
                    <tbody>
                        <tr>
                            <td>
                                <Code>spaceEvenly</Code>
                            </td>
                            <td>
                                <strong>boolean</strong>
                                <em
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        "docs-prop-default"
                                    )}
                                >
                                    true
                                </em>
                                <div>
                                    Whether to have elements with equal width.
                                </div>
                                <Tag
                                    size="large"
                                    intent={Intent.PRIMARY}
                                    minimal
                                    style={{ marginTop: 5 }}
                                >
                                    Applies to <strong>HorizontalLayout</strong>
                                    &nbsp;only
                                </Tag>
                            </td>
                        </tr>
                        {docProps.style}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
