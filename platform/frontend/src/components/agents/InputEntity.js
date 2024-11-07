import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import {
    constructSavePropertyRequests,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function InputEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({});
    const [scope, setScope] = useState(null);
    const [editEntity, setEditEntity] = useState({});
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
    const [jsonError, setJsonError] = useState(false);
    const routerQueryPath =
        "/" + _.get(router, "query.pathParams", []).join("/");
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(routerQueryPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
            setScope(_.get(response, "data.result.scope", null));
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
        const parent = _.last(_.split(scope, "/"));
        const urlPrefix = `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${parent}/input`;
        setLoading(true);
        axios
            .put(`${urlPrefix}/${entity.name}`, {
                name: entity.name,
                description: editEntity.description,
            })
            .then(() => {
                let tasks = constructSavePropertyRequests({
                    axios,
                    url: `${urlPrefix}/${entity.name}/property`,
                    difference: shallowDiff(
                        entity.properties,
                        editEntity.properties
                    ),
                    entity,
                    properties: editEntity.properties,
                });
                settlePromises(tasks, (error) => {
                    if (!error) {
                        setEdit(false);
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
                entity={entity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
            />
        </div>
    );
}
