import { FAIcon } from "@/components/FAIcon";
import {
    ENTITY_REGISTRY_LOOKUP,
    ENTITY_TYPE_LOOKUP,
    ENTITY_TYPE_URL_PREFIX_CONVERSION,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useGridContainerContext } from "@/components/contexts/GridContainerContext";
import { useToaster } from "@/components/contexts/ToasterContext";
import {
    getEntityMainProperties,
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    EditableText,
    EntityTitle,
    H3,
    Intent,
} from "@blueprintjs/core";
import {
    faBracketsCurly,
    faPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import EntityActions from "../EntityActions";
import EntityDisplayName from "../EntityDisplayName";
import Leaves from "../Leaves";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityContainer from "../RegistryEntityContainer";
import RegistryEntityIcon from "../RegistryEntityIcon";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
export default function ServerEntity({
    entity,
    registry,
    addCrumb,
    backCrumb,
    setShowNewEntity,
    setNewEntityType,
}) {
    const { name, type } = entity;
    const [server, setServer] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedServer, setEditedServer] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const { gridContainerId } = useGridContainerContext();
    const [template, setTemplate] = useState(null);
    const { appToaster, progressToaster, showAxiosErrorToast } = useToaster();
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
    const updateServer = ({ path, value }) => {
        let newServer = _.cloneDeep(editedServer);
        _.set(newServer, path, value);
        setEditedServer(newServer);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const displayName = _.get(mainProperties, "display_name", "");
    const url = `/registry/${ENTITY_REGISTRY_LOOKUP[type][registry]}/${_.get(
        ENTITY_TYPE_URL_PREFIX_CONVERSION,
        [type, registry],
        type
    )}/${name}`;
    const JSONError = useRef(false);
    useEffect(() => {
        setContainerHeader({
            id: gridContainerId,
            title: <EntityDisplayName entity={server} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [server, setContainerHeader, gridContainerId]);
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
                setServer(result);
                setEditedServer(result);
                setTemplate(result);
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity, url]);
    const handleDiscard = () => {
        setEditedServer(server);
        setMainProperties(
            getEntityMainProperties(_.get(server, "properties", {}))
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
                    name: editedServer.name,
                    description: editedServer.description,
                    icon: editedServer.icon,
                })
                .then(() => {
                    const properties = {
                        ...editedServer.properties,
                        ...mainProperties,
                    };
                    const diffs = shallowDiff(server.properties, properties);
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
                                const newServer = {
                                    ...editedServer,
                                    properties,
                                };
                                setServer(newServer);
                                setEditedServer(newServer);
                                setTemplate(newServer);
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
    const onDuplicate = () => {
        addContainer({
            content: (
                <RegistryEntityContainer
                    entity={template}
                    duplicate={true}
                    registry={registry}
                />
            ),
        });
    };
    const NESTED_ENTITY_LOOKUP = { tool: "tool", operator: "operator" };
    const isRay = _.isEqual(
        _.get(server, "properties.connection.protocol", null),
        "ray"
    );
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
                {!_.isEmpty(server) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={server}
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
                    style={{
                        ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                        position: "absolute",
                        left: 20,
                        top: 20,
                    }}
                >
                    <RegistryEntityIcon
                        type={type}
                        content={_.get(editedServer, "icon", null)}
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
                        <div>{_.get(editedServer, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedServer, "name")}
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
                    updateEntity={updateServer}
                    entity={editedServer}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={isEditing}
                    updateEntity={updateServer}
                    entity={editedServer}
                    loading={loading}
                    JSONError={JSONError}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <div style={{ marginBottom: 10 }}>
                    <EntityTitle
                        icon={
                            <FAIcon
                                icon={
                                    ENTITY_TYPE_LOOKUP[
                                        NESTED_ENTITY_LOOKUP[registry]
                                    ].icon
                                }
                                size={25}
                            />
                        }
                        heading={H3}
                        title={`${_.capitalize(
                            NESTED_ENTITY_LOOKUP[registry]
                        )}s`}
                    />
                </div>
                <div className="responsive-grid-container">
                    <Leaves
                        isEditing={isEditing}
                        loading={loading}
                        addCrumb={addCrumb}
                        list={_.values(
                            _.get(
                                server,
                                `contents.${NESTED_ENTITY_LOOKUP[registry]}`,
                                {}
                            )
                        )}
                    />
                    {!isEditing && !_.includes(["tool"], registry) && isRay && (
                        <Button
                            disabled={loading}
                            variant={ButtonVariant.MINIMAL}
                            icon={<FAIcon icon={faPlus} />}
                            fill
                            text={`Add ${NESTED_ENTITY_LOOKUP[registry]}`}
                            onClick={() => {
                                setShowNewEntity(true);
                                setNewEntityType(
                                    NESTED_ENTITY_LOOKUP[registry]
                                );
                            }}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
