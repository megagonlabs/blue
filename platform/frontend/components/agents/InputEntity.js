import { Classes, Section, SectionCard } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function InputEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({});
    useEffect(() => {
        axios.get(router.asPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
        });
    }, [router]);
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <Section compact>
                <SectionCard>
                    <div style={{ display: "flex" }}>
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ width: 52.7 }}
                        >
                            Name
                        </div>
                        {entity.name}
                    </div>
                    <div style={{ display: "flex" }}>
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ width: 52.7 }}
                        >
                            Type
                        </div>
                        {entity.type}
                    </div>
                </SectionCard>
            </Section>
            <Section
                compact
                collapsible
                title="Description"
                style={{ marginTop: 20 }}
            >
                <SectionCard>{entity.description}</SectionCard>
            </Section>
            <Section
                compact
                collapsible
                title="Properties"
                style={{ marginTop: 20 }}
            >
                <SectionCard>
                    <pre className={Classes.TEXT_SMALL} style={{ margin: 0 }}>
                        {JSON.stringify(entity.properties, null, 4)}
                    </pre>
                </SectionCard>
            </Section>
        </div>
    );
}
