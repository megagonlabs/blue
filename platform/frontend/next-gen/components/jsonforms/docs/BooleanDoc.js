import * as docProps from "@/components/jsonforms/docs/constant";
import JsonViewer from "@/components/JsonViewer";
import {
    Callout,
    Checkbox,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
    Size,
    Switch,
    Tag,
} from "@blueprintjs/core";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
const docJson = {
    type: "Control",
    label: "",
    props: {
        switch: false,
        large: false,
        style: {},
    },
    scope: "#/properties/...",
    required: false,
};
export default function BooleanDoc() {
    return (
        <div
            className={classNames(
                "full-parent-dimension",
                Classes.RUNNING_TEXT
            )}
            style={{ padding: 20, overflowY: "auto" }}
        >
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    marginBottom: 20,
                }}
            >
                <H1 style={{ margin: 0 }}>Boolean</H1>
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
                        copyMessage="Copied Boolean (Control) JSON"
                    />
                </div>
                <JsonViewer enableClipboard={false} json={docJson} />
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
                            <Code>switch</Code>
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
                            <div>
                                Whether this control should use switch
                                component.
                            </div>
                            <Callout
                                style={{
                                    margin: 0,
                                    marginTop: 10,
                                    display: "flex",
                                    gap: 10,
                                    flexWrap: "wrap",
                                }}
                            >
                                <Checkbox
                                    name="boolean-doc-switch-false"
                                    style={{ margin: 0 }}
                                    label="switch: false"
                                />
                                <Switch
                                    name="boolean-doc-switch-true"
                                    style={{ margin: 0 }}
                                    label="switch: true"
                                />
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
                            <div>
                                Whether this control should use large styles.
                            </div>
                            <Callout
                                style={{
                                    margin: 0,
                                    marginTop: 10,
                                    display: "flex",
                                    gap: 10,
                                    flexWrap: "wrap",
                                }}
                            >
                                <Checkbox
                                    name="boolean-doc-check-large-false"
                                    style={{ margin: 0 }}
                                    label="large: false"
                                />
                                <Checkbox
                                    size={Size.LARGE}
                                    name="boolean-doc-check-large-true"
                                    style={{ margin: 0 }}
                                    label="large: true"
                                />
                                <Switch
                                    name="boolean-doc-switch-large-false"
                                    style={{ margin: 0 }}
                                    label="large: false"
                                />
                                <Switch
                                    size={Size.LARGE}
                                    name="boolean-doc-switch-large-true"
                                    style={{ margin: 0 }}
                                    label="large: true"
                                />
                            </Callout>
                        </td>
                    </tr>
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
