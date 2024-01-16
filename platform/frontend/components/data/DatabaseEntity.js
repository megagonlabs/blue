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
import EntityDescription from "../entity/EntityDescription";
import EntityMain from "../entity/EntityMain";
import EntityProperties from "../entity/EntityProperties";
export default function DatabaseEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({});
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(router.asPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
        });
    }, [router]);
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain entity={entity} />
            <EntityDescription entity={entity} />
            <EntityProperties entity={entity} />
            <Section compact title="Collections" style={{ marginTop: 20 }}>
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
                                if (!_.isEqual(element.type, "collection"))
                                    return null;
                                return (
                                    <tr
                                        key={`data-entity-table-collection-${index}`}
                                    >
                                        <td>
                                            <Link
                                                href={`${router.asPath}/collection/${element.name}`}
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
