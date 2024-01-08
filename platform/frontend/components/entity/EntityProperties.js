import { Classes, Section, SectionCard } from "@blueprintjs/core";
export default function EntityProperties({ entity }) {
    return (
        <Section collapsible title="Properties" style={{ marginTop: 20 }}>
            <SectionCard>
                <pre className={Classes.TEXT_SMALL} style={{ margin: 0 }}>
                    {JSON.stringify(entity.properties, null, 4)}
                </pre>
            </SectionCard>
        </Section>
    );
}
