import {
    Classes,
    HTMLTable,
    Intent,
    ProgressBar,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import { faPenSwirl } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import { diff } from "deep-diff";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../app-context";
import EntityDescription from "../entity/EntityDescription";
import EntityMain from "../entity/EntityMain";
import EntityProperties from "../entity/EntityProperties";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
const renderProgress = (progress, requestError = false, callback = null) => {
    if (progress >= 100 && _.isFunction(callback)) {
        callback();
    }
    return {
        icon: faIcon({ icon: faPenSwirl }),
        message: (
            <ProgressBar
                className={classNames("margin-top-5", {
                    [Classes.PROGRESS_NO_STRIPES]: progress >= 100,
                })}
                intent={
                    requestError
                        ? Intent.DANGER
                        : progress < 100
                        ? Intent.PRIMARY
                        : Intent.SUCCESS
                }
                value={progress / 100}
            />
        ),
        timeout: progress < 100 ? 0 : 2000,
    };
};
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
        setLoading(true);
        const difference = diff(entity.properties, editEntity.properties);
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
                    .then((response) => {
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
        if (_.isArray(difference)) {
            for (var i = 0; i < difference.length; i++) {
                const kind = difference[i].kind,
                    path = difference[i].path[0];
                if (_.isEqual(kind, "D")) {
                    tasks.push(
                        new Promise((resolve, reject) => {
                            axios
                                .delete(
                                    `/agents/${appState.agent.registryName}/agent/${entity.name}/property/${path}`
                                )
                                .then((response) => {
                                    resolve(true);
                                })
                                .catch((error) => {
                                    AppToaster.show({
                                        intent: Intent.DANGER,
                                        message: `${error.name}: ${error.message}`,
                                    });
                                    reject(false);
                                });
                        })
                    );
                } else {
                    tasks.push(
                        new Promise((resolve, reject) => {
                            axios
                                .post(
                                    `/agents/${appState.agent.registryName}/agent/${entity.name}/property/${path}`,
                                    editEntity.properties[path],
                                    {
                                        headers: {
                                            "Content-type": "application/json",
                                        },
                                    }
                                )
                                .then((response) => {
                                    resolve(true);
                                })
                                .catch((error) => {
                                    AppToaster.show({
                                        intent: Intent.DANGER,
                                        message: `${error.name}: ${error.message}`,
                                    });
                                    reject(false);
                                });
                        })
                    );
                }
            }
        }
        (async () => {
            let progress = 0,
                requestError = false;
            const key = AppToaster.show(renderProgress(progress));
            const promises = tasks.map((task) => {
                return task
                    .catch((status) => {
                        if (!status) {
                            requestError = true;
                        }
                    })
                    .finally(() => {
                        progress += 100 / tasks.length;
                        AppToaster.show(
                            renderProgress(progress, requestError, () => {
                                setLoading(false);
                            }),
                            key
                        );
                    });
            });
            await Promise.allSettled(promises);
            if (!requestError) {
                setEdit(false);
            }
            setLoading(false);
        })();
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
                entity={editEntity}
                updateEntity={updateEntity}
            />
            <EntityProperties
                edit={edit}
                entity={editEntity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
                setLoading={setLoading}
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
