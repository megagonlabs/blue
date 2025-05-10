import {
    ENTITY_MAIN_INFO_PROPERTY_KEYS,
    ENTITY_TYPE_LOOKUP,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { getUpdatePropertyPromises, settlePromises } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import {
    Classes,
    Colors,
    EditableText,
    EntityTitle,
    H3,
} from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import shallowDiff from "shallow-diff";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import Leaves from "../Leaves";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
export default function SourceEntity({ entity, addCrumb }) {
    const { name, scope, type } = entity;
    const [source, setSource] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedSource, setEditedSource] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateSource = ({ path, value }) => {
        let newSource = _.cloneDeep(editedSource);
        _.set(newSource, path, value);
        setEditedSource(newSource);
    };
    const darkMode = useAppStore((state) => state.darkMode);
    const displayName = _.get(mainProperties, "display_name", "");
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = _.replace(
        `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/${path}`,
        "/source",
        "/data"
    );
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setSource(result);
                setEditedSource(result);
                const properties = _.pick(
                    _.get(result, "properties", {}),
                    ENTITY_MAIN_INFO_PROPERTY_KEYS
                );
                setMainProperties(properties);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity]);
    const handleDiscard = () => {
        setEditedSource(source);
        const properties = _.pick(
            _.get(source, "properties", {}),
            ENTITY_MAIN_INFO_PROPERTY_KEYS
        );
        setMainProperties(properties);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedSource.name,
                description: editedSource.description,
            })
            .then(() => {
                const properties = {
                    ...editedSource.properties,
                    ...mainProperties,
                };
                const diffs = shallowDiff(source.properties, properties);
                const tasks = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(tasks, ({ error }) => {
                    if (!error) {
                        const newSource = { ...editedSource, properties };
                        setSource(newSource);
                        setEditedSource(newSource);
                        setMainProperties(properties);
                        setIsEditing(false);
                    }
                    setLoading(false);
                });
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
                {!_.isEmpty(source) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={source}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
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
                        content={_.get(editedSource, "icon", null)}
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
                        <div>{_.get(editedSource, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedSource, "name")}
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
                    updateEntity={updateSource}
                    entity={editedSource}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={isEditing}
                    updateEntity={updateSource}
                    entity={editedSource}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <div style={{ marginBottom: 10 }}>
                    <EntityTitle
                        icon={
                            <FAIcon
                                icon={ENTITY_TYPE_LOOKUP["database"].icon}
                                size={25}
                            />
                        }
                        heading={H3}
                        title="Databases"
                    />
                </div>
                <div
                    style={{
                        display: "flex",
                        gap: 10,
                        flexDirection: "column",
                    }}
                >
                    <Leaves
                        loading={loading}
                        addCrumb={addCrumb}
                        list={_.values(_.get(source, "contents.database", {}))}
                    />
                </div>
            </div>
        </div>
    );
}
