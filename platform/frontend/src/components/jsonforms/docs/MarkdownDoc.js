import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
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
export default function MarkdownDoc({ closePanel }) {
    const uiSchemaJson = {
        type: "Markdown",
        scope: "#/properties/markdown",
        props: {
            style: {},
        },
    };
    const dataSchemaJson = {
        type: "object",
        properties: {
            markdown: {
                "md-content": "# H1",
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
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        marginBottom: 20,
                    }}
                >
                    <H1 style={{ margin: 0 }}>Markdown</H1>
                </div>
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
                                <div style={{ width: 81 }}>
                                    <Code>md-content</Code>
                                </div>
                            </td>
                            <td>
                                <strong>string</strong>
                                <em
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        "docs-prop-default"
                                    )}
                                >
                                    &quot;&quot;
                                </em>
                                <div>Markup language content.</div>
                                <Tag
                                    large
                                    intent={Intent.WARNING}
                                    minimal
                                    style={{ marginTop: 5 }}
                                >
                                    <strong>md-content</strong> must be
                                    specified under data schema
                                </Tag>
                            </td>
                        </tr>
                        {docProps.style}
                    </tbody>
                </HTMLTable>
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
                            docJson={JSON.stringify(dataSchemaJson, null, 4)}
                        />
                    </div>
                    <div>
                        <Tag style={{ marginBottom: 13 }} minimal>
                            Data Schema
                        </Tag>
                    </div>
                    <JsonViewer json={dataSchemaJson} enableClipboard={false} />
                </pre>
            </div>
        </>
    );
}
