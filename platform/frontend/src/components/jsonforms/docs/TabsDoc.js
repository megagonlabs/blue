import { faIcon } from "@/components/icon";
import * as docProps from "@/components/jsonforms/docs/constant";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
    ButtonGroup,
    Callout,
    Card,
    Classes,
    Code,
    H1,
    H2,
    HTMLTable,
    Intent,
    Section,
    SectionCard,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useState } from "react";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function TabsDoc({ closePanel }) {
    const docJson = {
        type: "Tabs",
        tabs: [],
        props: {
            vertical: false,
            large: false,
            compact: false,
            style: {},
        },
        elements: [],
    };
    const exampleJson = {
        type: "Tabs",
        tabs: ["Tab 1", "Tab 2"],
        elements: [
            {
                type: "Group",
                elements: [
                    {
                        type: "Label",
                        label: "Tab 1 content",
                    },
                ],
            },
            {
                type: "Group",
                elements: [
                    {
                        type: "Label",
                        label: "Tab 2 content",
                    },
                ],
            },
        ],
    };
    const [tab, setTab] = useState("tab1");
    return (
        <>
            <div className="border-bottom" style={{ padding: "10px 20px" }}>
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
                    <H1 style={{ margin: 0 }}>Tabs</H1>
                </div>
                <Callout intent={Intent.SUCCESS} icon={null}>
                    For clearer visual separation, it is recommended to use{" "}
                    <Code>Group</Code> &#40;without label&#41; for each
                    tab&apos;s contents.
                </Callout>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(docJson, null, 4)}
                            copyMessage="Copied Tab JSON"
                        />
                    </div>
                    <JsonViewer json={docJson} enableClipboard={false} />
                </pre>
                <H2>Example</H2>
                <pre style={{ position: "relative", overflow: "hidden" }}>
                    <div style={{ position: "absolute", right: 15, top: 13 }}>
                        <CopyDocJsonButton
                            docJson={JSON.stringify(exampleJson, null, 4)}
                        />
                    </div>
                    <JsonViewer json={exampleJson} enableClipboard={false} />
                </pre>
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
                        <ButtonGroup minimal>
                            <Button
                                active={_.isEqual(tab, "tab1")}
                                text="Tab 1"
                                onClick={() => setTab("tab1")}
                            />
                            <Button
                                active={_.isEqual(tab, "tab2")}
                                text="Tab 2"
                                onClick={() => setTab("tab2")}
                            />
                        </ButtonGroup>
                    </Card>
                    <Section>
                        <SectionCard>
                            Tab {_.isEqual(tab, "tab1") ? 1 : 2} content
                        </SectionCard>
                    </Section>
                </Callout>
                <Callout
                    style={{
                        display: "flex",
                        gap: 15,
                        alignItems: "flex-start",
                    }}
                >
                    <Card style={{ padding: 5 }}>
                        <ButtonGroup vertical minimal>
                            <Button
                                ellipsizeText
                                active={_.isEqual(tab, "tab1")}
                                text="Tab 1"
                                onClick={() => setTab("tab1")}
                            />
                            <Button
                                ellipsizeText
                                active={_.isEqual(tab, "tab2")}
                                text="Tab 2"
                                onClick={() => setTab("tab2")}
                            />
                        </ButtonGroup>
                    </Card>
                    <Section>
                        <SectionCard>
                            Tab {_.isEqual(tab, "tab1") ? 1 : 2} content
                        </SectionCard>
                    </Section>
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
        </>
    );
}
