import { Classes, EditableText, Section, SectionCard } from "@blueprintjs/core";
export default function EntityDescription({
    entity,
    edit,
    updateEntity,
    setEdit,
    loading = false,
}) {
    return (
        <Section compact title="Description" style={{ marginTop: 20 }}>
            <SectionCard
                style={{ whiteSpace: !edit ? "pre-wrap" : null }}
                onDoubleClick={(event) => {
                    setEdit(true);
                    event.stopPropagation();
                }}
            >
                {loading ? (
                    <div className={Classes.SKELETON}>&nbsp;</div>
                ) : edit ? (
                    <EditableText
                        alwaysRenderInput
                        multiline
                        minLines={2}
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
