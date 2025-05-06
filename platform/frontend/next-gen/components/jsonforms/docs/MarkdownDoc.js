import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import { H1, H2, HTMLTable, Pre, Size, Tag } from "@blueprintjs/core";
import CopyDocJSONButton from "./CopyDocJSONButton";
const uiSchemaJson = {
    type: "Markdown",
    scope: "#/properties/markdown",
    props: {
        style: {},
    },
};
const dataJson = {
    markdown: "markdown content",
};
export default function MarkdownDoc() {
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <H1 style={{ margin: 0 }}>Markdown</H1>
            </div>
            <H2>Example</H2>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(uiSchemaJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        UI Schema
                    </Tag>
                </div>
                <JSONViewer json={uiSchemaJson} enableClipboard={false} />
            </Pre>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(dataJson, null, 4)}
                    />
                </div>
                <div>
                    <Tag size={Size.LARGE} style={{ marginBottom: 10 }} minimal>
                        Data
                    </Tag>
                </div>
                <JSONViewer json={dataJson} enableClipboard={false} />
            </Pre>
            <H2>Props</H2>
            <HTMLTable className="docs-prop-table" style={{ width: "100%" }}>
                <thead>
                    <tr>
                        <th>Props</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>{docProps.style}</tbody>
            </HTMLTable>
        </div>
    );
}
