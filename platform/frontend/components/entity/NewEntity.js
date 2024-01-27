import {
    Button,
    Classes,
    EditableText,
    Intent,
    Section,
    SectionCard,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import { diff } from "deep-diff";
import _ from "lodash";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../app-context";
import { constructSavePropertyRequests, settlePromises } from "../helper";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
import EntityDescription from "./EntityDescription";
import EntityProperties from "./EntityProperties";
export default function NewEntity({ type }) {
    const { appState } = useContext(AppContext);
    const router = useRouter();
    const [entity, setEntity] = useState({
        name: "",
        properties: {},
        description: "",
    });
    const [created, setCreated] = useState(false);
    const [loading, setLoading] = useState(false);
    const [jsonError, setJsonError] = useState(false);
    const updateEntity = ({ path, value }) => {
        let newEntity = _.cloneDeep(entity);
        _.set(newEntity, path, value);
        setEntity(newEntity);
    };
    useEffect(() => {
        if (!router.isReady) return;
        if (!_.includes(router.asPath, "/default/new?entity=")) return;
        let params = [..._.get(router, "query.params", [])];
        params.splice(params.length - 1, 1);
        axios
            .get(`/${params.join("/")}/${type}/${router.query.entity}`)
            .then((response) => {
                let result = _.get(response, "data.result", {});
                _.set(result, "name", "");
                if (!_.isEmpty(result)) {
                    setEntity(_.get(response, "data.result", {}));
                }
            });
    }, [router]);
    const saveEntity = () => {
        if (!router.isReady) return;
        setLoading(true);
        axios[created ? "put" : "post"](
            `/agents/${appState[type].registryName}/${type}/${entity.name}`,
            {
                name: entity.name,
                description: entity.description,
            }
        )
            .then(() => {
                setCreated(true);
                const difference = diff({}, entity.properties);
                settlePromises(
                    constructSavePropertyRequests({
                        axios,
                        difference,
                        appState,
                        entity,
                        editEntity: entity,
                    }),
                    (error) => {
                        if (!error) {
                            let params = _.cloneDeep(
                                _.get(router, "query.params", [])
                            );
                            params.splice(params.length - 1, 1);
                            router.push(
                                `/${params.join("/")}/agent/${entity.name}`
                            );
                        }
                        setLoading(false);
                    }
                );
            })
            .catch((error) => {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `${error.name}: ${error.message}`,
                });
                setLoading(false);
            });
    };
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <Section compact style={{ position: "relative" }}>
                <SectionCard padded={false}>
                    <div style={{ display: "flex" }}>
                        <div
                            className={classNames(
                                Classes.TEXT_MUTED,
                                "required"
                            )}
                            style={{ width: 52.7, margin: "20px 0px 0px 20px" }}
                        >
                            Name
                        </div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                width: "calc(100% - 248.86px)",
                                padding: "20px 10px 10px 10px",
                            }}
                        >
                            <EditableText
                                intent={
                                    _.isEmpty(entity.name)
                                        ? Intent.DANGER
                                        : null
                                }
                                value={entity.name}
                                onChange={(value) => {
                                    updateEntity({ path: "name", value });
                                }}
                            />
                        </div>
                    </div>
                    <div style={{ display: "flex" }}>
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ width: 52.7, margin: "0px 0px 20px 20px" }}
                        >
                            Type
                        </div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                width: "calc(100% - 248.86px)",
                                padding: "0px 10px 20px 10px",
                            }}
                        >
                            {type}
                        </div>
                    </div>
                    <div
                        style={{
                            position: "absolute",
                            right: 15,
                            top: "50%",
                            transform: "translateY(-50%)",
                            msTransform: "translateY(-50%)",
                        }}
                    >
                        <Button
                            className={loading ? Classes.SKELETON : null}
                            large
                            disabled={jsonError || _.isEmpty(entity.name)}
                            intent={Intent.SUCCESS}
                            text="Save"
                            onClick={saveEntity}
                            icon={faIcon({ icon: faCheck })}
                        />
                    </div>
                </SectionCard>
            </Section>
            <EntityDescription
                edit
                entity={entity}
                updateEntity={updateEntity}
            />
            <EntityProperties
                edit
                entity={entity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
                setLoading={setLoading}
            />
        </div>
    );
}
