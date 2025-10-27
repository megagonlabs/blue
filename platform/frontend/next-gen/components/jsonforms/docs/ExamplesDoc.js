import { MESSAGE_OVERFLOW_THRESHOLD } from "@/components/constants";
import JSONViewer from "@/components/JSONViewer";
import { Callout, H1, Pre, Size, Tag } from "@blueprintjs/core";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import { JSONFORMS_RENDERERS } from "../renderers";
import CopyDocJSONButton from "./CopyDocJSONButton";
const EXAMPLE_SPECS = {
    candidates_table: {
        title: "1. Candidates table",
        uiSchemaJson: {
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
        dataSchemaJson: {
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
        dataJson: {
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
        },
    },
};
export default function ExamplesDoc() {
    return (
        <div>
            {["candidates_table"].map((key) => {
                const example = EXAMPLE_SPECS[key];
                return (
                    <>
                        <H1 style={{ marginTop: 0 }}>{example.title}</H1>
                        <Callout>
                            <div className="message-bubble-callout">
                                <JsonForms
                                    schema={example.dataSchemaJson}
                                    uischema={example.uiSchemaJson}
                                    data={example.dataJson}
                                    renderers={JSONFORMS_RENDERERS}
                                    cells={vanillaCells}
                                />
                            </div>
                        </Callout>
                        <Pre
                            style={{
                                position: "relative",
                                overflow: "hidden",
                                maxHeight: MESSAGE_OVERFLOW_THRESHOLD,
                            }}
                        >
                            <div
                                style={{
                                    position: "absolute",
                                    right: 15,
                                    top: 13,
                                }}
                            >
                                <CopyDocJSONButton
                                    docJson={JSON.stringify(
                                        example.uiSchemaJson,
                                        null,
                                        4
                                    )}
                                />
                            </div>
                            <div>
                                <Tag
                                    size={Size.LARGE}
                                    style={{ marginBottom: 10 }}
                                    minimal
                                >
                                    UI Schema
                                </Tag>
                            </div>
                            <JSONViewer
                                json={example.uiSchemaJson}
                                enableClipboard={false}
                            />
                        </Pre>
                        <Pre
                            style={{
                                position: "relative",
                                overflow: "hidden",
                                maxHeight: MESSAGE_OVERFLOW_THRESHOLD,
                            }}
                        >
                            <div
                                style={{
                                    position: "absolute",
                                    right: 15,
                                    top: 13,
                                }}
                            >
                                <CopyDocJSONButton
                                    docJson={JSON.stringify(
                                        example.dataSchemaJson,
                                        null,
                                        4
                                    )}
                                />
                            </div>
                            <div>
                                <Tag
                                    size={Size.LARGE}
                                    style={{ marginBottom: 10 }}
                                    minimal
                                >
                                    Data Schema
                                </Tag>
                            </div>
                            <JSONViewer
                                json={example.dataSchemaJson}
                                enableClipboard={false}
                            />
                        </Pre>
                        <Pre
                            style={{
                                position: "relative",
                                overflow: "hidden",
                                maxHeight: MESSAGE_OVERFLOW_THRESHOLD,
                            }}
                        >
                            <div
                                style={{
                                    position: "absolute",
                                    right: 15,
                                    top: 13,
                                }}
                            >
                                <CopyDocJSONButton
                                    docJson={JSON.stringify(
                                        example.dataJson,
                                        null,
                                        4
                                    )}
                                />
                            </div>
                            <div>
                                <Tag
                                    size={Size.LARGE}
                                    style={{ marginBottom: 10 }}
                                    minimal
                                >
                                    Data
                                </Tag>
                            </div>
                            <JSONViewer
                                json={example.dataJson}
                                enableClipboard={false}
                            />
                        </Pre>
                    </>
                );
            })}
        </div>
    );
}
