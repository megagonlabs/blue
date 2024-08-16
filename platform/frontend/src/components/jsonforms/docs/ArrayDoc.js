import { faIcon } from "@/components/icon";
import {
    Button,
    Callout,
    Classes,
    H1,
    H2,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function ArrayDoc({ closePanel }) {
    const uiSchemaJson = JSON.stringify(
        {
            type: "Control",
            scope: "#/properties/shopping_list",
            options: {
                detail: {
                    type: "VerticalLayout",
                    elements: [
                        {
                            type: "Label",
                            label: "Name",
                        },
                        {
                            type: "Control",
                            scope: "#/properties/name",
                        },
                    ],
                },
            },
        },
        null,
        4
    );
    const dataSchemaJson = JSON.stringify(
        {
            type: "object",
            properties: {
                shopping_list: {
                    type: "array",
                    items: {
                        type: "object",
                        properties: {
                            name: {
                                type: "string",
                            },
                        },
                    },
                },
            },
        },
        null,
        4
    );
    return (
        <>
            <div className="bp-border-bottom" style={{ padding: "10px 20px" }}>
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
                    <H1 style={{ margin: 0 }}>Array</H1>
                </div>
                <Callout intent={Intent.WARNING} icon={null}>
                    This is not a type but inlined layout configuration for UI
                    Schema.
                </Callout>
                <H2>Example</H2>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton docJson={uiSchemaJson} />
                    </div>
                    <div>
                        <Tag minimal>UI Schema</Tag>
                    </div>
                    {uiSchemaJson}
                </pre>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton docJson={dataSchemaJson} />
                    </div>
                    <div>
                        <Tag minimal>Data Schema</Tag>
                    </div>
                    {dataSchemaJson}
                </pre>
            </div>
        </>
    );
}
