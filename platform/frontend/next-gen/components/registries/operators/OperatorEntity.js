import {
    ENTITY_TYPE_LOOKUP,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useGridContainerContext } from "@/components/contexts/GridContainerContext";
import {
    getEntityMainProperties,
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { Classes, Colors, EditableText } from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import EntityDisplayName from "../EntityDisplayName";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityContainer from "../RegistryEntityContainer";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_OPERATOR_REGISTRY_NAME } = allEnv();
export default function OperatorEntity({
    entity,
    setShowIconEditor,
    icon,
    setIcon,
}) {
    const { name, type } = entity;
    const [operator, setOperator] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedOperator, setEditedOperator] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const { gridContainerId } = useGridContainerContext();
    const [template, setTemplate] = useState(null);
    const { removeContainer, setContainerHeader, addContainer } = useGridStore(
        useShallow((state) => ({
            removeContainer: state.removeContainer,
            addContainer: state.addContainer,
            setContainerHeader: state.setContainerHeader,
        }))
    );
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
    const url = `/registry/${NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/${type}/${name}`;
    useEffect(() => {
        setContainerHeader({
            id: gridContainerId,
            title: <EntityDisplayName entity={operator} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [operator, setContainerHeader, gridContainerId]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setOperator(result);
                setEditedOperator(result);
                setTemplate(result);
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity, url]);
    useEffect(() => {
        updateOperator({ path: "icon", value: icon });
    }, [icon]);
    const handleDiscard = () => {
        setEditedOperator(operator);
        setMainProperties(
            getEntityMainProperties(_.get(operator, "properties", {}))
        );
        setIsEditing(false);
        setIcon(_.get(operator, "icon", null));
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedOperator.name,
                description: editedOperator.description,
                icon: editedOperator.icon,
            })
            .then(() => {
                const properties = {
                    ...editedOperator.properties,
                    ...mainProperties,
                };
                const diffs = shallowDiff(operator.properties, properties);
                const promises = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(promises, ({ error }) => {
                    if (!error) {
                        const newOperator = { ...editedOperator, properties };
                        setOperator(newOperator);
                        setEditedOperator(newOperator);
                        setTemplate(newOperator);
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
            removeContainer(gridContainerId);
        });
    };
    const onDuplicate = () => {
        addContainer({
            content: (
                <RegistryEntityContainer entity={template} duplicate={true} />
            ),
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
                            onDelete={onDelete}
                            onDuplicate={onDuplicate}
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
                    onClick={() => {
                        if (_.isFunction(setShowIconEditor)) {
                            setShowIconEditor(isEditing);
                        }
                    }}
                    style={{
                        ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                        position: "absolute",
                        left: 20,
                        top: 20,
                        cursor:
                            isEditing && _.isFunction(setIcon)
                                ? "pointer"
                                : null,
                    }}
                >
                    <RegistryEntityIcon
                        type={type}
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
