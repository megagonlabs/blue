import { faIcon } from "@/components/icon";
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
    Intent,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import CopyDocJsonButton from "./CopyDocJsonButton";
export default function TabsDoc({ closePanel }) {
    const docJson = {
        type: "Tabs",
        props: { vertical: false, large: false },
        elements: [
            { type: "Group", elements: [] },
            { type: "Group", elements: [] },
        ],
    };
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
                    It is strongly recommended to use <Code>Group</Code> for
                    each tab&apos;s contents.
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
                <H2>Vertical vs. Horizontal</H2>
                <Card
                    style={{
                        padding: "5px 15px",
                        borderRadius: 0,
                        overflowX: "auto",
                        overscrollBehavior: "contain",
                    }}
                >
                    <ButtonGroup minimal>
                        <Button text="Tab 1" />
                        <Button text="Tab 2" />
                    </ButtonGroup>
                </Card>
            </div>
        </>
    );
}
