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
    Intent,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function ButtonDoc({ closePanel }) {
    const docJson = {
        type: "Button",
        label: "",
        props: {
            large: false,
            outlined: false,
            intent: null,
            style: {},
            action: null,
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
                    <H1 style={{ margin: 0 }}>Button</H1>
                </div>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(docJson, null, 4)}
                            copyMessage="Copied Button JSON"
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
                                    Whether this button should use large styles.
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <Code>outlined</Code>
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
                                    Whether this button should use outlined
                                    styles.
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
                                    <Button text="outlined: false" />{" "}
                                    <Button outlined text="outlined: true" />
                                </Callout>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <Code>intent</Code>
                            </td>
                            <td>
                                <strong>string</strong>
                                <em
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        "docs-prop-default"
                                    )}
                                >
                                    null
                                </em>
                                <div>
                                    Visual intent color to apply to element.
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
                                    <Button
                                        intent={Intent.DANGER}
                                        text='"danger"'
                                    />
                                    <Button
                                        intent={Intent.WARNING}
                                        text='"warning"'
                                    />
                                    <Button
                                        intent={Intent.PRIMARY}
                                        text='"primary"'
                                    />
                                    <Button
                                        intent={Intent.SUCCESS}
                                        text='"success"'
                                    />
                                </Callout>
                            </td>
                        </tr>
                        {docProps.style}
                        <tr>
                            <td>
                                <Code>action</Code>
                            </td>
                            <td>
                                <strong>string</strong>
                                <em
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        "docs-prop-default"
                                    )}
                                >
                                    null
                                </em>
                                <div>Name of the action.</div>
                            </td>
                        </tr>
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
