import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Button,
    Classes,
    H1,
    H2,
    HTMLTable,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function IntegerDoc({ closePanel }) {
    const docJson = JSON.stringify(
        {
            type: "Control",
            props: {
                inline: false,
                helperText: null,
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
                    <H1 style={{ margin: 0 }}>Integer</H1>
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
                            copyMessage="Copied Integer (Control) JSON"
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
                        {docProps.inline}
                        {docProps.helperText}
                        {docProps.style}
                        {docProps.nameId}
                    </tbody>
                </HTMLTable>
                {docProps.numericInputTip}
            </div>
        </>
    );
}
