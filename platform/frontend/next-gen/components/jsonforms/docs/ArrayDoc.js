import JsonViewer from "@/components/JsonViewer";
import { Callout, H1, H2, Intent, Pre, Size, Tag } from "@blueprintjs/core";
import CopyDocJsonButton from "./CopyDocJsonButton";
const uiSchemaJson = {
    type: "Control",
    scope: "#/properties/shopping_list",
    options: {
        detail: {
            type: "VerticalLayout",
            elements: [
                { type: "Label", label: "Name" },
                { type: "Control", scope: "#/properties/name" },
            ],
        },
    },
};
const dataSchemaJson = {
    type: "object",
    properties: {
        shopping_list: {
            type: "array",
            items: {
                type: "object",
                properties: { name: { type: "string" } },
            },
        },
    },
};
export default function BasicsDoc() {
    return (
        <div>
            <H1 style={{ marginTop: 0 }}>Array</H1>
            <Callout intent={Intent.WARNING} icon={null}>
                This is not a type, but an inlined layout configuration.
            </Callout>
            <H2>Example</H2>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJsonButton
                        docJson={JSON.stringify(uiSchemaJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        UI Schema
                    </Tag>
                </div>
                <JsonViewer json={uiSchemaJson} enableClipboard={false} />
            </Pre>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJsonButton
                        docJson={JSON.stringify(dataSchemaJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        Data Schema
                    </Tag>
                </div>
                <JsonViewer json={dataSchemaJson} enableClipboard={false} />
            </Pre>
        </div>
    );
}
