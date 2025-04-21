import JsonViewer from "@/components/JsonViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import { H1, H2, HTMLTable, Intent, Pre, Size, Tag } from "@blueprintjs/core";
import CopyDocJsonButton from "./CopyDocJsonButton";
const docJson = {
    type: "Control",
    props: {
        inline: false,
        helperText: null,
        style: {},
    },
    scope: "#/properties/...",
    required: false,
};
export default function NumberDoc() {
    return (
        <div>
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    marginBottom: 20,
                }}
            >
                <H1 style={{ margin: 0 }}>Number</H1>
                <Tag
                    size={Size.LARGE}
                    style={{ marginLeft: 10 }}
                    minimal
                    intent={Intent.PRIMARY}
                >
                    Control
                </Tag>
            </div>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJsonButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Number (Control) JSON"
                    />
                </div>
                <JsonViewer json={docJson} enableClipboard={false} />
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
            {docProps.numericInputTip}
        </div>
    );
}
