import { useAgentStore } from "@/stores/agent-store";
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
import {
    faBracketsCurly,
    faGrid2Plus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import {
    ENTITY_NAME_SEPARATOR,
    ENTITY_REGISTRY_LOOKUP,
    ENTITY_TYPE_URL_PREFIX_CONVERSION,
    HEX_TRANSPARENCY,
} from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import {
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
} from "../helper";
import EntityDescription from "./attributes/EntityDescription";
import EntityProperties from "./attributes/EntityProperties";
import MainPropertyBlock from "./MainPropertyBlock";
export default function NewEntity({
    type,
    callback,
    parent,
    duplicateEntity,
    registry,
}) {
    const { getAgents } = useAgentStore(
        useShallow((state) => ({ getAgents: state.getAgents }))
    );
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
    const { appToaster, progressToaster, showAxiosErrorToast } = useToaster();
    const JSONError = useRef(false);
    const updateEntity = ({ path, value }) => {
        let temp = _.cloneDeep(newEntity);
        _.set(temp, path, value);
        setNewEntity(temp);
    };
    const handleSave = () => {
        if (JSONError.current) {
            appToaster.show({
                intent: Intent.DANGER,
                icon: <FAIcon icon={faBracketsCurly} />,
                message: "Invalid JSON",
            });
        } else {
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
            let url = `/registry/${ENTITY_REGISTRY_LOOKUP[calculatedType]}`;
            let convertedType = _.get(
                ENTITY_TYPE_URL_PREFIX_CONVERSION,
                calculatedType,
                calculatedType
            );
            if (_.isEqual(calculatedType, "server")) {
                url = `/registry/${ENTITY_REGISTRY_LOOKUP[calculatedType][registry]}`;
                convertedType = _.get(
                    ENTITY_TYPE_URL_PREFIX_CONVERSION,
                    [calculatedType, registry],
                    calculatedType
                );
            }
            if (_.includes(["input", "output"], calculatedType)) {
                url += `/agent/${prefix}/${convertedType}/${fullName}`;
            } else if (_.isEqual(calculatedType, "tool")) {
                url += `/tools/${prefix}/${convertedType}/${fullName}`;
            } else if (_.isEqual(calculatedType, "operator")) {
                url += `/operators/${prefix}/${convertedType}/${fullName}`;
            } else {
                url += `/${convertedType}/${fullName}`;
            }
            axios
                .post(url, {
                    name: fullName,
                    description: newEntity.description,
                })
                .then(() => {
                    appToaster.show({
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
                        showAxiosErrorToast,
                    });
                    settlePromises(
                        promises,
                        ({ error }) => {
                            if (!error) {
                                if (_.isFunction(callback)) {
                                    let scope = _.get(parent, "scope", "/");
                                    if (
                                        !_.isEmpty(parent) &&
                                        _.includes(
                                            [
                                                "agent",
                                                "input",
                                                "output",
                                                "tool",
                                                "operator",
                                            ],
                                            calculatedType
                                        )
                                    ) {
                                        if (!_.isEqual(scope.slice(-1), "/")) {
                                            scope += "/";
                                        }
                                        scope += `${_.get(
                                            parent,
                                            "type"
                                        )}/${prefix}`;
                                    }
                                    callback({
                                        name: fullName,
                                        type: calculatedType,
                                        description: newEntity.description,
                                        scope,
                                    });
                                    console.log(calculatedType);
                                    if (_.isEqual(calculatedType, "agent")) {
                                        getAgents();
                                    }
                                    setLoading(false);
                                }
                            }
                        },
                        progressToaster
                    );
                })
                .catch((error) => {
                    showAxiosErrorToast(error);
                    setLoading(false);
                });
        }
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
                        JSONError={JSONError}
                    />
                </div>
            )}
        </div>
    );
}
