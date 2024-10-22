import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import {
    HTMLTable,
    Intent,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function CollectionEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({ type: "collection" });
    const [loading, setLoading] = useState(true);
    const routerQueryPath =
        "/" + _.get(router, "query.pathParams", []).join("/");
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(routerQueryPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
            setLoading(false);
        });
    }, [router]);
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain entity={entity} loading={loading} />
            <EntityDescription entity={entity} loading={loading} />
            <EntityProperties entity={entity} loading={loading} />
            <Section
                collapsible
                compact
                title="Entities"
                style={{ marginTop: 20 }}
            >
                <SectionCard padded={false}>
                    <HTMLTable
                        className="entity-section-card-table"
                        bordered
                        style={{ width: "100%" }}
                    >
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {_.values(entity.contents).map((element, index) => {
                                if (!_.isEqual(element.type, "entity")) {
                                    return null;
                                }
                                return (
                                    <tr key={index}>
                                        <td>
                                            <Link
                                                href={`${routerQueryPath}/entity/${element.name}`}
                                            >
                                                <Tag
                                                    style={{
                                                        pointerEvents: "none",
                                                    }}
                                                    minimal
                                                    interactive
                                                    large
                                                    intent={Intent.PRIMARY}
                                                >
                                                    {element.name}
                                                </Tag>
                                            </Link>
                                        </td>
                                        <td>{element.description}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
            <Section
                compact
                collapsible
                title="Relations"
                style={{ marginTop: 20 }}
            >
                <SectionCard padded={false}>
                    <HTMLTable
                        className="entity-section-card-table"
                        bordered
                        style={{ width: "100%" }}
                    >
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {_.values(entity.contents).map((element, index) => {
                                if (!_.isEqual(element.type, "relation")) {
                                    return null;
                                }
                                return (
                                    <tr key={index}>
                                        <td>
                                            <Link
                                                href={`${routerQueryPath}/relation/${element.name}`}
                                            >
                                                <Tag
                                                    style={{
                                                        pointerEvents: "none",
                                                    }}
                                                    minimal
                                                    interactive
                                                    large
                                                    intent={Intent.PRIMARY}
                                                >
                                                    {element.name}
                                                </Tag>
                                            </Link>
                                        </td>
                                        <td>{element.description}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
        </div>
    );
}
