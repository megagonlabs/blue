import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import {
    constructSavePropertyRequests,
    settlePromises,
} from "@/components/helper";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    HTMLTable,
    Intent,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import { faPlus } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import { diff } from "deep-diff";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function AgentEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({});
    const [editEntity, setEditEntity] = useState({});
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
    const [jsonError, setJsonError] = useState(false);
    const discard = () => {
        setEdit(false);
        setEditEntity(entity);
    };
    useEffect(() => {
        if (!router.isReady) {
            return;
        }
        axios.get(router.asPath).then((response) => {
            const result = _.get(response, "data.result", {});
            let icon = _.get(result, "icon", null);
            if (!_.isEmpty(icon) && !_.startsWith(icon, "data:image/")) {
                icon = _.split(icon, ":");
            }
            _.set(result, "icon", icon);
            setEntity(result);
            setEditEntity(result);
            setLoading(false);
        });
    }, [router]);
    const updateEntity = ({ path, value }) => {
        let newEntity = _.cloneDeep(editEntity);
        _.set(newEntity, path, value);
        setEditEntity(newEntity);
    };
    const saveEntity = () => {
        const urlPrefix = `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent`;
        setLoading(true);
        let icon = _.get(editEntity, "icon", null);
        if (!_.isEmpty(icon) && !_.startsWith(icon, "data:image/")) {
            icon = _.join(icon, ":");
        }
        let tasks = [
            new Promise((resolve, reject) => {
                axios
                    .put(`${urlPrefix}/${entity.name}`, {
                        name: entity.name,
                        description: editEntity.description,
                        icon: icon,
                    })
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
                url: `${urlPrefix}/${entity.name}/property`,
                difference,
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
    const addInputOutput = (type) => {
        if (!router.isReady) {
            return;
        }
        let params = _.cloneDeep(_.get(router, "query.pathParams", []));
        router.push(`/${params.join("/")}/${type}/new`);
    };
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain
                enableIcon={true}
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                updateEntity={updateEntity}
                saveEntity={saveEntity}
                discard={discard}
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
                                    <tr key={index}>
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
                            <tr>
                                <td colSpan={2}>
                                    <Button
                                        icon={faIcon({ icon: faPlus })}
                                        outlined
                                        text="Add input"
                                        onClick={() => {
                                            addInputOutput("input");
                                        }}
                                    />
                                </td>
                            </tr>
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
                                    <tr key={index}>
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
                            <tr>
                                <td colSpan={2}>
                                    <Button
                                        icon={faIcon({ icon: faPlus })}
                                        outlined
                                        text="Add output"
                                        onClick={() => {
                                            addInputOutput("output");
                                        }}
                                    />
                                </td>
                            </tr>
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
        </div>
    );
}
