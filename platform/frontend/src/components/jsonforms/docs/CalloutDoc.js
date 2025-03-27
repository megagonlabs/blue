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
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function CalloutDoc({ closePanel }) {
    const docJson = {
        type: "Callout",
        label: "",
        props: {
            intent: null,
            helperText: null,
            style: {},
        },
    };
    const SAMPLE_CALLOUT_STYLES = {
        icon: null,
    };
    return (
        <>
            <div className="border-bottom" style={{ padding: "10px 20px" }}>
                <Button
                    variant="outlined"
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
                <div style={{ marginBottom: 20 }}>
                    <H1 style={{ margin: 0 }}>Callout</H1>
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
                                    {...SAMPLE_CALLOUT_STYLES}
                                    intent={Intent.DANGER}
                                >
                                    danger, helper text
                                </Callout>
                                <Callout
                                    {...SAMPLE_CALLOUT_STYLES}
                                    intent={Intent.WARNING}
                                >
                                    warning, helper text
                                </Callout>
                                <Callout
                                    {...SAMPLE_CALLOUT_STYLES}
                                    intent={Intent.PRIMARY}
                                >
                                    primary, helper text
                                </Callout>
                                <Callout
                                    {...SAMPLE_CALLOUT_STYLES}
                                    intent={Intent.SUCCESS}
                                >
                                    success, helper text
                                </Callout>
                            </td>
                        </tr>
                        {docProps.helperText}
                        {docProps.style}
                    </tbody>
                </HTMLTable>
            </div>
        </>
    );
}
