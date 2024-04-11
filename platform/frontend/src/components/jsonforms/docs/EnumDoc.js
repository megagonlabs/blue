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
    Tooltip,
} from "@blueprintjs/core";
import { faArrowLeft, faCopy } from "@fortawesome/pro-duotone-svg-icons";
export default function EnumDoc({ closePanel }) {
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
                    <H1 style={{ margin: 0 }}>Enum</H1>
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
                        <Tooltip minimal placement="bottom-end" content="Copy">
                            <Button
                                minimal
                                large
                                icon={faIcon({ icon: faCopy })}
                            />
                        </Tooltip>
                    </div>
                    {JSON.stringify(
                        {
                            type: "Control",
                            label: "",
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
                    )}
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
            </div>
        </>
    );
}
