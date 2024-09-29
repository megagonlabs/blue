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
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
export default function MarkdownDoc({ closePanel }) {
    const docJson = {};
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
                    <H1 style={{ margin: 0 }}>Markdown</H1>
                </div>
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
                                <div style={{ width: 81 }}>
                                    <Code>md-content</Code>
                                </div>
                            </td>
                            <td>
                                <strong>string</strong>
                                <em
                                    className={classNames(
                                        Classes.TEXT_MUTED,
                                        "docs-prop-default"
                                    )}
                                >
                                    &quot;&quot;
                                </em>
                                <div>Markup language content</div>
                                <Tag
                                    large
                                    intent={Intent.WARNING}
                                    minimal
                                    style={{ marginTop: 5 }}
                                >
                                    <strong>md-content</strong> must be
                                    specified under data schema
                                </Tag>
                            </td>
                        </tr>
                        {docProps.style}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
