import JsonViewer from "@/components/JsonViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Callout,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
} from "@blueprintjs/core";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
const docJson = {
    type: "Label",
    scope: "#/properties/...",
    label: "",
    props: {
        muted: false,
        small: false,
        large: false,
        style: {},
    },
};
export default function LabelDoc() {
    return (
        <div
            className={classNames(
                "full-parent-dimension",
                Classes.RUNNING_TEXT
            )}
            style={{ padding: 20, overflowY: "auto" }}
        >
            <div style={{ marginBottom: 20 }}>
                <H1 style={{ margin: 0 }}>Label</H1>
            </div>
            <Callout icon={null} intent={Intent.WARNING}>
                <Code>label</Code> and <Code>scope</Code> are mutually
                exclusive; if <Code>scope</Code> is not specified, then{" "}
                <Code>label</Code> value will be used.
            </Callout>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJsonButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Label JSON"
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
                    <tr>
                        <td>
                            <Code>muted</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>Change text color to a gentler gray.</div>
                            <Callout style={{ margin: 0, marginTop: 5 }}>
                                <div className={Classes.TEXT_MUTED}>
                                    muted: true
                                </div>
                                <div>muted: false</div>
                            </Callout>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>small</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>Use a smaller font size.</div>
                            <Callout style={{ margin: 0, marginTop: 5 }}>
                                <div className={Classes.TEXT_SMALL}>
                                    small: true
                                </div>
                                <div>small: false</div>
                            </Callout>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>large</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>Use a larger font size.</div>
                            <Callout style={{ margin: 0, marginTop: 5 }}>
                                <div className={Classes.TEXT_LARGE}>
                                    large: true
                                </div>
                                <div>large: false</div>
                            </Callout>
                        </td>
                    </tr>
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
