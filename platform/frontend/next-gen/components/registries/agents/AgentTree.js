import { GREEN_CHECK } from "@/components/constants";
import { useToaster } from "@/components/contexts/ToasterContext";
import { FAIcon } from "@/components/FAIcon";
import {
    constructAgentTree,
    insertBetween,
    settlePromises,
} from "@/components/helper";
import {
    Button,
    ButtonVariant,
    Card,
    Classes,
    ControlGroup,
    H3,
    Intent,
    Size,
    Tree,
} from "@blueprintjs/core";
import {
    faArrowLeft,
    faArrowRight,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import EntityDisplayName from "../EntityDisplayName";
import RegistryEntityIcon from "../RegistryEntityIcon";
const TREE_CARD_STYLE = {
    width: "calc((100% - 125px) / 2)",
    padding: 0,
    height: "100%",
    overflow: "auto",
};
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function AgentTree({ entity }) {
    const [agentGroup, setAgentGroup] = useState(null);
    const [available, setAvailable] = useState([]);
    const [added, setAdded] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedAvailable, setSelectedAvailable] = useState(new Set());
    const [selectedAdded, setSelectedAdded] = useState(new Set());
    const onDeselectAvailable = (agents) => {
        let newSelected = _.cloneDeep(selectedAvailable);
        let availableNodes = _.cloneDeep(available);
        function removeSecondaryLabel(nodes) {
            for (let i = 0; i < _.size(nodes); i++) {
                const node = nodes[i];
                if (_.includes(agents, node.id)) {
                    node.secondaryLabel = null;
                }
                if (!_.isEmpty(node.childNodes)) {
                    removeSecondaryLabel(node.childNodes);
                }
            }
            return nodes;
        }
        setAvailable(removeSecondaryLabel(availableNodes));
        for (let i = 0; i < _.size(agents); i++) {
            newSelected.delete(agents[i]);
        }
        setSelectedAvailable(newSelected);
    };
    const { progressToaster, showAxiosErrorToast } = useToaster();
    const onDeselectAdded = (agents) => {
        let newSelected = _.cloneDeep(selectedAdded);
        let addedNodes = _.cloneDeep(added);
        function removeSecondaryLabel(nodes) {
            for (let i = 0; i < _.size(nodes); i++) {
                const node = nodes[i];
                if (_.includes(agents, node.id)) {
                    node.secondaryLabel = null;
                }
                if (!_.isEmpty(node.childNodes)) {
                    removeSecondaryLabel(node.childNodes);
                }
            }
            return nodes;
        }
        setAdded(removeSecondaryLabel(addedNodes));
        for (let i = 0; i < _.size(agents); i++) {
            newSelected.delete(agents[i]);
        }
        setSelectedAdded(newSelected);
    };
    const onDeselectAll = () => {
        let availableNodes = _.cloneDeep(available);
        function removeSecondaryLabel(nodes) {
            for (let i = 0; i < _.size(nodes); i++) {
                const node = nodes[i];
                node.secondaryLabel = null;
                if (!_.isEmpty(node.childNodes)) {
                    removeSecondaryLabel(node.childNodes);
                }
            }
            return nodes;
        }
        setAvailable(removeSecondaryLabel(availableNodes));
        let addedNodes = _.cloneDeep(added);
        setAdded(removeSecondaryLabel(addedNodes));
    };
    useEffect(() => {
        const current = _.values(_.get(agentGroup, "contents.agent", {}));
        let tree = [];
        for (let i = 0; i < _.size(current); i++) {
            tree.push(constructAgentTree(current[i]));
        }
        setAdded(tree);
    }, [agentGroup]);
    useEffect(() => {
        setLoading(true);
        Promise.allSettled([
            axios
                .get(
                    `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_group/${entity.name}`
                )
                .then((response) => {
                    setAgentGroup(_.get(response, "data.result", null));
                }),
            axios
                .get(`/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agents`)
                .then((response) => {
                    const result = _.get(response, "data.results", []);
                    let tree = [];
                    for (let i = 0; i < _.size(result); i++) {
                        tree.push(constructAgentTree(result[i]));
                    }
                    setAvailable(tree);
                }),
        ]).then(() => {
            setLoading(false);
        });
    }, []);
    const onAvailableNodeClick = (node, nodePath) => {
        let selected = _.cloneDeep(selectedAvailable);
        let nodes = _.cloneDeep(available);
        const agent = node.agent.name;
        if (selected.has(agent)) {
            selected.delete(agent);
            _.set(
                nodes,
                [...insertBetween(nodePath, "childNodes"), "secondaryLabel"],
                null
            );
        } else {
            selected.add(agent);
            _.set(
                nodes,
                [...insertBetween(nodePath, "childNodes"), "secondaryLabel"],
                GREEN_CHECK
            );
        }
        setSelectedAvailable(selected);
        setAvailable(nodes);
    };
    const onAvailableNodeCollapse = (node, nodePath) => {
        let nodes = _.cloneDeep(available);
        _.set(
            nodes,
            [...insertBetween(nodePath, "childNodes"), "isExpanded"],
            false
        );
        setAvailable(nodes);
    };
    const onAvailableNodeExpand = (node, nodePath) => {
        let nodes = _.cloneDeep(available);
        _.set(
            nodes,
            [...insertBetween(nodePath, "childNodes"), "isExpanded"],
            true
        );
        setAvailable(nodes);
    };
    const onAddedNodeClick = (node, nodePath) => {
        let selected = _.cloneDeep(selectedAdded);
        let nodes = _.cloneDeep(added);
        const agent = node.agent.name;
        if (selected.has(agent)) {
            selected.delete(agent);
            _.set(
                nodes,
                [...insertBetween(nodePath, "childNodes"), "secondaryLabel"],
                null
            );
        } else {
            selected.add(agent);
            _.set(
                nodes,
                [...insertBetween(nodePath, "childNodes"), "secondaryLabel"],
                GREEN_CHECK
            );
        }
        setSelectedAdded(selected);
        setAdded(nodes);
    };
    const onAddedNodeExpand = (node, nodePath) => {
        let nodes = _.cloneDeep(added);
        _.set(
            nodes,
            [...insertBetween(nodePath, "childNodes"), "isExpanded"],
            true
        );
        setAdded(nodes);
    };
    const onAddedNodeCollapse = (node, nodePath) => {
        let nodes = _.cloneDeep(added);
        _.set(
            nodes,
            [...insertBetween(nodePath, "childNodes"), "isExpanded"],
            false
        );
        setAdded(nodes);
    };
    const onAddSelected = () => {
        setLoading(true);
        let promises = [];
        const selected = _.toArray(selectedAvailable);
        for (let i = 0; i < _.size(selected); i++) {
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .post(
                            `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_group/${entity.name}/agent/${selected[i]}`,
                            { name: selected[i], description: "" }
                        )
                        .then(() => {
                            resolve(selected[i]);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(selected[i]);
                        });
                })
            );
        }
        settlePromises(
            promises,
            ({ results }) => {
                let newAdded = _.cloneDeep(added);
                let result = [];
                for (let i = 0; i < _.size(results); i++) {
                    if (_.isEqual(results[i].status, "fulfilled")) {
                        const agent = { name: results[i].value };
                        result.push(agent.name);
                        newAdded.push({
                            id: agent.name,
                            icon: (
                                <RegistryEntityIcon
                                    maxSize={20}
                                    type={"agent"}
                                    content={_.get(agent, "icon", null)}
                                />
                            ),
                            agent,
                            label: (
                                <div
                                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                                    style={{ marginLeft: 7 }}
                                >
                                    <EntityDisplayName entity={agent} />
                                </div>
                            ),
                            childNodes: [],
                            hasCaret: false,
                        });
                    }
                }
                onDeselectAvailable(result);
                setAdded(newAdded);
                setLoading(false);
            },
            progressToaster
        );
    };
    const onRemoveSelected = () => {
        setLoading(true);
        let promises = [];
        const selected = _.toArray(selectedAdded);
        for (let i = 0; i < _.size(selected); i++) {
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(
                            `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_group/${entity.name}/agent/${selected[i]}`
                        )
                        .then(() => {
                            resolve(selected[i]);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(selected[i]);
                        });
                })
            );
        }
        settlePromises(
            promises,
            ({ results }) => {
                let newAdded = _.cloneDeep(added);
                let result = [];
                for (let i = 0; i < _.size(results); i++) {
                    if (_.isEqual(results[i].status, "fulfilled")) {
                        result.push(results[i].value);
                        _.pullAllBy(newAdded, [{ id: results[i].value }], "id");
                    }
                }
                onDeselectAdded(result);
                setAdded(newAdded);
                setLoading(false);
            },
            progressToaster
        );
    };
    return (
        <div className="full-parent-dimension">
            <H3 style={{ marginBottom: 20 }}>Agents</H3>
            <div
                className="full-parent-dimension"
                style={{
                    display: "flex",
                    gap: 20,
                    alignItems: "center",
                    height: "calc(100% - 45px)",
                }}
            >
                <Card style={TREE_CARD_STYLE}>
                    <Tree
                        contents={available}
                        onNodeExpand={onAvailableNodeExpand}
                        onNodeCollapse={onAvailableNodeCollapse}
                        onNodeClick={onAvailableNodeClick}
                    />
                </Card>
                <ControlGroup vertical style={{ width: 125 }}>
                    <Button
                        disabled={_.isEmpty(selectedAvailable)}
                        size={Size.LARGE}
                        intent={Intent.SUCCESS}
                        text="Add"
                        endIcon={<FAIcon icon={faArrowRight} />}
                        variant={ButtonVariant.OUTLINED}
                        onClick={onAddSelected}
                    />
                    <Button
                        size={Size.LARGE}
                        text="Deselect all"
                        variant={ButtonVariant.MINIMAL}
                        onClick={onDeselectAll}
                    />
                    <Button
                        disabled={_.isEmpty(selectedAdded)}
                        size={Size.LARGE}
                        intent={Intent.DANGER}
                        text="Remove"
                        icon={<FAIcon icon={faArrowLeft} />}
                        variant={ButtonVariant.OUTLINED}
                        onClick={onRemoveSelected}
                    />
                </ControlGroup>
                <Card style={TREE_CARD_STYLE}>
                    <Tree
                        contents={added}
                        onNodeExpand={onAddedNodeExpand}
                        onNodeCollapse={onAddedNodeCollapse}
                        onNodeClick={onAddedNodeClick}
                    />
                </Card>
            </div>
        </div>
    );
}
