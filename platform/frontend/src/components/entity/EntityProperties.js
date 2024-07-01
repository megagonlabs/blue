import EditorJSON from "@/components/codemirror/EditorJSON";
import { Classes, Intent, Section, SectionCard, Tag } from "@blueprintjs/core";
import _ from "lodash";
export default function EntityProperties({
    entity,
    edit,
    setEdit,
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
            compact
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
            <SectionCard
                padded={false}
                onDoubleClick={(event) => {
                    if (_.isFunction(setEdit)) {
                        setEdit(true);
                    }
                    event.stopPropagation();
                }}
            >
                {!edit ? (
                    <pre
                        className={Classes.TEXT_SMALL}
                        style={{
                            margin: 0,
                            padding: 15,
                            width: "100%",
                            overflowX: "auto",
                        }}
                    >
                        {JSON.stringify(entity.properties, null, 4)}
                    </pre>
                ) : (
                    <EditorJSON
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
