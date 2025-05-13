import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Callout,
    Classes,
    Code,
    EntityTitle,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
} from "@blueprintjs/core";
import { faQuoteLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
    type: "Callout",
    label: "",
    props: {
        intent: null,
        helperText: null,
        style: {},
    },
};
export default function CalloutDoc() {
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <EntityTitle
                    title="Callout"
                    heading={H1}
                    icon={<FAIcon icon={faQuoteLeft} size={30} />}
                />
            </div>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Button JSON"
                    />
                </div>
                <JSONViewer json={docJson} enableClipboard={false} />
            </Pre>
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
                            <div>Visual intent color to apply to element.</div>
                            <Callout icon={null} intent={Intent.DANGER}>
                                danger, helper text
                            </Callout>
                            <Callout icon={null} intent={Intent.WARNING}>
                                warning, helper text
                            </Callout>
                            <Callout icon={null} intent={Intent.PRIMARY}>
                                primary, helper text
                            </Callout>
                            <Callout icon={null} intent={Intent.SUCCESS}>
                                success, helper text
                            </Callout>
                        </td>
                    </tr>
                    {docProps.helperText}
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
