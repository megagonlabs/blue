import {
    ENTITY_TYPE_LOOKUP,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useGridContainerContext } from "@/components/contexts/GridContainerContext";
import { FAIcon } from "@/components/FAIcon";
import {
    getEntityMainProperties,
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
    showAxiosErrorToast,
} from "@/components/helper";
import { UICallout } from "@/components/ux/UICallout";
import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    EditableText,
    EntityTitle,
    H3,
} from "@blueprintjs/core";
import {
    faCheckCircle,
    faPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import EntityDisplayName from "../EntityDisplayName";
import Leaves from "../Leaves";
import MainPropertyBlock from "../MainPropertyBlock";
import RegistryEntityContainer from "../RegistryEntityContainer";
import RegistryEntityIcon from "../RegistryEntityIcon";
import AgentMainProperties from "./AgentMainProperties";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function AgentEntity({
    entity,
    addCrumb,
    setShowIconEditor,
    icon,
    setIcon,
    setShowNewEntity,
    setNewEntityType,
    backCrumb,
}) {
    const { name, type, scope, created_by = null } = entity;
    const { gridContainerId } = useGridContainerContext();
    const setContainerHeader = useGridStore(
        (state) => state.setContainerHeader
    );
    const { user, permissions } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            permissions: state.permissions,
        }))
    );
    const own = _.isEqual(created_by, user.uid);
    const canEditEntity = useMemo(() => {
        // write_all
        const permissionKey = _.get(
            ENTITY_TYPE_LOOKUP,
            [type, "permissionKey"],
            null
        );
        const writeAll = _.includes(
            _.get(user, ["permissions", permissionKey], []),
            "write_all"
        );
        return own || writeAll;
    }, [user, permissions]);
    const baseAgent = !_.isEmpty(scope) && _.isEqual(scope, "/");
    const [agent, setAgent] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedAgent, setEditedAgent] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const [template, setTemplate] = useState(null);
    const addContainer = useGridStore((state) => state.addContainer);
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateAgent = ({ path, value }) => {
        let newAgent = _.cloneDeep(editedAgent);
        _.set(newAgent, path, value);
        setEditedAgent(newAgent);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const systemAgent = _.get(mainProperties, "system_agent", false);
    const displayName = _.get(mainProperties, "display_name", "");
    const image = _.get(mainProperties, "image", "");
    const url = `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/${type}/${name}`;
    useEffect(() => {
        setContainerHeader({
            id: gridContainerId,
            title: <EntityDisplayName entity={agent} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [agent]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setAgent(result);
                setEditedAgent(result);
                setTemplate(result);
                setIcon(_.get(result, "icon", null));
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity]);
    useEffect(() => {
        updateAgent({ path: "icon", value: icon });
    }, [icon]);
    const handleDiscard = () => {
        setEditedAgent(agent);
        setMainProperties(
            getEntityMainProperties(_.get(agent, "properties", {}))
        );
        setIsEditing(false);
        setIcon(_.get(agent, "icon", null));
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name,
                description: editedAgent.description,
                icon: editedAgent.icon,
            })
            .then(() => {
                let updated = _.cloneDeep(mainProperties);
                const properties = { ...editedAgent.properties, ...updated };
                const diffs = shallowDiff(agent.properties, properties);
                const promises = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(promises, ({ error }) => {
                    if (!error) {
                        const newAgent = { ...editedAgent, properties };
                        setEditedAgent(newAgent);
                        setAgent(newAgent);
                        setTemplate(newAgent);
                        setMainProperties(getEntityMainProperties(properties));
                        setIsEditing(false);
                    }
                    setLoading(false);
                });
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
                {!_.isEmpty(agent) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={agent}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
                            onDelete={onDelete}
                            onDuplicate={baseAgent && onDuplicate}
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
                        content={_.get(editedAgent, "icon", null)}
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
                        <div>{_.get(editedAgent, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedAgent, "name")}
                        </div>
                    </div>
                    <MainPropertyBlock loading={loading} label="System agent">
                        {systemAgent ? (
                            <FAIcon
                                style={{ color: Colors.GREEN3 }}
                                icon={faCheckCircle}
                            />
                        ) : (
                            "-"
                        )}
                    </MainPropertyBlock>
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
                    <MainPropertyBlock loading={loading} label="Docker image">
                        {isEditing ? (
                            <EditableText
                                alwaysRenderInput
                                value={image}
                                onChange={(value) => {
                                    updateMainProperties({
                                        path: "image",
                                        value,
                                    });
                                }}
                            />
                        ) : (
                            <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                                {!_.isEmpty(image) ? image : "-"}
                            </div>
                        )}
                    </MainPropertyBlock>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <AgentMainProperties
                    updateMainProperties={updateMainProperties}
                    isEditing={isEditing}
                    properties={mainProperties}
                    loading={loading}
                />
                <div style={{ marginTop: 20 }}>
                    <EntityDescription
                        isEditing={isEditing}
                        updateEntity={updateAgent}
                        entity={editedAgent}
                        loading={loading}
                    />
                </div>
                {!baseAgent && (
                    <div style={{ marginTop: 20 }}>
                        <UICallout
                            id="derived_agents_configurations_override"
                            content="Derived agents inherit configurations from their parent agent (inherited configurations that are not overridden are not shown). You can override inherited properties, inputs, and outputs by specifying them here."
                        />
                    </div>
                )}
                <div style={{ marginTop: 20 }}>
                    <EntityProperties
                        isEditing={isEditing}
                        updateEntity={updateAgent}
                        entity={editedAgent}
                        loading={loading}
                    />
                </div>
                <div style={{ marginTop: 20 }} className="split-pane-container">
                    <div className="pane-item">
                        <div style={{ marginBottom: 10 }}>
                            <EntityTitle
                                icon={
                                    <FAIcon
                                        icon={ENTITY_TYPE_LOOKUP["input"].icon}
                                        size={25}
                                    />
                                }
                                heading={H3}
                                title="Inputs"
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
                                list={_.values(
                                    _.get(agent, "contents.input", {})
                                )}
                            />
                            {!isEditing && canEditEntity && (
                                <Button
                                    disabled={loading}
                                    variant={ButtonVariant.MINIMAL}
                                    icon={<FAIcon icon={faPlus} />}
                                    fill
                                    text="Add input"
                                    onClick={() => {
                                        setShowNewEntity(true);
                                        setNewEntityType("input");
                                    }}
                                />
                            )}
                        </div>
                    </div>
                    <div className="pane-item">
                        <div style={{ marginBottom: 10 }}>
                            <EntityTitle
                                icon={
                                    <FAIcon
                                        icon={ENTITY_TYPE_LOOKUP["output"].icon}
                                        size={25}
                                    />
                                }
                                heading={H3}
                                title="Outputs"
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
                                list={_.values(
                                    _.get(agent, "contents.output", {})
                                )}
                            />
                            {!isEditing && canEditEntity && (
                                <Button
                                    disabled={loading}
                                    variant={ButtonVariant.MINIMAL}
                                    icon={<FAIcon icon={faPlus} />}
                                    fill
                                    text="Add output"
                                    onClick={() => {
                                        setShowNewEntity(true);
                                        setNewEntityType("output");
                                    }}
                                />
                            )}
                        </div>
                    </div>
                </div>
                <div style={{ marginTop: 20 }}>
                    <div style={{ marginBottom: 10 }}>
                        <EntityTitle
                            icon={
                                <FAIcon
                                    icon={ENTITY_TYPE_LOOKUP["agent"].icon}
                                    size={25}
                                />
                            }
                            heading={H3}
                            title="Derived Agents"
                        />
                    </div>
                    <div className="responsive-grid-container">
                        <Leaves
                            isEditing={isEditing}
                            loading={loading}
                            addCrumb={addCrumb}
                            list={_.values(_.get(agent, "contents.agent", {}))}
                        />
                        {!isEditing && canEditEntity && (
                            <Button
                                disabled={loading}
                                variant={ButtonVariant.MINIMAL}
                                icon={<FAIcon icon={faPlus} />}
                                fill
                                text="Add derived agent"
                                onClick={() => {
                                    setShowNewEntity(true);
                                    setNewEntityType("agent");
                                }}
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
