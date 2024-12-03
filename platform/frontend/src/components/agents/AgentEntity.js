import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import {
    constructSavePropertyRequests,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Classes,
    HTMLTable,
    Intent,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import { faPlus } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { AuthContext } from "../contexts/auth-context";
export default function AgentEntity() {
    const BLANK_ENTITY = { type: "agent" };
    const router = useRouter();
    const { appActions } = useContext(AppContext);
    const [entity, setEntity] = useState(BLANK_ENTITY);
    const [editEntity, setEditEntity] = useState(BLANK_ENTITY);
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
    const [jsonError, setJsonError] = useState(false);
    const discard = () => {
        setEdit(false);
        setEditEntity(entity);
    };
    const routerQueryPath =
        "/" + _.get(router, "query.pathParams", []).join("/");
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(routerQueryPath).then((response) => {
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
        axios
            .put(`${urlPrefix}/${entity.name}`, {
                name: entity.name,
                description: editEntity.description,
                icon: icon,
            })
            .then(() => {
                const tasks = constructSavePropertyRequests({
                    axios,
                    url: `${urlPrefix}/${entity.name}/property`,
                    difference: shallowDiff(
                        entity.properties,
                        editEntity.properties
                    ),
                    properties: editEntity.properties,
                });
                settlePromises(tasks, (error) => {
                    if (!error) {
                        setEdit(false);
                        appActions.agent.setIcon({
                            key: entity.name,
                            value: _.get(editEntity, "icon", null),
                        });
                        setEntity(editEntity);
                    }
                    setLoading(false);
                });
            })
            .catch((error) => {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `${error.name}: ${error.message}`,
                });
            });
    };
    const addInputOutput = (type) => {
        if (!router.isReady) return;
        router.push(`${routerQueryPath}/${type}/new`);
    };
    const { user } = useContext(AuthContext);
    const canEditEntity = (() => {
        // write_own
        const created_by = _.get(entity, "created_by", null);
        if (_.isEqual(created_by, user.uid)) {
            return true;
        }
        // write_all
        const writePermissions = _.get(user, "permissions.agent_registry", []);
        if (_.includes(writePermissions, "write_all")) {
            return true;
        }
        return false;
    })();
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain
                enableIcon
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
                loading={loading}
                updateEntity={updateEntity}
            />
            <EntityProperties
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                jsonError={jsonError}
                loading={loading}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
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
                                                href={`${routerQueryPath}/input/${element.name}`}
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
                            {canEditEntity ? (
                                <tr>
                                    <td colSpan={2}>
                                        <Button
                                            className={
                                                loading
                                                    ? Classes.SKELETON
                                                    : null
                                            }
                                            icon={faIcon({ icon: faPlus })}
                                            outlined
                                            text="Add input"
                                            onClick={() => {
                                                addInputOutput("input");
                                            }}
                                        />
                                    </td>
                                </tr>
                            ) : null}
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
                                                href={`${routerQueryPath}/output/${element.name}`}
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
                            {canEditEntity ? (
                                <tr>
                                    <td colSpan={2}>
                                        <Button
                                            className={
                                                loading
                                                    ? Classes.SKELETON
                                                    : null
                                            }
                                            icon={faIcon({ icon: faPlus })}
                                            outlined
                                            text="Add output"
                                            onClick={() => {
                                                addInputOutput("output");
                                            }}
                                        />
                                    </td>
                                </tr>
                            ) : null}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
        </div>
    );
}
