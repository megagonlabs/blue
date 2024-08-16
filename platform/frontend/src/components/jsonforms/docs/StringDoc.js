import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Button,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function StringDoc({ closePanel }) {
    const docJson = JSON.stringify(
        {
            type: "Control",
            options: {
                multi: false,
            },
            props: {
                inline: false,
                placeholder: null,
                helperText: null,
                style: {},
            },
            scope: "",
            required: false,
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
                    <H1 style={{ margin: 0 }}>String</H1>
                    <Tag
                        large
                        style={{ marginLeft: 10 }}
                        minimal
                        intent={Intent.PRIMARY}
                    >
                        Control
                    </Tag>
                </div>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={docJson}
                            copyMessage="Copied String (Control) JSON"
                        />
                    </div>
                    {docJson}
                </pre>
                <H2>Props</H2>
                <HTMLTable
                    className="docs-prop-table"
                    style={{ width: "100%" }}
                >
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
        </>
    );
}
