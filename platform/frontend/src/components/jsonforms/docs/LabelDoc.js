import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Button,
    Callout,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Tooltip,
} from "@blueprintjs/core";
import { faArrowLeft, faCopy } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
export default function LabelDoc({ closePanel }) {
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
                    <H1 style={{ margin: 0 }}>Label</H1>
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
                                muted: false,
                                small: false,
                                large: false,
                                style: {},
                                nameId: null,
                            },
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
                        {docProps.nameId}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
