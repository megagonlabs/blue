import { JSONFORMS_RENDERERS } from "@/components/constant";
import { faIcon } from "@/components/icon";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import { Button, Callout, Classes, H1, Intent, Tag } from "@blueprintjs/core";
import {
    faArrowLeft,
    faSparkles,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import CopyDocJsonButton from "../docs/CopyDocJsonButton";
export default function CandidatesTable({
    closePanel,
    setJsonUischema,
    setData,
    setJsonSchema,
}) {
    const uiSchemaJson = {
            type: "VerticalLayout",
            elements: [
                {
                    type: "Table",
                    scope: "#/properties/table_data",
                    props: { bordered: true },
                    columns: ["Candidate", "Matches", "Actions"],
                    rowCells: [
                        {
                            type: "VerticalLayout",
                            elements: [
                                {
                                    type: "HorizontalLayout",
                                    props: {
                                        spaceEvenly: false,
                                    },
                                    elements: [
                                        {
                                            type: "Control",
                                            scope: "#/properties/selected",
                                        },
                                        {
                                            type: "Label",
                                            scope: "#/properties/name",
                                        },
                                    ],
                                },
                                {
                                    type: "Label",
                                    scope: "#/properties/title",
                                },
                            ],
                        },
                        {
                            type: "Markdown",
                            scope: "#/properties/matches",
                        },
                        {
                            type: "Button",
                            label: "View",
                        },
                    ],
                },
            ],
        },
        dataSchemaJson = {
            type: "object",
            properties: {
                table_data: {
                    type: "array",
                    items: {
                        type: "object",
                        properties: {
                            selected: {
                                type: "boolean",
                            },
                        },
                    },
                },
            },
        },
        dataJson = {
            table_data: [
                {
                    name: "candidate 3711",
                    title: "Technical Manager, Cisco",
                    matches: "pytorch\nmachine learning\nc++\nllms",
                },
                {
                    name: "candidate 3712",
                    title: "Data Scientist 3, Google",
                    matches:
                        "scikit learn\npytorch\nclustering\nalgorithm design\ndepp learning",
                },
                {
                    name: "candidate 3713",
                    title: "Staff Research Scientist, DeepMind",
                    matches:
                        "pytorch\nmodel training\nllm architecture\nfine tuning",
                },
            ],
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
                    <H1 style={{ margin: 0 }}>Candidates table</H1>
                </div>
                <Button
                    onClick={() => {
                        setJsonUischema(JSON.stringify(uiSchemaJson, null, 4));
                        setJsonSchema(JSON.stringify(dataSchemaJson, null, 4));
                        setTimeout(() => {
                            setData(dataJson);
                        }, 0);
                    }}
                    icon={faIcon({ icon: faSparkles })}
                    large
                    intent={Intent.SUCCESS}
                    text="Try"
                />
                <Callout>
                    <div className="message-bubble-callout">
                        <JsonForms
                            schema={dataSchemaJson}
                            uischema={uiSchemaJson}
                            data={dataJson}
                            renderers={JSONFORMS_RENDERERS}
                            cells={vanillaCells}
                        />
                    </div>
                </Callout>
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
            </div>
        </>
    );
}
