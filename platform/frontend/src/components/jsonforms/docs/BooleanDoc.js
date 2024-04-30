import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Button,
    Callout,
    Checkbox,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Switch,
    Tag,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function BooleanDoc({ closePanel }) {
    const docJson = JSON.stringify(
        {
            type: "Control",
            label: "",
            props: {
                switch: false,
                style: {},
                nameId: null,
            },
            scope: "",
            required: false,
        },
        null,
        4
    );
    return (
        <>
            <div className="bp-border-bottom" style={{ padding: 10 }}>
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
                    <H1 style={{ margin: 0 }}>Boolean</H1>
                    <Tag
                        large
                        style={{ marginLeft: 10 }}
                        minimal
                        intent={Intent.PRIMARY}
                    >
                        Control
                    </Tag>
                </div>
                <pre style={{ position: "relative" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={docJson}
                            copyMessage="Copied Boolean (Control) JSON"
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
                                        marginTop: 5,
                                        display: "flex",
                                        gap: 10,
                                        flexWrap: "wrap",
                                    }}
                                >
                                    <Checkbox
                                        style={{ margin: 0 }}
                                        label="switch: false"
                                    />
                                    <Switch
                                        style={{ margin: 0 }}
                                        label="switch: true"
                                    />
                                </Callout>
                            </td>
                        </tr>
                        {docProps.style}
                        {docProps.nameId}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
