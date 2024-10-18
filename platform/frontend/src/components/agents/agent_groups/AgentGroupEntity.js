import { AppContext } from "@/components/contexts/app-context";
import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import {
    constructSavePropertyRequests,
    settlePromises,
} from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import { diff } from "deep-diff";
import _ from "lodash";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
export default function AgentGroupEntity() {
    const BLANK_ENTITY = { type: "agent_group" };
    const router = useRouter();
    const { appActions } = useContext(AppContext);
    const [entity, setEntity] = useState(BLANK_ENTITY);
    const [editEntity, setEditEntity] = useState(BLANK_ENTITY);
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
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
        const urlPrefix = `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_group`;
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
                properties: editEntity.properties,
            })
        );
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
            />
            <EntityDescription
                edit={edit}
                setEdit={setEdit}
                entity={editEntity}
                updateEntity={updateEntity}
            />
        </div>
    );
}
