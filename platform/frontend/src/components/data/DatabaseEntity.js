import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import { faIcon } from "@/components/icon";
import {
    H5,
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
import { ENTITY_TYPE_LOOKUP } from "../constant";
export default function DatabaseEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({ type: "database" });
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
                compact
                icon={faIcon({ icon: ENTITY_TYPE_LOOKUP.collection.icon })}
                title={<H5 className="margin-0">Collections</H5>}
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
                                if (!_.isEqual(element.type, "collection")) {
                                    return null;
                                }
                                return (
                                    <tr key={index}>
                                        <td>
                                            <Link
                                                href={`${routerQueryPath}/collection/${element.name}`}
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
