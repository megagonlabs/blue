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
import { diff } from "deep-diff";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
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
        properties: { image: "" },
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
                const difference = diff({}, entity.properties),
                    tasks = constructSavePropertyRequests({
                        axios,
                        difference,
                        appState,
                        entity,
                        editEntity: entity,
                    });
                settlePromises(tasks, (error) => {
                    if (!error) {
                        let path = router.asPath;
                        path = path.substring(0, path.lastIndexOf("/"));
                        router.push(`${path}/agent/${entity.name}`);
                        setLoading(false);
                    }
                });
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
                            className={Classes.TEXT_MUTED}
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
                            disabled={jsonError}
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
