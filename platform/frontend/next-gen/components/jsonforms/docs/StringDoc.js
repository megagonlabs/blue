import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
    Size,
    Tag,
} from "@blueprintjs/core";
import classNames from "classnames";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
    type: "Control",
    options: { multi: false },
    props: {
        inline: false,
        placeholder: null,
        helperText: null,
        style: {},
    },
    scope: "#/properties/...",
    required: false,
};
export default function StringDoc() {
    return (
        <div>
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    marginBottom: 20,
                }}
            >
                <H1 style={{ margin: 0 }}>String</H1>
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
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied String (Control) JSON"
                    />
                </div>
                <JSONViewer json={docJson} enableClipboard={false} />
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
                    <tr>
                        <td>
                            <Code>options.multi</Code>
                        </td>
                        <td>
                            <strong>string</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>
                                Whether to render as multi-line textarea or
                                single-line input.
                            </div>
                        </td>
                    </tr>
                    {docProps.placeholder}
                    {docProps.inline}
                    {docProps.helperText}
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
