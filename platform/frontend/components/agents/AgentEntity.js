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
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../app-context";
import EntityDescription from "../entity/EntityDescription";
import EntityMain from "../entity/EntityMain";
import EntityProperties from "../entity/EntityProperties";
export default function AgentEntity() {
    const { appState } = useContext(AppContext);
    const router = useRouter();
    const [entity, setEntity] = useState({});
    const [editEntity, setEditEntity] = useState({});
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(router.asPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
            setEditEntity(_.get(response, "data.result", {}));
            setLoading(false);
        });
    }, [router]);
    const updateEntity = ({ path, value }) => {
        let currentEntity = _.cloneDeep(editEntity);
        _.set(currentEntity, path, value);
        setEditEntity(currentEntity);
    };
    const saveEntity = () => {
        setEdit(false);
        setLoading(true);
        axios
            .put(
                `/agents/${appState.agent.registryName}/agent/${entity.name}`,
                {
                    name: entity.name,
                    description: editEntity.description,
                }
            )
            .then((response) => {
                setLoading(false);
            })
            .catch((error) => {
                setLoading(false);
            });
    };
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain
                edit={edit}
                setEdit={setEdit}
                entity={entity}
                saveEntity={saveEntity}
                loading={loading}
                error={error}
            />
            <EntityDescription
                edit={edit}
                entity={editEntity}
                updateEntity={updateEntity}
            />
            <EntityProperties
                edit={edit}
                entity={editEntity}
                error={error}
                setError={setError}
            />
            <Section title="Inputs" style={{ marginTop: 20 }}>
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
                                if (!_.isEqual(element.type, "input"))
                                    return null;
                                return (
                                    <tr
                                        key={`agent-entity-table-input-${index}`}
                                    >
                                        <td>
                                            <Link
                                                href={`${router.asPath}/input/${element.name}`}
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
            <Section title="Outputs" style={{ marginTop: 20 }}>
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
                                if (!_.isEqual(element.type, "output"))
                                    return null;
                                return (
                                    <tr
                                        key={`agent-entity-table-output-${index}`}
                                    >
                                        <td>
                                            <Link
                                                href={`${router.asPath}/output/${element.name}`}
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
