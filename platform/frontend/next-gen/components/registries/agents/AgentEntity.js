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
import { faCheckCircle } from "@fortawesome/sharp-duotone-solid-svg-icons";
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
import AgentMainProperties from "./AgentMainProperties";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function AgentEntity({ entity, addCrumb }) {
    const { name, scope, type } = entity;
    const [agent, setAgent] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedAgent, setEditedAgent] = useState(null);
    const [mainProperties, setMainProperties] = useState({});
    const [loading, setLoading] = useState(false);
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
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/${path}`;
    const getMainProperties = (properties) => {
        let next = _.cloneDeep(properties);
        _.set(
            next,
            "listens",
            _.entries(_.get(next, "listens", {})).map((listen) => ({
                key: listen[0],
                includes: _.get(listen, "1.includes", []),
                excludes: _.get(listen, "1.excludes", []),
            }))
        );
        _.set(
            next,
            "tags",
            _.entries(_.get(next, "tags", {})).map((tag) => ({
                key: tag[0],
                tags: _.get(tag, "1", []),
            }))
        );
        return next;
    };
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                if (_.isEmpty(result)) {
                    setAgent(null);
                    setEditedAgent(null);
                } else {
                    setAgent(result);
                    setEditedAgent(result);
                    const properties = _.pick(
                        _.get(result, "properties", {}),
                        ENTITY_MAIN_INFO_PROPERTY_KEYS
                    );
                    setMainProperties(getMainProperties(properties));
                }
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity]);
    const handleDiscard = () => {
        setEditedAgent(agent);
        const properties = _.pick(
            _.get(agent, "properties", {}),
            ENTITY_MAIN_INFO_PROPERTY_KEYS
        );
        setMainProperties(getMainProperties(properties));
        setIsEditing(false);
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
                        setMainProperties(getMainProperties(properties));
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
                <div>
                    <AgentMainProperties
                        updateMainProperties={updateMainProperties}
                        isEditing={isEditing}
                        properties={mainProperties}
                        loading={loading}
                    />
                </div>
                <div style={{ marginTop: 20 }}>
                    <EntityDescription
                        isEditing={isEditing}
                        updateEntity={updateAgent}
                        entity={editedAgent}
                        loading={loading}
                    />
                </div>
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
                                loading={loading}
                                addCrumb={addCrumb}
                                list={_.values(
                                    _.get(agent, "contents.input", {})
                                )}
                            />
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
                                loading={loading}
                                addCrumb={addCrumb}
                                list={_.values(
                                    _.get(agent, "contents.output", {})
                                )}
                            />
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
                            loading={loading}
                            addCrumb={addCrumb}
                            list={_.values(_.get(agent, "contents.agent", {}))}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
