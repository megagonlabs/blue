import {
    ENTITY_MAIN_INFO_PROPERTY_KEYS,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { getUpdatePropertyPromises, settlePromises } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors, EditableText } from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import shallowDiff from "shallow-diff";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_OPERATOR_REGISTRY_NAME } = allEnv();
export default function OperatorEntity({ entity }) {
    const { name, scope, type } = entity;
    const [operator, setOperator] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedOperator, setEditedOperator] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateOperator = ({ path, value }) => {
        let newOperator = _.cloneDeep(editedOperator);
        _.set(newOperator, path, value);
        setEditedOperator(newOperator);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const displayName = _.get(mainProperties, "display_name", "");
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = `/registry/${NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/${path}`;
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setOperator(result);
                setEditedOperator(result);
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
        setEditedOperator(operator);
        const properties = _.pick(
            _.get(operator, "properties", {}),
            ENTITY_MAIN_INFO_PROPERTY_KEYS
        );
        setMainProperties(properties);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedOperator.name,
                description: editedOperator.description,
            })
            .then(() => {
                const properties = {
                    ...editedOperator.properties,
                    ...mainProperties,
                };
                const diffs = shallowDiff(operator.properties, properties);
                const tasks = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(tasks, ({ error }) => {
                    if (!error) {
                        const newOperator = { ...editedOperator, properties };
                        setOperator(newOperator);
                        setEditedOperator(newOperator);
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
                {!_.isEmpty(operator) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={operator}
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
                        content={_.get(editedOperator, "icon", null)}
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
                        <div>{_.get(editedOperator, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedOperator, "name")}
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
                    updateEntity={updateOperator}
                    entity={editedOperator}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={isEditing}
                    updateEntity={updateOperator}
                    entity={editedOperator}
                    loading={loading}
                />
            </div>
        </div>
    );
}
