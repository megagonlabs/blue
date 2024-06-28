import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
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
import { useEffect, useState } from "react";
export default function OutputEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({});
    const [scope, setScope] = useState(null);
    const [editEntity, setEditEntity] = useState({});
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(true);
    const [jsonError, setJsonError] = useState(false);
    useEffect(() => {
        if (!router.isReady) {
            return;
        }
        axios.get(router.asPath).then((response) => {
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
        setLoading(true);
        const parent = _.last(_.split(scope, "/"));
        const urlPrefix = `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agents/${parent}/output`;
        let tasks = [
            new Promise((resolve, reject) => {
                axios
                    .put(`${urlPrefix}/${entity.name}`, {
                        name: entity.name,
                        description: editEntity.description,
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
                entity={entity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
                setLoading={setLoading}
            />
        </div>
    );
}
