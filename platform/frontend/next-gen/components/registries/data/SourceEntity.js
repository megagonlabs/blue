import {
    ENTITY_TYPE_LOOKUP,
    ENTITY_TYPE_URL_PREFIX_CONVERSION,
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
import { UICallout } from "@/components/ux/UICallout";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    Classes,
    Colors,
    EditableText,
    EntityTitle,
    H3,
    Intent,
    Size,
    Tag,
} from "@blueprintjs/core";
import {
    faAngleRight,
    faEllipsisV,
    faSync,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
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
import Leaves from "../Leaves";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityContainer from "../RegistryEntityContainer";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
export default function SourceEntity({
    entity,
    addCrumb,
    setShowIconEditor,
    icon,
    setIcon,
    backCrumb,
}) {
    const { name, type } = entity;
    const [source, setSource] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedSource, setEditedSource] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const { gridContainerId } = useGridContainerContext();
    const [template, setTemplate] = useState(null);
    const { progressToaster, showAxiosErrorToast } = useToaster();
    const { setContainerHeader, addContainer } = useGridStore(
        useShallow((state) => ({
            addContainer: state.addContainer,
            setContainerHeader: state.setContainerHeader,
        }))
    );
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
    const darkMode = useAppStore((state) => state.dark_mode);
    const displayName = _.get(mainProperties, "display_name", "");
    const url = `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/${_.get(
        ENTITY_TYPE_URL_PREFIX_CONVERSION,
        type,
        type
    )}/${name}`;
    const onSynchronize = () => {
        setLoading(true);
        axios.put(`${url}/sync`).finally(() => {
            setLoading(false);
        });
    };
    useEffect(() => {
        setContainerHeader({
            id: gridContainerId,
            title: <EntityDisplayName entity={source} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [source]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setSource(result);
                setEditedSource(result);
                setTemplate(result);
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity]);
    useEffect(() => {
        updateSource({ path: "icon", value: icon });
    }, [icon]);
    const handleDiscard = () => {
        setEditedSource(source);
        setMainProperties(
            getEntityMainProperties(_.get(source, "properties", {}))
        );
        setIsEditing(false);
        setIcon(_.get(source, "icon", null));
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedSource.name,
                description: editedSource.description,
                icon: editedSource.icon,
            })
            .then(() => {
                const properties = {
                    ...editedSource.properties,
                    ...mainProperties,
                };
                const diffs = shallowDiff(source.properties, properties);
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
                            const newSource = { ...editedSource, properties };
                            setSource(newSource);
                            setEditedSource(newSource);
                            setTemplate(newSource);
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
    };
    const onDelete = () => {
        setLoading(true);
        axios.delete(url).finally(() => {
            setLoading(false);
            backCrumb();
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
            <div style={{ marginBottom: 20 }}>
                <UICallout
                    id="data_registry_source_entity_synchronize"
                    content={
                        <div
                            style={{
                                display: "flex",
                                alignItems: "center",
                                flexWrap: "wrap",
                            }}
                        >
                            Synchronize the data source by{" "}
                            <span>clicking on</span>
                            <Button
                                className="pointer-events-none"
                                style={{ marginLeft: 5, marginRight: 5 }}
                                intent={Intent.PRIMARY}
                                icon={<FAIcon icon={faEllipsisV} />}
                            />
                            <FAIcon icon={faAngleRight} />
                            <Tag
                                style={{ marginLeft: 5, marginRight: 5 }}
                                minimal
                                icon={<FAIcon icon={faSync} />}
                                size={Size.LARGE}
                                intent={Intent.SUCCESS}
                            >
                                Synchronize
                            </Tag>
                            .
                        </div>
                    }
                />
            </div>
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
                            onDelete={onDelete}
                            onSynchronize={onSynchronize}
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
                        isEditing={isEditing}
                        loading={loading}
                        addCrumb={addCrumb}
                        list={_.values(_.get(source, "contents.database", {}))}
                    />
                </div>
            </div>
        </div>
    );
}
