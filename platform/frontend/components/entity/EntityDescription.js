import { Section, SectionCard } from "@blueprintjs/core";
export default function EntityDescription({ entity }) {
    return (
        <Section collapsible title="Description" style={{ marginTop: 20 }}>
            <SectionCard>{entity.description}</SectionCard>
        </Section>
    );
}
