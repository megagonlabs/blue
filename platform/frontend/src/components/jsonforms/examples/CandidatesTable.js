import { JSONFORMS_RENDERERS } from "@/components/constant";
import { faIcon } from "@/components/icon";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import { Button, Callout, Classes, H1, Tag } from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import CopyDocJsonButton from "../docs/CopyDocJsonButton";
export default function CandidatesTable({ closePanel }) {
    const uiSchemaJson = {
            type: "VerticalLayout",
            elements: [
                {
                    type: "Table",
                    scope: "#/properties/table_data",
                    props: {
                        bordered: true,
                    },
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
                    title: "technical manager, cisco",
                    matches: "pytorch\nmachine learning\nc++\nllms",
                },
                {
                    name: "candidate 3712",
                    title: "data scientist 3, google",
                    matches:
                        "scikit learn\npytorch\nclustering\nalgorithm design\ndepp learning",
                },
                {
                    name: "candidate 3713",
                    title: "staff research scientist, deepmind",
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
                <Callout>
                    <JsonForms
                        schema={dataSchemaJson}
                        uischema={uiSchemaJson}
                        data={dataJson}
                        renderers={JSONFORMS_RENDERERS}
                        cells={vanillaCells}
                    />
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
