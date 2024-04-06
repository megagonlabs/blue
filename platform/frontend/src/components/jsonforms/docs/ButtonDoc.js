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
    Intent,
    Tooltip,
} from "@blueprintjs/core";
import { faArrowLeft, faCopy } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
export default function ButtonDoc({ closePanel }) {
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
                    <H1 style={{ margin: 0 }}>Button</H1>
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
                                large: false,
                                outlined: false,
                                intent: null,
                                style: {},
                                nameId: null,
                            },
                            scope: "",
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
                                    compact
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
                                    compact
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
                        {docProps.nameId}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
