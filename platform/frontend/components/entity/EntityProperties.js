import { Classes, Section, SectionCard } from "@blueprintjs/core";
export default function EntityProperties({ entity }) {
    return (
        <Section collapsible title="Properties" style={{ marginTop: 20 }}>
            <SectionCard padded={false}>
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
            </SectionCard>
        </Section>
    );
}
