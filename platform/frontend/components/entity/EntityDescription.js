import { EditableText, Section, SectionCard } from "@blueprintjs/core";
import { useEffect, useState } from "react";
export default function EntityDescription({ entity, edit }) {
    const [description, setDescription] = useState("");
    useEffect(() => {
        setDescription(entity.description);
    }, [entity]);
    return (
        <Section collapsible title="Description" style={{ marginTop: 20 }}>
            <SectionCard>
                {edit ? (
                    <EditableText
                        multiline
                        onChange={(value) => {
                            setDescription(value);
                        }}
                        value={description}
                    />
                ) : (
                    entity.description
                )}
            </SectionCard>
        </Section>
    );
}
