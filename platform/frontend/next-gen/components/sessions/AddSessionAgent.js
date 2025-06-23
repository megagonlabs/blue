import { GREEN_CHECK } from "@/components/constants";
import { constructAgentTree, insertBetween } from "@/components/helper";
import { Button, Card, H3, Intent, Size, Tag, Tree } from "@blueprintjs/core";
import {
    faCheck,
    faForward,
    faGrid2Plus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import { FAIcon } from "../FAIcon";
import { showAxiosErrorToast } from "../helper";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function AddSessionAgent({
    skippable = false,
    sessionId,
    setSkippable,
    setShowAddSessionAgent,
}) {
    const [available, setAvailable] = useState([]);
    const [unavailable, setUnavailable] = useState(0);
    const [loading, setLoading] = useState(false);
    const [selectedAvailable, setSelectedAvailable] = useState(new Set());
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agents`)
            .then((response) => {
                const result = _.get(response, "data.results", []);
                let tree = [],
                    notRunning = 0;
                for (let i = 0; i < _.size(result); i++) {
                    const containerStatus = _.get(
                        result,
                        [i, "container", "status"],
                        null
                    );
                    if (_.isEqual(containerStatus, "running")) {
                        tree.push(constructAgentTree(result[i]));
                    } else {
                        notRunning += 1;
                    }
                }
                setAvailable(tree);
                setUnavailable(notRunning);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);
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
    const handleAddSessionAgent = () => {
        setLoading(true);
        let promises = [];
        const agents = Array.from(selectedAvailable);
        for (let i = 0; i < _.size(agents); i++) {
            const agent = agents[i];
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .post(`/sessions/session/${sessionId}/agent/${agent}`, {
                            properties: {},
                        })
                        .then(() => {
                            resolve(agent);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(agent);
                        });
                })
            );
        }
        Promise.allSettled(promises).then((results) => {
            let next = _.cloneDeep(selectedAvailable);
            let added = new Set();
            for (let i = 0; i < _.size(results); i++) {
                if (_.isEqual(results[i].status, "fulfilled")) {
                    next.delete(results[i].value);
                    added.add(results[i].value);
                }
            }
            setSelectedAvailable(next);
            function removeSecondaryLabel(nodes, addedAgents) {
                for (let i = 0; i < _.size(nodes); i++) {
                    const node = nodes[i];
                    if (addedAgents.has(node.agent.name)) {
                        node.secondaryLabel = null;
                    }
                    if (!_.isEmpty(node.childNodes)) {
                        removeSecondaryLabel(node.childNodes, addedAgents);
                    }
                }
                return nodes;
            }
            let newAvailable = _.cloneDeep(available);
            setAvailable(removeSecondaryLabel(newAvailable, added));
            setLoading(false);
        });
    };
    return (
        <div className="full-parent-dimension">
            <H3 style={{ marginBottom: 20 }}>Agents</H3>
            <Card
                className="full-parent-dimension"
                style={{
                    padding: 0,
                    overflow: "auto",
                    maxHeight: "calc(100% - 105px)",
                }}
            >
                <Tree
                    contents={available}
                    onNodeExpand={onAvailableNodeExpand}
                    onNodeCollapse={onAvailableNodeCollapse}
                    onNodeClick={onAvailableNodeClick}
                />
            </Card>
            <div
                style={{ marginTop: 20, display: "flex", alignItems: "center" }}
            >
                <Button
                    loading={loading}
                    intent={
                        _.isEmpty(selectedAvailable)
                            ? Intent.SUCCESS
                            : Intent.PRIMARY
                    }
                    text={
                        _.isEmpty(selectedAvailable)
                            ? skippable
                                ? "Skip"
                                : "Done"
                            : "Add"
                    }
                    icon={
                        <FAIcon
                            icon={
                                _.isEmpty(selectedAvailable)
                                    ? skippable
                                        ? faForward
                                        : faCheck
                                    : faGrid2Plus
                            }
                        />
                    }
                    size={Size.LARGE}
                    onClick={() => {
                        if (_.isEmpty(selectedAvailable)) {
                            setSkippable(false);
                            setShowAddSessionAgent(false);
                        } else {
                            handleAddSessionAgent();
                        }
                    }}
                />
                {!_.isEmpty(selectedAvailable) && (
                    <span style={{ marginLeft: 15 }}>
                        {_.size(selectedAvailable)} selected
                    </span>
                )}
                {unavailable > 0 && (
                    <div
                        style={{ position: "absolute", right: 20, bottom: 25 }}
                    >
                        <Tag minimal size={Size.LARGE} intent={Intent.WARNING}>
                            {unavailable} unavailable
                        </Tag>
                    </div>
                )}
            </div>
        </div>
    );
}
