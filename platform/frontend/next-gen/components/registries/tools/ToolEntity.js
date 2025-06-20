import {
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import {
    getEntityMainProperties,
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors, EditableText } from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_TOOL_REGISTRY_NAME } = allEnv();
export default function ToolEntity({ entity, backCrumb }) {
    const { name, scope, type } = entity;
    const [tool, setTool] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedTool, setEditedTool] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateTool = ({ path, value }) => {
        let newTool = _.cloneDeep(editedTool);
        _.set(newTool, path, value);
        setEditedTool(newTool);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const displayName = _.get(mainProperties, "display_name", "");
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = _.replace(
        `/registry/${NEXT_PUBLIC_TOOL_REGISTRY_NAME}/${path}`,
        "/server/",
        "/tools/"
    );
    const onSynchronize = () => {
        setLoading(true);
        axios.put(`${url}/sync`).finally(() => {
            setLoading(false);
        });
    };
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setTool(result);
                setEditedTool(result);
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity, tool]);
    const handleDiscard = () => {
        setEditedTool(tool);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedTool.name,
                description: editedTool.description,
            })
            .then(() => {
                const properties = {
                    ...editedTool.properties,
                    ...mainProperties,
                };
                const diffs = shallowDiff(tool.properties, properties);
                const promises = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(promises, ({ error }) => {
                    if (!error) {
                        const newTool = { ...editedTool, properties };
                        setTool(newTool);
                        setEditedTool(newTool);
                        setMainProperties(getEntityMainProperties(properties));
                        setIsEditing(false);
                    }
                    setLoading(false);
                });
            });
    };
    const onDelete = () => {
        setLoading(true);
        axios.delete(url).finally(() => {
            setLoading(false);
            backCrumb();
        });
    };
    return (
        <div>
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
                {!_.isEmpty(tool) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={tool}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
                            onDelete={onDelete}
                            onSynchronize={onSynchronize}
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
                        content={_.get(editedTool, "icon", null)}
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
                        <div>{_.get(editedTool, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedTool, "name")}
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
                    updateEntity={updateTool}
                    entity={editedTool}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={isEditing}
                    updateEntity={updateTool}
                    entity={editedTool}
                    loading={loading}
                />
            </div>
        </div>
    );
}
