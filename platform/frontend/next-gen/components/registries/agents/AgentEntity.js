import {
    ENTITY_MAIN_INFO_PROPERTY_KEYS,
    HEX_TRANSPARENCY,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { getUpdatePropertyPromises, settlePromises } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors, EditableText } from "@blueprintjs/core";
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
import RegistryEntityIcon from "../RegistryEntityIcon";
import AgentMainProperties from "./AgentMainProperties";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
const MAIN_INFO_STYLES = {
    height: 40,
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    maxWidth: "100%",
};
function MAIN_INFO_BLOCK({ loading, label, children }) {
    return (
        <div style={MAIN_INFO_STYLES}>
            <div
                className={classNames(
                    Classes.TEXT_MUTED,
                    Classes.TEXT_OVERFLOW_ELLIPSIS
                )}
            >
                {label}
            </div>
            <div
                className={loading ? Classes.SKELETON : null}
                style={{ fontWeight: 600 }}
            >
                {children}
            </div>
        </div>
    );
}
export default function AgentEntity({ name }) {
    const [agent, setAgent] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedAgent, setEditedAgent] = useState(null);
    const [mainProperties, setMainProperties] = useState(null);
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
    const darkMode = useAppStore((state) => state.darkMode);
    const systemAgent = _.get(mainProperties, "system_agent", false);
    const displayName = _.get(mainProperties, "display_name", "");
    const image = _.get(mainProperties, "image", "");
    const url = `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${name}`;
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
    }, [name]);
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
                const tasks = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(tasks, ({ error }) => {
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
                    <MAIN_INFO_BLOCK loading={loading} label="System agent">
                        {systemAgent ? (
                            <FAIcon
                                style={{ color: Colors.GREEN3 }}
                                icon={faCheckCircle}
                            />
                        ) : (
                            "-"
                        )}
                    </MAIN_INFO_BLOCK>
                    <MAIN_INFO_BLOCK loading={loading} label="Display name">
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
                    </MAIN_INFO_BLOCK>
                    <MAIN_INFO_BLOCK loading={loading} label="Docker image">
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
                    </MAIN_INFO_BLOCK>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
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
        </div>
    );
}
