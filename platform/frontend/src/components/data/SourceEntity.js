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
import { useContext, useEffect, useState } from "react";
import { ENTITY_TYPE_LOOKUP } from "../constant";
import { AppContext } from "../contexts/app-context";
import {
    axiosErrorToast,
    constructSavePropertyRequests,
    settlePromises,
    shallowDiff,
} from "../helper";
export default function SourceEntity() {
    const BLANK_ENTITY = { type: "data" };
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const urlPrefix = `/registry/${appState.data.registryName}/data`;
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
                let tasks = constructSavePropertyRequests({
                    axios,
                    url: `${urlPrefix}/${entity.name}/property`,
                    difference: shallowDiff(
                        entity.properties,
                        editEntity.properties
                    ),
                    properties: editEntity.properties,
                });
                settlePromises(tasks, ({ error }) => {
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
            .catch((error) => axiosErrorToast(error));
    };
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
                loading={loading}
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                updateEntity={updateEntity}
            />
            <EntityProperties
                loading={loading}
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
            />
            <Section
                compact
                icon={faIcon({ icon: ENTITY_TYPE_LOOKUP.database.icon })}
                title={<H5 className="margin-0">Databases</H5>}
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
                                if (!_.isEqual(element.type, "database")) {
                                    return null;
                                }
                                return (
                                    <tr key={index}>
                                        <td>
                                            <Link
                                                href={`${routerQueryPath}/database/${element.name}`}
                                            >
                                                <Tag
                                                    style={{
                                                        pointerEvents: "none",
                                                    }}
                                                    minimal
                                                    interactive
                                                    size="large"
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
