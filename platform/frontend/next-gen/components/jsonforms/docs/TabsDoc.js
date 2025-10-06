import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Callout,
    Card,
    Classes,
    Code,
    EntityTitle,
    H1,
    H2,
    HTMLTable,
    Intent,
    Pre,
} from "@blueprintjs/core";
import { faPause } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useState } from "react";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
    type: "Tabs",
    scope: "#/properties/...",
    tabs: [],
    props: { vertical: false, large: false, compact: false, style: {} },
    elements: [],
};
const exampleJson = {
    type: "Tabs",
    scope: "...",
    tabs: ["Tab 1", "Tab 2"],
    elements: [
        {
            type: "Group",
            elements: [{ type: "Label", label: "Tab 1 content" }],
        },
        {
            type: "Group",
            elements: [{ type: "Label", label: "Tab 2 content" }],
        },
    ],
};
export default function TabsDoc() {
    const [tab, setTab] = useState("tab1");
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <EntityTitle
                    title="Tabs"
                    heading={H1}
                    icon={
                        <FAIcon
                            className="fa-rotate-90"
                            icon={faPause}
                            size={30}
                        />
                    }
                />
            </div>
            <Callout intent={Intent.SUCCESS} icon={null}>
                For better visual separation, it is recommended to use&nbsp;
                <Code>Group</Code> &#40;without label&#41; for each tab&apos;s
                contents.
            </Callout>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Tab JSON"
                    />
                </div>
                <JSONViewer json={docJson} enableClipboard={false} />
            </Pre>
            <H2>Example</H2>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(exampleJson, null, 4)}
                    />
                </div>
                <JSONViewer json={exampleJson} enableClipboard={false} />
            </Pre>
            <H2>Horizontal vs. Vertical</H2>
            <Callout>
                <Card
                    style={{
                        padding: "5px 20px",
                        overflowX: "auto",
                        marginBottom: 15,
                        overscrollBehavior: "contain",
                    }}
                >
                    <ButtonGroup variant={ButtonVariant.MINIMAL}>
                        <Button
                            active={_.isEqual(tab, "tab1")}
                            text="Tab 1"
                            onClick={() => {
                                setTab("tab1");
                            }}
                        />
                        <Button
                            active={_.isEqual(tab, "tab2")}
                            text="Tab 2"
                            onClick={() => {
                                setTab("tab2");
                            }}
                        />
                    </ButtonGroup>
                </Card>
                <div
                    className="full-parent-width custom-card"
                    style={{ padding: 20 }}
                >
                    Tab {_.isEqual(tab, "tab1") ? 1 : 2} content
                </div>
            </Callout>
            <Callout
                style={{
                    display: "flex",
                    gap: 15,
                    alignItems: "flex-start",
                }}
            >
                <Card style={{ padding: 5 }}>
                    <ButtonGroup vertical variant={ButtonVariant.MINIMAL}>
                        <Button
                            ellipsizeText
                            active={_.isEqual(tab, "tab1")}
                            text="Tab 1"
                            onClick={() => {
                                setTab("tab1");
                            }}
                        />
                        <Button
                            ellipsizeText
                            active={_.isEqual(tab, "tab2")}
                            text="Tab 2"
                            onClick={() => {
                                setTab("tab2");
                            }}
                        />
                    </ButtonGroup>
                </Card>
                <div
                    className="full-parent-width custom-card"
                    style={{ padding: 20 }}
                >
                    Tab {_.isEqual(tab, "tab1") ? 1 : 2} content
                </div>
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
                            <Code>tabs</Code>
                        </td>
                        <td>
                            <strong>array</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                &#91;at least 1 element&#93;
                            </em>
                            <div>Consists of tabs labels.</div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>vertical</Code>
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
                                Whether tabs bar should align tabs button
                                vertically or horizontally.
                            </div>
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
                            <div>
                                Whether tabs button should use large styles.
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
                                Whether tabs bar should use compact styles.
                            </div>
                        </td>
                    </tr>
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}
