import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Callout,
    Card,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
    Size,
    Tag,
} from "@blueprintjs/core";
import classNames from "classnames";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJsonVertical = {
    type: "VerticalLayout",
    elements: [],
};
const docJSonHorizontal = {
    type: "HorizontalLayout",
    props: { spaceEvenly: true, style: {} },
    elements: [],
};
export default function LayoutDoc() {
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <H1 style={{ margin: 0 }}>Layout</H1>
            </div>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJsonVertical, null, 4)}
                        copyMessage="Copied Layout JSON"
                    />
                </div>
                <JSONViewer json={docJsonVertical} enableClipboard={false} />
            </Pre>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJSonHorizontal, null, 4)}
                        copyMessage="Copied Layout JSON"
                    />
                </div>
                <JSONViewer json={docJSonHorizontal} enableClipboard={false} />
            </Pre>
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
            <HTMLTable className="docs-prop-table" style={{ width: "100%" }}>
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
                                Whether to have elements with equal width.
                            </div>
                            <Tag
                                size={Size.LARGE}
                                intent={Intent.PRIMARY}
                                minimal
                                style={{ marginTop: 10 }}
                            >
                                Applies to <strong>HorizontalLayout</strong>
                                &nbsp;only
                            </Tag>
                        </td>
                    </tr>
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
