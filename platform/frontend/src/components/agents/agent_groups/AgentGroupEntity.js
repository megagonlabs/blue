import { ENTITY_TYPE_LOOKUP } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import GroupAgentSelector from "@/components/entity/GroupAgentSelector";
import { axiosErrorToast, settlePromises } from "@/components/helper";
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
import { faFolderTree } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useCallback, useContext, useEffect, useState } from "react";
export default function AgentGroupEntity() {
    const BLANK_ENTITY = { type: "agent_group" };
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const urlPrefix = `/registry/${appState.agent.registryName}/agent_group`;
    const [entity, setEntity] = useState(BLANK_ENTITY);
    const [editEntity, setEditEntity] = useState(BLANK_ENTITY);
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(false);
    const discard = () => {
        setEdit(false);
        setEditEntity(entity);
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
    const routerQueryPath =
        "/" + _.get(router, "query.pathParams", []).join("/");
    const fetchAgentGroup = useCallback(() => {
        setLoading(true);
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
    }, [routerQueryPath]);
    useEffect(() => {
        if (!router.isReady) return;
        fetchAgentGroup();
    }, [router, fetchAgentGroup]);
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
                        axiosErrorToast(error);
                        reject(false);
                    });
            }),
        ];
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
    };
    const [isGroupAgentSelectorDialogOpen, setIsGroupAgentSelectorDialogOpen] =
        useState(false);
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
            />
            <EntityDescription
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                loading={loading}
                updateEntity={updateEntity}
            />
            <Section
                compact
                icon={faIcon({ icon: ENTITY_TYPE_LOOKUP.agent.icon })}
                title={<H5 className="margin-0">Agents</H5>}
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
                            </tr>
                        </thead>
                        <tbody>
                            {_.values(entity.contents).map((element, index) => {
                                if (!_.isEqual(element.type, "agent")) {
                                    return null;
                                }
                                return (
                                    <tr key={index}>
                                        <td>
                                            <Link
                                                href={`${routerQueryPath}/agent/${element.name}`}
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
                                    </tr>
                                );
                            })}
                            {canEditEntity && !edit && (
                                <tr>
                                    <td>
                                        <Button
                                            className={
                                                loading
                                                    ? Classes.SKELETON
                                                    : null
                                            }
                                            icon={faIcon({
                                                icon: faFolderTree,
                                            })}
                                            outlined
                                            text="Update agents"
                                            onClick={() =>
                                                setIsGroupAgentSelectorDialogOpen(
                                                    true
                                                )
                                            }
                                        />
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </HTMLTable>
                </SectionCard>
            </Section>
            <GroupAgentSelector
                isOpen={isGroupAgentSelectorDialogOpen}
                setIsGroupAgentSelectorDialogOpen={
                    setIsGroupAgentSelectorDialogOpen
                }
                fetchAgentGroup={fetchAgentGroup}
                entity={entity}
            />
        </div>
    );
}
