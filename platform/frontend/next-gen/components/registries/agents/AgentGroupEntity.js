import {
    ENTITY_TYPE_LOOKUP,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useContainerContext } from "@/components/contexts/ContainerContext";
import { FAIcon } from "@/components/FAIcon";
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
    EntityTitle,
    H3,
} from "@blueprintjs/core";
import { faFolderTree } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import EntityDescription from "../attributes/EntityDescription";
import EntityActions from "../EntityActions";
import EntityDisplayName from "../EntityDisplayName";
import Leaves from "../Leaves";
import RegistryEntityContainer from "../RegistryEntityContainer";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function AgentGroupEntity({
    entity,
    addCrumb,
    setShowIconEditor,
    icon,
    setIcon,
    backCrumb,
    setShowAgentTree,
    breaker,
}) {
    const { name, type } = entity;
    const { containerId } = useContainerContext();
    const setContainerHeader = useGridStore(
        (state) => state.setContainerHeader
    );
    const [agentGroup, setAgentGroup] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedAgentGroup, setEditedAgentGroup] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
    const [template, setTemplate] = useState(null);
    const addContainer = useGridStore((state) => state.addContainer);
    const updateMainProperties = ({ path, value }) => {
        let newProperties = _.cloneDeep(mainProperties);
        _.set(newProperties, path, value);
        setMainProperties(newProperties);
    };
    const updateAgentGroup = ({ path, value }) => {
        let newAgentGroup = _.cloneDeep(editedAgentGroup);
        _.set(newAgentGroup, path, value);
        setEditedAgentGroup(newAgentGroup);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const displayName = _.get(mainProperties, "display_name", "");
    const url = `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/${type}/${name}`;
    useEffect(() => {
        setContainerHeader({
            id: containerId,
            title: <EntityDisplayName entity={agentGroup} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [agentGroup]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setAgentGroup(result);
                setEditedAgentGroup(result);
                setTemplate(result);
                setIcon(_.get(result, "icon", null));
                setMainProperties(
                    getEntityMainProperties(_.get(result, "properties", {}))
                );
            })
            .finally(() => {
                setLoading(false);
                if (!_.isNull(breaker)) {
                    breaker.current = true;
                }
            });
    }, [entity, breaker.current]);
    useEffect(() => {
        updateAgentGroup({ path: "icon", value: icon });
    }, [icon]);
    const handleDiscard = () => {
        setEditedAgentGroup(agentGroup);
        setMainProperties(
            getEntityMainProperties(_.get(agentGroup, "properties", {}))
        );
        setIsEditing(false);
        setIcon(_.get(agentGroup, "icon", null));
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name,
                description: editedAgentGroup.description,
                icon: editedAgentGroup.icon,
            })
            .then(() => {
                let updated = _.cloneDeep(mainProperties);
                if (_.has(mainProperties, "listens")) {
                    let result = {};
                    for (let i = 0; i < _.size(mainProperties.listens); i++) {
                        const key = _.trim(mainProperties.listens[i].key);
                        if (!_.isEmpty(key)) {
                            _.set(result, mainProperties.listens[i].key, {
                                includes: _.get(
                                    mainProperties.listens,
                                    [i, "includes"],
                                    []
                                ),
                                excludes: _.get(
                                    mainProperties.listens,
                                    [i, "excludes"],
                                    []
                                ),
                            });
                        }
                    }
                    _.set(updated, "listens", result);
                }
                if (_.has(mainProperties, "tags")) {
                    let result = {};
                    for (let i = 0; i < _.size(mainProperties.tags); i++) {
                        const key = _.trim(mainProperties.tags[i].key);
                        if (!_.isEmpty(key)) {
                            _.set(
                                result,
                                mainProperties.tags[i].key,
                                _.get(mainProperties.tags, [i, "tags"], [])
                            );
                        }
                    }
                    _.set(updated, "tags", result);
                }
                const properties = {
                    ...editedAgentGroup.properties,
                    ...updated,
                };
                const diffs = shallowDiff(agentGroup.properties, properties);
                const promises = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(promises, ({ error }) => {
                    if (!error) {
                        const newAgentGroup = {
                            ...editedAgentGroup,
                            properties,
                        };
                        setEditedAgentGroup(newAgentGroup);
                        setAgentGroup(newAgentGroup);
                        setTemplate(newAgentGroup);
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
                {!_.isEmpty(agentGroup) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={agentGroup}
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
                        content={_.get(editedAgentGroup, "icon", null)}
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
                        <div>{_.get(editedAgentGroup, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedAgentGroup, "name")}
                        </div>
                    </div>
                    {/* <MainPropertyBlock loading={loading} label="Display name">
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
                    </MainPropertyBlock> */}
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <div style={{ marginTop: 20 }}>
                    <EntityDescription
                        isEditing={isEditing}
                        updateEntity={updateAgentGroup}
                        entity={editedAgentGroup}
                        loading={loading}
                    />
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
                        title="Agents"
                    />
                </div>
                <div className="responsive-grid-container">
                    <Leaves
                        loading={loading}
                        addCrumb={addCrumb}
                        list={_.values(_.get(agentGroup, "contents.agent", {}))}
                    />
                    {!isEditing && (
                        <Button
                            disabled={loading}
                            variant={ButtonVariant.MINIMAL}
                            icon={<FAIcon icon={faFolderTree} />}
                            fill
                            text="Update agents"
                            onClick={() => {
                                setShowAgentTree(true);
                            }}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
