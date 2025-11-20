import {
    ENTITY_TYPE_LOOKUP,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useGridContainerContext } from "@/components/contexts/GridContainerContext";
import { useToaster } from "@/components/contexts/ToasterContext";
import { FAIcon } from "@/components/FAIcon";
import {
    getEntityMainProperties,
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { Classes, Colors, EditableText, Intent } from "@blueprintjs/core";
import { faBracketsCurly } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef, useState } from "react";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import EntityDisplayName from "../EntityDisplayName";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityIcon from "../RegistryEntityIcon";
import InputListens from "./InputListens";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function InputEntity({ entity, backCrumb }) {
    const { name, scope, type } = entity;
    const [input, setInput] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedInput, setEditedInput] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const { appToaster, progressToaster, showAxiosErrorToast } = useToaster();
    const setContainerHeader = useGridStore(
        (state) => state.setContainerHeader
    );
    const { gridContainerId } = useGridContainerContext();
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateInput = ({ path, value }) => {
        let newInput = _.cloneDeep(editedInput);
        _.set(newInput, path, value);
        setEditedInput(newInput);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const displayName = _.get(mainProperties, "display_name", "");
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/${path}`;
    useEffect(() => {
        setContainerHeader({
            id: gridContainerId,
            title: <EntityDisplayName entity={input} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [input, gridContainerId, setContainerHeader, type]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setInput(result);
                setEditedInput(result);
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity, url]);
    const JSONError = useRef(false);
    const handleDiscard = () => {
        setEditedInput(input);
        setMainProperties(
            getEntityMainProperties(_.get(input, "properties", {}))
        );
        setIsEditing(false);
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
            axios
                .put(url, {
                    name: editedInput.name,
                    description: editedInput.description,
                })
                .then(() => {
                    const properties = {
                        ...editedInput.properties,
                        ...mainProperties,
                    };
                    const diffs = shallowDiff(input.properties, properties);
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
                                const newInput = { ...editedInput, properties };
                                setInput(newInput);
                                setEditedInput(newInput);
                                setMainProperties(
                                    getEntityMainProperties(properties)
                                );
                                setIsEditing(false);
                            }
                            setLoading(false);
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
    const onDelete = () => {
        setLoading(true);
        axios.delete(url).finally(() => {
            setLoading(false);
            backCrumb();
        });
    };
    const onDoubleClick = () => {
        if (!isEditing) {
            setIsEditing(true);
        }
    };
    return (
        <div>
            <div
                onDoubleClick={onDoubleClick}
                style={{
                    backgroundColor: `${Colors.BLUE3}${
                        HEX_TRANSPARENCY[darkMode ? 20 : 10]
                    }`,
                    borderRadius: 2,
                    padding: 20,
                    position: "relative",
                }}
            >
                {!_.isEmpty(input) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={input}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
                            onDelete={onDelete}
                        />
                    </div>
                )}
                <div
                    className={classNames(
                        "padding-0",
                        "overflow-hidden",
                        "custom-card",
                        { [Classes.SKELETON]: loading }
                    )}
                    style={{
                        ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                        position: "absolute",
                        left: 20,
                        top: 20,
                    }}
                >
                    <RegistryEntityIcon
                        type={type}
                        content={_.get(editedInput, "icon", null)}
                    />
                </div>
                <div
                    style={{
                        display: "flex",
                        marginLeft: 60,
                        columnGap: 40,
                        rowGap: 20,
                        flexWrap: "wrap",
                        paddingRight: isEditing ? 150.96 : 60,
                    }}
                >
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={MAIN_INFO_STYLES}
                    >
                        <div>{_.get(editedInput, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedInput, "name")}
                        </div>
                    </div>
                    <MainPropertyBlock loading={loading} label="Display name">
                        {isEditing ? (
                            <EditableText
                                alwaysRenderInput
                                value={displayName}
                                onChange={(value) => {
                                    updateMainProperties({
                                        path: "display_name",
                                        value,
                                    });
                                }}
                            />
                        ) : (
                            <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                                {!_.isEmpty(displayName) ? displayName : "-"}
                            </div>
                        )}
                    </MainPropertyBlock>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityDescription
                    isEditing={isEditing}
                    updateEntity={updateInput}
                    entity={editedInput}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <InputListens
                    updateMainProperties={updateMainProperties}
                    isEditing={isEditing}
                    properties={mainProperties}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={isEditing}
                    setIsEditing={setIsEditing}
                    updateEntity={updateInput}
                    entity={editedInput}
                    loading={loading}
                    JSONError={JSONError}
                />
            </div>
        </div>
    );
}
