import { faIcon } from "@/components/icon";
import { Button, Classes, H1 } from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/pro-duotone-svg-icons";
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
            </div>
        </>
    );
}
