import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
    Callout,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function LabelDoc({ closePanel }) {
    const docJson = {
        type: "Label",
        label: "",
        props: {
            muted: false,
            small: false,
            large: false,
            style: {},
        },
    };
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
                    <H1 style={{ margin: 0 }}>Label</H1>
                </div>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(docJson, null, 4)}
                            copyMessage="Copied Label JSON"
                        />
                    </div>
                    <JsonViewer json={docJson} enableClipboard={false} />
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
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
