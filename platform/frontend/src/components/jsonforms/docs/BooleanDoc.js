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
    Tooltip,
} from "@blueprintjs/core";
import { faArrowLeft, faCopy } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
export default function BooleanDoc({ closePanel }) {
    return (
        <>
            <div
                style={{
                    padding: 10,
                    borderBottom: "1px solid rgba(17, 20, 24, 0.15)",
                }}
            >
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
                            label: null,
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
