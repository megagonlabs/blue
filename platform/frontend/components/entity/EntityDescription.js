import { EditableText, Section, SectionCard } from "@blueprintjs/core";
export default function EntityDescription({ entity, edit, updateEntity }) {
    return (
        <Section
            compact
            collapsible={!edit}
            title="Description"
            style={{ marginTop: 20 }}
        >
            <SectionCard style={{ whiteSpace: !edit ? "pre-wrap" : null }}>
                {edit ? (
                    <EditableText
                        multiline
                        onChange={(value) => {
                            updateEntity({ path: "description", value });
                        }}
                        value={entity.description}
                    />
                ) : (
                    entity.description
                )}
            </SectionCard>
        </Section>
    );
}
