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
import { faGrid2Plus } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import {
    ENTITY_NAME_SEPARATOR,
    ENTITY_TYPE_CONVERSION,
    HEX_TRANSPARENCY,
} from "../constants";
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
    NEXT_PUBLIC_TOOL_REGISTRY_NAME,
} = allEnv();
export default function NewEntity({ type, callback, parent, duplicateEntity }) {
    const [newEntity, setNewEntity] = useState({ type, description: "" });
    const calculatedType = !_.isEmpty(duplicateEntity)
        ? duplicateEntity.type
        : type;
    useEffect(() => {
        if (!_.isEmpty(duplicateEntity)) {
            setNewEntity(duplicateEntity);
        }
    }, [duplicateEntity]);
    const darkMode = useAppStore((state) => state.dark_mode);
    const [loading, setLoading] = useState(false);
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
    const handleSave = () => {
        setLoading(true);
        let fullName = newEntity.name;
        const prefix = _.get(parent, "name", "");
        if (_.isEqual(calculatedType, "agent")) {
            fullName = prefix;
            if (!_.isEmpty(fullName)) {
                fullName += ENTITY_NAME_SEPARATOR;
            }
            fullName += newEntity.name;
        }
        const REGISTRY_NAME_LOOKUP = {
            agent: NEXT_PUBLIC_AGENT_REGISTRY_NAME,
            agent_group: NEXT_PUBLIC_AGENT_REGISTRY_NAME,
            input: NEXT_PUBLIC_AGENT_REGISTRY_NAME,
            output: NEXT_PUBLIC_AGENT_REGISTRY_NAME,
            source: NEXT_PUBLIC_DATA_REGISTRY_NAME,
            operator: NEXT_PUBLIC_OPERATOR_REGISTRY_NAME,
            model: NEXT_PUBLIC_MODEL_REGISTRY_NAME,
            server: NEXT_PUBLIC_TOOL_REGISTRY_NAME,
            tool: NEXT_PUBLIC_TOOL_REGISTRY_NAME,
        };
        let url = `/registry/${REGISTRY_NAME_LOOKUP[calculatedType]}`;
        const convertedType = _.get(
            ENTITY_TYPE_CONVERSION,
            calculatedType,
            calculatedType
        );
        if (_.includes(["input", "output"], calculatedType)) {
            url += `/agent/${prefix}/${convertedType}/${fullName}`;
        } else if (_.isEqual(calculatedType, "tool")) {
            url += `/tools/${prefix}/${convertedType}/${fullName}`;
        } else {
            url += `/${convertedType}/${fullName}`;
        }
        axios
            .post(url, {
                name: fullName,
                description: newEntity.description,
            })
            .then(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Created ${newEntity.name} ${calculatedType}`,
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
                        if (_.isFunction(callback)) {
                            let scope = _.get(parent, "scope", "/");
                            if (
                                !_.isEmpty(parent) &&
                                _.includes(
                                    ["agent", "input", "output", "tool"],
                                    calculatedType
                                )
                            ) {
                                if (!_.isEqual(scope.slice(-1), "/")) {
                                    scope += "/";
                                }
                                scope += `${_.get(parent, "type")}/${prefix}`;
                            }
                            callback({
                                name: fullName,
                                type: calculatedType,
                                description: newEntity.description,
                                scope,
                            });
                            setLoading(false);
                        }
                    }
                });
            })
            .catch((error) => {
                showAxiosErrorToast(error);
                setLoading(false);
            });
    };
    return (
        <div>
            <H3 style={{ marginBottom: 20 }}>
                Create&nbsp;
                {_.isEqual(calculatedType, "agent_group")
                    ? "application"
                    : calculatedType}
            </H3>
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
                        onClick={handleSave}
                        icon={<FAIcon icon={faGrid2Plus} />}
                        size={Size.LARGE}
                        intent={Intent.SUCCESS}
                        text="Create"
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
                    {!_.isEqual(calculatedType, "agent_group") && (
                        <MainPropertyBlock
                            loading={loading}
                            label="Display name"
                        >
                            <EditableText
                                alwaysRenderInput
                                value={_.get(
                                    mainProperties,
                                    "display_name",
                                    ""
                                )}
                                onChange={(value) => {
                                    updateMainProperties({
                                        path: "display_name",
                                        value,
                                    });
                                }}
                            />
                        </MainPropertyBlock>
                    )}
                    {_.isEqual(calculatedType, "agent") && (
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
            {!_.isEqual(calculatedType, "agent_group") && (
                <div style={{ marginTop: 20 }}>
                    <EntityProperties
                        isEditing={true}
                        updateEntity={updateEntity}
                        entity={newEntity}
                        loading={loading}
                    />
                </div>
            )}
        </div>
    );
}
