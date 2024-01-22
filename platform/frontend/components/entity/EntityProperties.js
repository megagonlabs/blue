import { Classes, Intent, Section, SectionCard, Tag } from "@blueprintjs/core";
import Editor from "../Editor";
export default function EntityProperties({
    entity,
    edit,
    jsonError,
    setJsonError,
    updateEntity,
    setLoading,
}) {
    const setProperties = (value) => {
        updateEntity({ path: "properties", value: JSON.parse(value) });
    };
    return (
        <Section
            collapsible={!edit}
            title="Properties"
            style={{ marginTop: 20 }}
            rightElement={
                jsonError && edit ? (
                    <Tag large minimal intent={Intent.DANGER}>
                        Invalid JSON
                    </Tag>
                ) : null
            }
        >
            <SectionCard padded={false}>
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
                        code={JSON.stringify(entity.properties, null, 4)}
                        setCode={setProperties}
                        setLoading={setLoading}
                        setError={setJsonError}
                    />
                )}
            </SectionCard>
        </Section>
    );
}
