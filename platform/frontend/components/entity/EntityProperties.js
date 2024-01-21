import { Classes, Intent, Section, SectionCard, Tag } from "@blueprintjs/core";
import { useEffect, useState } from "react";
import Editor from "../Editor";
export default function EntityProperties({ entity, edit }) {
    const [properties, setProperties] = useState("");
    useEffect(() => {
        setProperties(JSON.stringify(entity.properties, null, 4));
    }, [entity]);
    const [error, setError] = useState(false);
    return (
        <Section
            collapsible
            title="Properties"
            style={{ marginTop: 20 }}
            rightElement={
                error ? (
                    <Tag large minimal intent={Intent.DANGER}>
                        Invalid JSON
                    </Tag>
                ) : null
            }
        >
            <SectionCard
                padded={false}
                style={{ height: edit ? 300 : null, overflowX: "auto" }}
            >
                {!edit ? (
                    <pre
                        className={Classes.TEXT_SMALL}
                        style={{
                            margin: 0,
                            padding: 20,
                            width: "100%",
                            overflowX: "auto",
                        }}
                    >
                        {JSON.stringify(entity.properties, null, 4)}
                    </pre>
                ) : (
                    <Editor
                        code={properties}
                        setCode={setProperties}
                        setError={setError}
                    />
                )}
            </SectionCard>
        </Section>
    );
}
