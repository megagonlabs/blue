import { useAppStore } from "@/stores/app-store";
import {
    Button,
    Classes,
    Colors,
    EditableText,
    H3,
    Intent,
    Size,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useState } from "react";
import { ENTITY_TYPE_CONVERSION, HEX_TRANSPARENCY } from "../constants";
import { FAIcon } from "../FAIcon";
import {
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
    showAxiosErrorToast,
} from "../helper";
import { AppToaster } from "../toaster";
import EntityDescription from "./attributes/EntityDescription";
import EntityProperties from "./attributes/EntityProperties";
import MainPropertyBlock from "./MainPropertyBlock";
const {
    NEXT_PUBLIC_AGENT_REGISTRY_NAME,
    NEXT_PUBLIC_DATA_REGISTRY_NAME,
    NEXT_PUBLIC_OPERATOR_REGISTRY_NAME,
    NEXT_PUBLIC_MODEL_REGISTRY_NAME,
} = allEnv();
export default function NewEntity({ entity, addCrumb, setCreated }) {
    const type = _.get(entity, "type", null);
    const [newEntity, setNewEntity] = useState({
        ...entity,
        type,
        description: "",
    });
    const darkMode = useAppStore((state) => state.dark_mode);
    const [loading, setLoading] = useState(false);
    const [namePrefix, setNamePrefix] = useState("");
    const [mainProperties, setMainProperties] = useState({});
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateEntity = ({ path, value }) => {
        let temp = _.cloneDeep(newEntity);
        _.set(temp, path, value);
        setNewEntity(temp);
    };
    const onSave = () => {
        setLoading(true);
        const fullName = `${namePrefix}${newEntity.name}`;
        const REGISTRY_NAME_LOOKUP = {
            agent: NEXT_PUBLIC_AGENT_REGISTRY_NAME,
            source: NEXT_PUBLIC_DATA_REGISTRY_NAME,
            operator: NEXT_PUBLIC_OPERATOR_REGISTRY_NAME,
            model: NEXT_PUBLIC_MODEL_REGISTRY_NAME,
        };
        const url = `/registry/${REGISTRY_NAME_LOOKUP[type]}/${_.get(
            ENTITY_TYPE_CONVERSION,
            type,
            type
        )}/${fullName}`;
        axios
            .post(url, {
                name: fullName,
                description: newEntity.description,
            })
            .then(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Created ${newEntity.name} ${type}`,
                });
                const properties = {
                    ...newEntity.properties,
                    ...mainProperties,
                };
                const diffs = shallowDiff({}, properties);
                const promises = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(promises, ({ error }) => {
                    if (!error) {
                        addCrumb(newEntity);
                        setCreated(true);
                    }
                });
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <div>
            <H3 style={{ marginBottom: 20 }}>Create {type}</H3>
            <div
                style={{
                    backgroundColor: `${Colors.BLUE3}${
                        HEX_TRANSPARENCY[darkMode ? 20 : 10]
                    }`,
                    borderRadius: 2,
                    padding: 20,
                    position: "relative",
                }}
            >
                <div
                    className={loading ? Classes.SKELETON : null}
                    style={{ position: "absolute", right: 20 }}
                >
                    <Button
                        disabled={_.isEmpty(newEntity.name)}
                        onClick={onSave}
                        icon={<FAIcon icon={faCheck} />}
                        size={Size.LARGE}
                        intent={Intent.SUCCESS}
                        text="Save"
                    />
                </div>
                <div
                    style={{
                        display: "flex",
                        columnGap: 40,
                        rowGap: 20,
                        flexWrap: "wrap",
                    }}
                >
                    <MainPropertyBlock loading={loading} label="Name">
                        <EditableText
                            alwaysRenderInput
                            value={_.get(newEntity, "name")}
                            onChange={(value) => {
                                updateEntity({ path: "name", value });
                            }}
                        />
                    </MainPropertyBlock>
                    <MainPropertyBlock loading={loading} label="Display name">
                        <EditableText
                            alwaysRenderInput
                            value={_.get(mainProperties, "display_name", "")}
                            onChange={(value) => {
                                updateMainProperties({
                                    path: "display_name",
                                    value,
                                });
                            }}
                        />
                    </MainPropertyBlock>
                    {_.isEqual(type, "agent") && (
                        <MainPropertyBlock
                            loading={loading}
                            label="Docker image"
                        >
                            <EditableText
                                alwaysRenderInput
                                value={_.get(mainProperties, "image", "")}
                                onChange={(value) => {
                                    updateMainProperties({
                                        path: "image",
                                        value,
                                    });
                                }}
                            />
                        </MainPropertyBlock>
                    )}
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityDescription
                    isEditing={true}
                    updateEntity={updateEntity}
                    entity={newEntity}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={true}
                    updateEntity={updateEntity}
                    entity={newEntity}
                    loading={loading}
                />
            </div>
        </div>
    );
}
