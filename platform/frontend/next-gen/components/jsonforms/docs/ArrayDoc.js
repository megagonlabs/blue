import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import {
    Callout,
    EntityTitle,
    H1,
    H2,
    Intent,
    Pre,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faListUl } from "@fortawesome/sharp-duotone-solid-svg-icons";
import CopyDocJSONButton from "./CopyDocJSONButton";
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
            <EntityTitle
                title="Array"
                heading={H1}
                icon={<FAIcon icon={faListUl} size={30} />}
            />
            <Callout intent={Intent.WARNING} icon={null}>
                This is not a type, but an inlined layout configuration.
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
                        docJson={JSON.stringify(dataSchemaJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        Data Schema
                    </Tag>
                </div>
                <JSONViewer json={dataSchemaJson} enableClipboard={false} />
            </Pre>
        </div>
    );
}
