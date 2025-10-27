import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    EntityTitle,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faListDropdown } from "@fortawesome/sharp-duotone-solid-svg-icons";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
    type: "Control",
    label: "",
    props: {
        inline: false,
        helperText: null,
        style: {},
        large: false,
    },
    scope: "#/properties/...",
};
const dataSchemaJson = {
    type: "object",
    properties: {
        blood_type: {
            type: "string",
            enum: ["A", "B", "AB", "O"],
        },
    },
};
export default function EnumDoc() {
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <EntityTitle
                    title="Enum"
                    heading={H1}
                    tags={
                        <Tag size={Size.LARGE} minimal intent={Intent.PRIMARY}>
                            Control
                        </Tag>
                    }
                    icon={<FAIcon icon={faListDropdown} size={30} />}
                />
            </div>
            <H2>Example</H2>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Enum (Control) JSON"
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        UI Schema
                    </Tag>
                </div>
                <JSONViewer json={docJson} enableClipboard={false} />
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
            <H2>Props</H2>
            <HTMLTable className="docs-prop-table" style={{ width: "100%" }}>
                <thead>
                    <tr>
                        <th>Props</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {docProps.inline}
                    {docProps.helperText}
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
