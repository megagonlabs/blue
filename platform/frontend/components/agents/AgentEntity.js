import {
    HTMLTable,
    Intent,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import axios from "axios";
import { diff } from "deep-diff";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../app-context";
import EntityDescription from "../entity/EntityDescription";
import EntityMain from "../entity/EntityMain";
import EntityProperties from "../entity/EntityProperties";
import { constructSavePropertyRequests, settlePromises } from "../helper";
import { AppToaster } from "../toaster";
export default function AgentEntity() {
    const { appState } = useContext(AppContext);
    const router = useRouter();
    const [entity, setEntity] = useState({});
    const [editEntity, setEditEntity] = useState({});
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
    const [jsonError, setJsonError] = useState(false);
    useEffect(() => {
        if (!router.isReady) return;
        if (_.includes(router.asPath, "/default/new?entity=")) return;
        axios.get(router.asPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
            setEditEntity(_.get(response, "data.result", {}));
            setLoading(false);
        });
    }, [router]);
    const updateEntity = ({ path, value }) => {
        let newEntity = _.cloneDeep(editEntity);
        _.set(newEntity, path, value);
        setEditEntity(newEntity);
    };
    const saveEntity = () => {
        setLoading(true);
        let tasks = [
            new Promise((resolve, reject) => {
                axios
                    .put(
                        `/agents/${appState.agent.registryName}/agent/${entity.name}`,
                        {
                            name: entity.name,
                            description: editEntity.description,
                        }
                    )
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        AppToaster.show({
                            intent: Intent.DANGER,
                            message: `${error.name}: ${error.message}`,
                        });
                        reject(false);
                    });
            }),
        ];
        const difference = diff(entity.properties, editEntity.properties);
        tasks.concat(
            constructSavePropertyRequests({
                axios,
                difference,
                appState,
                entity,
                editEntity,
            })
        );
        settlePromises(tasks, (error) => {
            if (!error) {
                setEdit(false);
                setEntity(editEntity);
            }
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
                jsonError={jsonError}
            />
            <EntityDescription
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                updateEntity={updateEntity}
            />
            <EntityProperties
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
                setLoading={setLoading}
            />
            <Section
                compact
                collapsible
                title="Inputs"
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
                                if (!_.isEqual(element.type, "input")) {
                                    return null;
                                }
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
            <Section
                compact
                collapsible
                title="Outputs"
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
                                if (!_.isEqual(element.type, "output")) {
                                    return null;
                                }
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
