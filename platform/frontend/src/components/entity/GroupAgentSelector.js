import { faIcon } from "@/components/icon";
import {
    Button,
    Card,
    Classes,
    ControlGroup,
    Dialog,
    DialogBody,
    Divider,
    Intent,
    Tree,
} from "@blueprintjs/core";
import {
    faArrowLeft,
    faArrowRight,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { axiosErrorToast, settlePromises } from "../helper";
import EntityIcon from "./EntityIcon";
import GroupAgentSelectorCheck from "./GroupAgentSelectorCheck";
const interleave = (list, element) =>
        list.flatMap((e) => [e, element]).slice(0, -1),
    TREE_CARD_STYLE = {
        width: "calc((100% - 96.53px) / 2)",
        padding: "5px 0px",
        height: 300,
        overflow: "auto",
    },
    agentRegistryName = process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME;
export default function GroupAgentSelector({
    isOpen,
    setIsGroupAgentSelectorDialogOpen,
    fetchAgentGroup,
    entity,
}) {
    const [availableAgentTreeNodes, setAvailableAgentTreeNodes] = useState([]);
    const [addedAgents, setAddedAgents] = useState([]);
    const [addedAgentTreeNodes, setAddedAgentTreeNodes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingAvailableAgentsTree, setLoadingAvailableAgentsTree] =
        useState(false);
    const [addingAgent, setAddingAgent] = useState(false);
    const [removingAgent, setRemovingAgent] = useState(false);
    const { appState, appActions } = useContext(AppContext);
    const { agentGroupSelection } = appState.agent;
    const [edited, setEdited] = useState(false);
    const constructTree = (agent, prevPath, type) => {
        const contents = _.values(_.get(agent, "contents", {})).filter(
                (content) => _.isEqual(_.get(content, "type", null), "agent")
            ),
            path = `${prevPath}${_.isEmpty(prevPath) ? "" : "."}${agent.name}`;

        let icon = _.get(agent, "icon", null);
        if (!_.isEmpty(icon) && !_.startsWith(icon, "data:image/")) {
            icon = _.split(icon, ":");
        }
        let node = {
            id: path,
            icon: <EntityIcon entity={{ icon, type: "agent" }} />,
            agentName: agent.name,
            label: (
                <div
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{ paddingLeft: 8 }}
                >
                    {_.get(agent, "properties.display_name", agent.name)}
                </div>
            ),
            childNodes: [],
            secondaryLabel: (
                <GroupAgentSelectorCheck agent={agent.name} type={type} />
            ),
        };
        for (let i = 0; i < _.size(contents); i++) {
            node.childNodes.push(constructTree(contents[i], path, type));
        }
        if (_.isEmpty(node.childNodes)) {
            _.set(node, "hasCaret", false);
        }
        return node;
    };
    const onNodeExpandAvailable = (node, nodePath) => {
            let nodes = _.cloneDeep(availableAgentTreeNodes);
            _.set(
                nodes,
                [...interleave(nodePath, "childNodes"), "isExpanded"],
                true
            );
            setAvailableAgentTreeNodes(nodes);
        },
        onNodeCollapseAvailable = (node, nodePath) => {
            let nodes = _.cloneDeep(availableAgentTreeNodes);
            _.set(
                nodes,
                [...interleave(nodePath, "childNodes"), "isExpanded"],
                false
            );
            setAvailableAgentTreeNodes(nodes);
        },
        onNodeClickAvailable = (node) => {
            appActions.agent.updateAgentGroupSelection({
                name: node.agentName,
                type: "available",
                value: !_.get(
                    agentGroupSelection,
                    ["available", node.agentName],
                    false
                ),
            });
        },
        onNodeExpandAdded = (node, nodePath) => {
            let nodes = _.cloneDeep(addedAgentTreeNodes);
            _.set(
                nodes,
                [...interleave(nodePath, "childNodes"), "isExpanded"],
                true
            );
            setAddedAgentTreeNodes(nodes);
        },
        onNodeCollapseAdded = (node, nodePath) => {
            let nodes = _.cloneDeep(addedAgentTreeNodes);
            _.set(
                nodes,
                [...interleave(nodePath, "childNodes"), "isExpanded"],
                false
            );
            setAddedAgentTreeNodes(nodes);
        },
        onNodeClickAdded = (node) => {
            appActions.agent.updateAgentGroupSelection({
                name: node.agentName,
                type: "added",
                value: !_.get(
                    agentGroupSelection,
                    ["added", node.agentName],
                    false
                ),
            });
        };
    const agentsToRemove = _.keys(agentGroupSelection.added).filter(
        (key) => agentGroupSelection.added[key]
    );
    const onRemoveSelectedAgents = () => {
        let tasks = [];
        for (let i = 0; i < _.size(agentsToRemove); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(
                            `/registry/${agentRegistryName}/agent_group/${entity.name}/agent/${agentsToRemove[i]}`,
                            { name: entity.name, description: "" }
                        )
                        .then(() => resolve(true))
                        .catch((error) => {
                            axiosErrorToast(error);
                            reject(false);
                        });
                })
            );
        }
        setLoading(true);
        setRemovingAgent(true);
        settlePromises(tasks, ({ results }) => {
            let newAddedAgents = _.cloneDeep(addedAgents);
            for (let i = 0; i < _.size(results); i++) {
                if (_.isEqual(results[i].status, "fulfilled")) {
                    setEdited(true);
                    appActions.agent.updateAgentGroupSelection({
                        name: agentsToRemove[i],
                        type: "added",
                        value: false,
                    });
                    _.pullAllBy(
                        newAddedAgents,
                        [{ name: agentsToRemove[i] }],
                        "name"
                    );
                }
            }
            setAddedAgents(newAddedAgents);
            setRemovingAgent(false);
            setLoading(false);
        });
    };
    const agentsToAdd = _.keys(agentGroupSelection.available).filter(
        (key) => agentGroupSelection.available[key]
    );
    const onAddSelectedAgents = () => {
        let tasks = [];
        for (let i = 0; i < _.size(agentsToAdd); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    axios
                        .post(
                            `/registry/${agentRegistryName}/agent_group/${entity.name}/agent/${agentsToAdd[i]}`,
                            { name: entity.name, description: "" }
                        )
                        .then(() => resolve(true))
                        .catch((error) => {
                            axiosErrorToast(error);
                            reject(error.response.status);
                        });
                })
            );
        }
        setLoading(true);
        setAddingAgent(true);
        settlePromises(tasks, ({ results }) => {
            let newAddedAgents = _.cloneDeep(addedAgents);
            for (let i = 0; i < _.size(results); i++) {
                if (_.isEqual(results[i].status, "fulfilled")) {
                    setEdited(true);
                    appActions.agent.updateAgentGroupSelection({
                        name: agentsToAdd[i],
                        type: "available",
                        value: false,
                    });
                    newAddedAgents.push({
                        name: agentsToAdd[i],
                        type: "agent",
                    });
                }
            }
            setAddedAgents(_.uniqBy(newAddedAgents, "name"));
            setAddingAgent(false);
            setLoading(false);
        });
    };
    const onDeselectAll = () => appActions.agent.clearAgentGroupSelection();
    useEffect(() => {
        let tree = [];
        for (let i = 0; i < _.size(addedAgents); i++) {
            tree.push(constructTree(addedAgents[i], "", "added"));
        }
        setAddedAgentTreeNodes(tree);
    }, [addedAgents]);
    useEffect(() => {
        setAddedAgents(
            _.values(_.get(entity, "contents", {})).filter((content) =>
                _.isEqual(_.get(content, "type", null), "agent")
            )
        );
    }, [entity.contents]);
    const constructAvailableAgentsTree = () => {
        setLoading(true);
        setLoadingAvailableAgentsTree(true);
        axios.get(`/registry/${agentRegistryName}/agents`).then((response) => {
            const result = _.get(response, "data.results", []);
            let tree = [];
            for (let i = 0; i < _.size(result); i++) {
                tree.push(constructTree(result[i], "", "available"));
            }
            setAvailableAgentTreeNodes(tree);
            setLoading(false);
            setLoadingAvailableAgentsTree(false);
        });
    };
    useEffect(() => {
        if (isOpen) constructAvailableAgentsTree();
    }, [isOpen]);
    return (
        <Dialog
            isOpen={isOpen}
            onClose={() => {
                if (edited) fetchAgentGroup();
                setEdited(false);
                onDeselectAll();
                setIsGroupAgentSelectorDialogOpen(false);
            }}
            title="Agents"
            style={{ width: 900 }}
        >
            <DialogBody>
                <div style={{ display: "flex", gap: 15, alignItems: "center" }}>
                    <Card
                        className={
                            loadingAvailableAgentsTree ? Classes.SKELETON : null
                        }
                        style={TREE_CARD_STYLE}
                    >
                        <Tree
                            onNodeExpand={onNodeExpandAvailable}
                            onNodeCollapse={onNodeCollapseAvailable}
                            onNodeClick={onNodeClickAvailable}
                            contents={availableAgentTreeNodes}
                        />
                    </Card>
                    <div style={{ width: 96.53 }}>
                        <ControlGroup vertical>
                            <Button
                                intent={Intent.SUCCESS}
                                outlined
                                text="Add"
                                loading={addingAgent}
                                disabled={loading || _.isEmpty(agentsToAdd)}
                                onClick={onAddSelectedAgents}
                                rightIcon={faIcon({
                                    icon: faArrowRight,
                                })}
                            />
                            <Divider style={{ opacity: 0 }} />
                            <Button
                                minimal
                                text="Deselect all"
                                onClick={onDeselectAll}
                            />
                            <Divider style={{ opacity: 0 }} />
                            <Button
                                intent={Intent.DANGER}
                                outlined
                                loading={removingAgent}
                                disabled={loading || _.isEmpty(agentsToRemove)}
                                onClick={onRemoveSelectedAgents}
                                text="Remove"
                                icon={faIcon({ icon: faArrowLeft })}
                            />
                        </ControlGroup>
                    </div>
                    <Card style={TREE_CARD_STYLE}>
                        <Tree
                            onNodeExpand={onNodeExpandAdded}
                            onNodeCollapse={onNodeCollapseAdded}
                            onNodeClick={onNodeClickAdded}
                            contents={addedAgentTreeNodes}
                        />
                    </Card>
                </div>
            </DialogBody>
        </Dialog>
    );
}
