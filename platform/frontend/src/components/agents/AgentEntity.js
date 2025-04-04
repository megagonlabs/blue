import { AuthContext } from "@/components/contexts/auth-context";
import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import {
    axiosErrorToast,
    constructSavePropertyRequests,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { faIcon } from "@/components/icon";
import {
    Button,
    Classes,
    H5,
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
import { ENTITY_TYPE_LOOKUP, GENERAL_KEYS } from "../constant";
import { AppContext } from "../contexts/app-context";
import EntityGeneral from "./EntityGeneral";
export default function AgentEntity() {
    const BLANK_ENTITY = { type: "agent" };
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const urlPrefix = `/registry/${appState.agent.registryName}/agent`;
    const [entity, setEntity] = useState(BLANK_ENTITY);
    const [editEntity, setEditEntity] = useState(BLANK_ENTITY);
    const [edit, setEdit] = useState(false);
    const [general, setGeneral] = useState({});
    const [loading, setLoading] = useState(true);
    const [jsonError, setJsonError] = useState(false);
    const discard = () => {
        setEdit(false);
        setEditEntity(entity);
        setGeneral(getGeneralProperties(entity.properties));
    };
    const routerQueryPath =
        "/" + _.get(router, "query.pathParams", []).join("/");
    const getGeneralProperties = (properties) => {
        let tempGeneral = {};
        for (let i = 0; i < _.size(GENERAL_KEYS); i++) {
            const key = GENERAL_KEYS[i];
            if (_.has(properties, key)) {
                if (_.isEqual(key, "listens")) {
                    _.set(
                        tempGeneral,
                        key,
                        _.entries(properties[key]).map((entry) => ({
                            key: entry[0],
                            includes: _.get(entry, "1.includes", []),
                            excludes: _.get(entry, "1.excludes", []),
                        }))
                    );
                } else if (_.isEqual(key, "tags")) {
                    _.set(
                        tempGeneral,
                        key,
                        _.entries(properties[key]).map((entry) => ({
                            key: entry[0],
                            tags: _.get(entry, "1", []),
                        }))
                    );
                } else {
                    _.set(tempGeneral, key, properties[key]);
                }
            }
        }
        return tempGeneral;
    };
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
            setGeneral(getGeneralProperties(result.properties));
        });
    }, [router, routerQueryPath]);
    const updateEntity = ({ path, value }) => {
        let newEntity = _.cloneDeep(editEntity);
        _.set(newEntity, path, value);
        setEditEntity(newEntity);
    };
    const saveEntity = () => {
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
                let updatedGeneral = { ...general };
                if (_.has(general, "listens")) {
                    let result = {};
                    for (let i = 0; i < _.size(general.listens); i++) {
                        _.set(result, general.listens[i].key, {
                            includes: _.get(
                                general.listens,
                                [i, "includes"],
                                []
                            ),
                            excludes: _.get(
                                general.listens,
                                [i, "excludes"],
                                []
                            ),
                        });
                    }
                    _.set(updatedGeneral, "listens", result);
                }
                if (_.has(general, "tags")) {
                    let result = {};
                    for (let i = 0; i < _.size(general.tags); i++) {
                        _.set(
                            result,
                            general.tags[i].key,
                            _.get(general.tags, [i, "tags"], [])
                        );
                    }
                    _.set(updatedGeneral, "tags", result);
                }
                const changes = {
                    ...editEntity.properties,
                    ...updatedGeneral,
                };
                const tasks = constructSavePropertyRequests({
                    axios,
                    url: `${urlPrefix}/${entity.name}/property`,
                    difference: shallowDiff(entity.properties, changes),
                    properties: changes,
                });
                settlePromises(tasks, ({ error }) => {
                    if (!error) {
                        setEdit(false);
                        appActions.agent.setIcon({
                            key: entity.name,
                            value: _.get(editEntity, "icon", null),
                        });
                        const newEntity = {
                            ...editEntity,
                            properties: changes,
                        };
                        setEntity(newEntity);
                        setEditEntity(newEntity);
                    }
                    setLoading(false);
                });
            })
            .catch((error) => axiosErrorToast(error));
    };
    const addEntityRouterPush = (type) => {
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
            <EntityGeneral
                edit={edit}
                setEdit={setEdit}
                loading={loading}
                general={general}
                setGeneral={setGeneral}
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
                icon={faIcon({ icon: ENTITY_TYPE_LOOKUP.input.icon })}
                title={<H5 className="margin-0">Inputs</H5>}
                style={{ marginTop: 20 }}
            >
                <SectionCard padded={false}>
                    <HTMLTable
                        className="entity-section-card-table full-parent-width"
                        bordered
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
                            {canEditEntity && !edit && (
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
                                                addEntityRouterPush("input");
                                            }}
                                        />
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
            <Section
                compact
                icon={faIcon({ icon: ENTITY_TYPE_LOOKUP.output.icon })}
                title={<H5 className="margin-0">Outputs</H5>}
                style={{ marginTop: 20 }}
            >
                <SectionCard padded={false}>
                    <HTMLTable
                        className="entity-section-card-table full-parent-width"
                        bordered
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
                            {canEditEntity && !edit && (
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
                                                addEntityRouterPush("output");
                                            }}
                                        />
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
            <Section
                compact
                icon={faIcon({ icon: ENTITY_TYPE_LOOKUP.agent.icon })}
                title={<H5 className="margin-0">Derived Agents</H5>}
                style={{ marginTop: 20 }}
            >
                <SectionCard padded={false}>
                    <HTMLTable
                        className="entity-section-card-table full-parent-width"
                        bordered
                    >
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {_.values(entity.contents).map((element, index) => {
                                if (!_.isEqual(element.type, "agent"))
                                    return null;
                                return (
                                    <tr key={index}>
                                        <td>
                                            <Link
                                                href={`${routerQueryPath}/agent/${element.name}`}
                                                onClick={() => setEdit(false)}
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
                            {canEditEntity && !edit && (
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
                                            text="Add agent"
                                            onClick={() => {
                                                addEntityRouterPush("agent");
                                            }}
                                        />
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
        </div>
    );
}
