import {
    Classes,
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
export default function DatabaseEntity() {
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
            <Section compact title="Collections" style={{ marginTop: 20 }}>
                <SectionCard padded={false}>
                    <HTMLTable bordered style={{ width: "100%" }}>
                        <thead>
                            <tr>
                                <th
                                    style={{
                                        paddingLeft: 15,
                                        paddingRight: 15,
                                    }}
                                >
                                    Name
                                </th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {_.values(entity.contents).map((element) => {
                                if (!_.isEqual(element.type, "collection"))
                                    return null;
                                return (
                                    <tr>
                                        <td
                                            style={{
                                                paddingLeft: 15,
                                                paddingRight: 15,
                                            }}
                                        >
                                            <Link
                                                href={`${router.asPath}/collection/${element.name}`}
                                            >
                                                <Tag
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
