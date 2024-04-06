import { faIcon } from "@/components/icon";
import {
    Button,
    Callout,
    Card,
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
export default function LayoutDoc({ closePanel }) {
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
                    <H1 style={{ margin: 0 }}>Layout</H1>
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
                            type: "VerticalLayout",
                            elements: [],
                        },
                        null,
                        4
                    )}
                </pre>
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
                            type: "HorizontalLayout",
                            props: {
                                spaceEvenly: true,
                            },
                            elements: [],
                        },
                        null,
                        4
                    )}
                </pre>
                <H2>Vertical vs. Horizontal</H2>
                <Callout
                    style={{
                        display: "flex",
                        rowGap: 15,
                        flexDirection: "column",
                    }}
                >
                    <Card compact>1</Card>
                    <Card compact>2</Card>
                </Callout>
                <Callout
                    style={{
                        display: "flex",
                        columnGap: 15,
                        flexDirection: "row",
                    }}
                >
                    <Card compact style={{ flex: 1 }}>
                        1
                    </Card>
                    <Card compact style={{ flex: 1 }}>
                        2
                    </Card>
                </Callout>
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
                                <Code>spaceEvenly</Code>
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
                                    Whether to have elementsw with equal width
                                </div>
                                <Tag
                                    intent={Intent.PRIMARY}
                                    minimal
                                    style={{ marginTop: 5 }}
                                >
                                    Applies to&nbsp;
                                    <strong>HorizontalLayout</strong>&nbsp;only
                                </Tag>
                            </td>
                        </tr>
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
