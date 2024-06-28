import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import { Button, Classes, Code, H1, H2, HTMLTable } from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function GroupDoc({ closePanel }) {
    const docJson = JSON.stringify(
        {
            type: "Group",
            label: "",
            props: {
                collapsible: false,
                defaultIsOpen: true,
                compact: false,
                style: {},
            },
            elements: [],
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
                    <H1 style={{ margin: 0 }}>Group</H1>
                </div>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={docJson}
                            copyMessage="Copied Group JSON"
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
                                <Code>collapsible</Code>
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
                                    Whether this section&apos;s contents should
                                    be collapsible.
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <Code>defaultIsOpen</Code>
                            </td>
                            <td>
                                <strong>boolean</strong>
                                <em
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        "docs-prop-default"
                                    )}
                                >
                                    true
                                </em>
                                <div>
                                    defaultIsOpen attribute sets the default
                                    open state of the group.
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <Code>compact</Code>
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
                                    Whether this section should use compact
                                    styles.
                                </div>
                            </td>
                        </tr>
                        {docProps.style}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
