import { EMPTY_OBJECT, MIN_ALLOTMENT_PANE_SIZE } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { insertBetween, showAxiosErrorToast } from "@/components/helper";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import Timestamp from "@/components/Timestamp";
import { useAppStore } from "@/stores/app-store";
import { useSessionStore } from "@/stores/session-store";
import { useSocketStore } from "@/stores/socket-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    HTMLTable,
    Intent,
    Size,
    Tag,
    Tooltip,
    Tree,
} from "@blueprintjs/core";
import {
    faCircleA,
    faDiagramSuccessor,
    faFolder,
    faFolderOpen,
    faFolderTree,
    faList,
    faMessages,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { ReactFlowProvider } from "@xyflow/react";
import { Allotment } from "allotment";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useMemo, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { useShallow } from "zustand/react/shallow";
import AgentLogs from "../../platforms/AgentLogs";
import SessionAgents from "../details/SessionAgents";
import MessageViewer from "./MessageViewer";
import StreamFlows from "./StreamFlows";
const FOLDER_CLOSED_ICON = (
    <FAIcon icon={faFolder} style={{ marginRight: 7 }} />
);
const FOLDER_OPEN_ICON = (
    <FAIcon icon={faFolderOpen} size={18} style={{ marginRight: 7 }} />
);
function parseRedisStreamKeysToTree(keys, previousTree = [], messageMap) {
    const newTree = [...previousTree]; // Start with a copy of the previous tree
    const newNodeMap = {}; // Map for new nodes based on their ID
    const previousNodeMap = {}; // Map for previous nodes for quick lookup
    // Create a map of the previous tree nodes for efficient lookup
    function mapPreviousTree(nodes) {
        nodes.forEach((node) => {
            previousNodeMap[node.id] = node;
            if (node.childNodes) {
                mapPreviousTree(node.childNodes);
            }
        });
    }
    mapPreviousTree(previousTree);
    for (let i = 0; i < _.size(keys); i++) {
        const parts = keys[i].split(":");
        let currentPath = "";
        let parentId = null;
        for (let j = 0; j < parts.length; j++) {
            const part = parts[j];
            const id = currentPath ? `${currentPath}:${part}` : part;
            const label = part;
            let existingNode = newNodeMap[id] || previousNodeMap[id];
            let isNewNode = false;
            if (!existingNode) {
                existingNode = {
                    id: id,
                    label: label,
                    childNodes: [],
                    icon: FOLDER_CLOSED_ICON,
                };
                newNodeMap[id] = existingNode;
                isNewNode = true;
            }
            if (_.includes(["STREAM"], part)) {
                _.set(
                    existingNode,
                    "secondaryLabel",
                    <Tag minimal intent={Intent.PRIMARY}>
                        {_.get(messageMap, [id, "contentType"], "-")}
                    </Tag>
                );
            }
            if (!_.isNull(parentId)) {
                const parentNode =
                    newNodeMap[parentId] || previousNodeMap[parentId];
                if (parentNode) {
                    parentNode.childNodes = parentNode.childNodes || [];
                }
                if (
                    !_.some(parentNode.childNodes, (child) =>
                        _.isEqual(child.id, id)
                    )
                ) {
                    parentNode.childNodes.push(existingNode);
                    parentNode.hasCaret = true;
                    parentNode.icon = parentNode.icon || FOLDER_CLOSED_ICON;
                }
            } else if (
                !_.some(newTree, (rootNode) => _.isEqual(rootNode.id, id))
            ) {
                newTree.push(existingNode);
            }
            currentPath = id;
            parentId = id;
            // Inherit properties from the previous tree if the node existed
            if (!isNewNode && previousNodeMap[id]) {
                existingNode.isExpanded = previousNodeMap[id].isExpanded;
                existingNode.secondaryLabel =
                    previousNodeMap[id].secondaryLabel;
                // Add other status-related properties you want to preserve here
            }
        }
        // Post-process the final node (leaf)
        if (newNodeMap[currentPath] || previousNodeMap[currentPath]) {
            const finalNode =
                newNodeMap[currentPath] || previousNodeMap[currentPath];
            if (
                finalNode &&
                !_.some(keys, (key) => key.startsWith(currentPath + ":"))
            ) {
                delete finalNode.childNodes;
                delete finalNode.hasCaret;
                delete finalNode.icon;
            }
        }
    }
    // Post-process new nodes to ensure folders have correct icons
    for (const nodeId in newNodeMap) {
        const node = newNodeMap[nodeId];
        if (node.childNodes && node.childNodes.length > 0) {
            node.icon = FOLDER_CLOSED_ICON;
            node.hasCaret = true;
        }
    }
    // Merge updates into the previous tree structure
    function mergeUpdates(newNodes, previousNodes) {
        const merged = [];
        const previousMap = {};
        previousNodes.forEach((node) => (previousMap[node.id] = node));
        newNodes.forEach((newNode) => {
            const existingNode = previousMap[newNode.id];
            if (existingNode) {
                merged.push({
                    ...existingNode,
                    label: newNode.label, // Always update label if it exists in new data
                    childNodes: mergeUpdates(
                        newNode.childNodes || [],
                        existingNode.childNodes || []
                    ),
                    hasCaret: !_.isUndefined(newNode.hasCaret)
                        ? newNode.hasCaret
                        : existingNode.hasCaret,
                    icon: newNode.icon || existingNode.icon,
                    secondaryLabel:
                        newNode.secondaryLabel || existingNode.secondaryLabel,
                    // Keep existing status properties
                    isExpanded: existingNode.isExpanded,
                    // Add other status properties to preserve
                });
            } else {
                merged.push(newNode);
            }
        });
        return merged;
    }
    // Handle cases where keys might have been removed
    const allKeysProcessed = new Set(
        keys
            .map((key) => {
                const parts = key.split(":");
                let path = "";
                return parts.map(
                    (part) => (path = path ? `${path}:${part}` : part)
                );
            })
            .flat()
    );
    function filterOutdatedNodes(nodes) {
        return nodes.filter((node) => {
            const isStillPresent =
                allKeysProcessed.has(node.id) ||
                (node.childNodes &&
                    _.some(node.childNodes, (child) =>
                        allKeysProcessed.has(child.id)
                    ));
            if (node.childNodes) {
                node.childNodes = filterOutdatedNodes(node.childNodes);
                if (node.childNodes.length > 0) {
                    node.hasCaret = true;
                } else if (
                    !_.some(keys, (key) => key.startsWith(node.id + ":"))
                ) {
                    delete node.childNodes;
                    delete node.hasCaret;
                }
            }
            return (
                isStillPresent ||
                node.hasCaret ||
                _.isEqual(node.icon, FOLDER_CLOSED_ICON)
            ); // Keep folders or leaves
        });
    }
    const updatedTree = mergeUpdates(newTree, previousTree);
    const finalTree = filterOutdatedNodes(updatedTree);
    return finalTree;
}
function DebuggerContainer({ width, height, sessionId }) {
    const { session, inspection } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], EMPTY_OBJECT),
            inspection: state.inspection,
        }))
    );
    const { messages } = session;
    const darkMode = useAppStore((state) => state.dark_mode);
    const elementRef = useRef(null);
    const [focusStream, setFocusStream] = useState(null);
    useEffect(() => {
        const current = _.get(inspection, [sessionId, "focusStream"], null);
        if (!_.isNull(current)) {
            setFocusStream(current);
        }
    }, [inspection]);
    const setConnectionSessionAttributes = useSocketStore(
        (state) => state.setConnectionSessionAttributes
    );
    useEffect(() => {
        setConnectionSessionAttributes({
            session_id: sessionId,
            key: "debug_mode",
            value: true,
            reObserve: true,
        });
        return () => {
            setConnectionSessionAttributes({
                session_id: sessionId,
                key: "debug_mode",
                value: false,
                reObserve: true,
            });
        };
    }, []);
    const focusIndex = useMemo(() => {
        for (let i = 0; i < _.size(messages); i++) {
            if (_.isEqual(focusStream, messages[i].stream)) {
                return i;
            }
        }
        return null;
    }, [focusStream]);
    const CELL_CONTENT_STYLES = {
        height: 22,
        display: "flex",
        alignItems: "center",
    };
    const [viewType, setViewType] = useState("list");
    const [visibleSection, setVisibleSection] = useState("messages");
    const [treeContents, setTreeContents] = useState([]);
    useEffect(() => {
        let streams = [];
        let messageMap = {};
        for (let i = 0; i < _.size(messages); i++) {
            const { stream, contentType } = messages[i];
            streams.push(stream);
            messageMap[stream] = { contentType };
        }
        setTreeContents(
            parseRedisStreamKeysToTree(streams, treeContents, messageMap)
        );
    }, [messages]);
    const onNodeClick = (node, nodePath) => {
        let contents = _.cloneDeep(treeContents);
        const path = insertBetween(nodePath, "childNodes");
        let current = _.get(contents, path);
        if (_.has(current, "childNodes")) {
            const isExpanded = !_.get(current, "isExpanded", false);
            _.set(contents, path, {
                ...current,
                isExpanded,
                icon: isExpanded ? FOLDER_OPEN_ICON : FOLDER_CLOSED_ICON,
            });
            setTreeContents(contents);
        } else {
            setFocusStream(node.id);
        }
    };
    const onNodeExpand = (node, nodePath) => {
        let contents = _.cloneDeep(treeContents);
        const path = insertBetween(nodePath, "childNodes");
        let current = _.get(contents, path);
        _.set(contents, path, {
            ...current,
            isExpanded: true,
            icon: FOLDER_OPEN_ICON,
        });
        setTreeContents(contents);
    };
    const onNodeCollapse = (node, nodePath) => {
        let contents = _.cloneDeep(treeContents);
        const path = insertBetween(nodePath, "childNodes");
        let current = _.get(contents, path);
        _.set(contents, path, {
            ...current,
            isExpanded: false,
            icon: FOLDER_CLOSED_ICON,
        });
        setTreeContents(contents);
    };
    const [containerId, setContainerId] = useState(null);
    const callback = (agent) => {
        axios
            .get(`/containers/agents/agent/${agent.name}`)
            .then((response) => {
                setContainerId(_.get(response, "data.result.id", null));
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            });
    };
    return (
        <div
            ref={elementRef}
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <Allotment>
                <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                    <div
                        className="border-bottom"
                        style={{
                            padding: 10,
                            display: "flex",
                            justifyContent: "space-between",
                        }}
                    >
                        <ButtonGroup
                            size={Size.LARGE}
                            variant={ButtonVariant.MINIMAL}
                        >
                            <Tooltip
                                content="Messages"
                                placement="bottom-start"
                            >
                                <Button
                                    onClick={() => {
                                        setVisibleSection("messages");
                                    }}
                                    active={_.isEqual(
                                        visibleSection,
                                        "messages"
                                    )}
                                    icon={<FAIcon icon={faMessages} />}
                                />
                            </Tooltip>
                            <Tooltip content="Agents" placement="bottom">
                                <Button
                                    onClick={() => {
                                        setVisibleSection("agents");
                                    }}
                                    active={_.isEqual(visibleSection, "agents")}
                                    icon={<FAIcon icon={faCircleA} />}
                                />
                            </Tooltip>
                            <Tooltip content="Stream flows" placement="bottom">
                                <Button
                                    onClick={() => {
                                        setVisibleSection("stream_flows");
                                    }}
                                    active={_.isEqual(
                                        visibleSection,
                                        "stream_flows"
                                    )}
                                    icon={<FAIcon icon={faDiagramSuccessor} />}
                                />
                            </Tooltip>
                        </ButtonGroup>
                        {_.isEqual(visibleSection, "messages") && (
                            <ButtonGroup
                                size={Size.LARGE}
                                variant={ButtonVariant.MINIMAL}
                            >
                                <Tooltip content="List View" placement="bottom">
                                    <Button
                                        onClick={() => {
                                            setViewType("list");
                                        }}
                                        active={_.isEqual(viewType, "list")}
                                        icon={<FAIcon icon={faList} />}
                                    />
                                </Tooltip>
                                <Tooltip content="Tree View" placement="bottom">
                                    <Button
                                        onClick={() => {
                                            setViewType("tree");
                                        }}
                                        active={_.isEqual(viewType, "tree")}
                                        icon={<FAIcon icon={faFolderTree} />}
                                    />
                                </Tooltip>
                            </ButtonGroup>
                        )}
                    </div>
                    <div
                        className="full-parent-dimension"
                        style={{
                            overflowY: "auto",
                            maxHeight: "calc(100% - 61px)",
                        }}
                    >
                        {_.isEqual(visibleSection, "agents") && (
                            <SessionAgents
                                sessionId={sessionId}
                                interactive={true}
                                callback={callback}
                            />
                        )}
                        {_.isEqual(visibleSection, "stream_flows") && (
                            <ReactFlowProvider>
                                <StreamFlows sessionId={sessionId} />
                            </ReactFlowProvider>
                        )}
                        {_.isEqual(visibleSection, "messages") &&
                            (_.isEqual(viewType, "list") ? (
                                <AutoSizer>
                                    {({ width: tableWidth }) => (
                                        <HTMLTable
                                            interactive
                                            striped
                                            style={{ width: tableWidth }}
                                            className="table-header-sticky"
                                        >
                                            <thead
                                                style={{
                                                    position: "sticky",
                                                    top: 0,
                                                    backgroundColor: darkMode
                                                        ? Colors.BLACK
                                                        : Colors.WHITE,
                                                    zIndex: 1,
                                                }}
                                            >
                                                <tr>
                                                    <th className="border-bottom">
                                                        <div
                                                            style={{
                                                                paddingLeft: 9,
                                                            }}
                                                        >
                                                            Type
                                                        </div>
                                                    </th>
                                                    <th className="border-bottom">
                                                        Stream
                                                    </th>
                                                    <th
                                                        className="border-bottom"
                                                        style={{
                                                            textAlign:
                                                                Alignment.END,
                                                        }}
                                                    >
                                                        <div
                                                            style={{
                                                                paddingRight: 9,
                                                            }}
                                                        >
                                                            Time
                                                        </div>
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {messages.map((message) => (
                                                    <tr
                                                        key={message.stream}
                                                        onClick={() => {
                                                            setFocusStream(
                                                                message.stream
                                                            );
                                                        }}
                                                    >
                                                        <td>
                                                            <div
                                                                style={{
                                                                    ...CELL_CONTENT_STYLES,
                                                                    width: 80,
                                                                    paddingLeft: 9,
                                                                }}
                                                            >
                                                                <Tag
                                                                    minimal
                                                                    intent={
                                                                        Intent.PRIMARY
                                                                    }
                                                                >
                                                                    {
                                                                        message.contentType
                                                                    }
                                                                </Tag>
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <Tooltip
                                                                placement="bottom"
                                                                boundary={
                                                                    elementRef.current
                                                                }
                                                                content={
                                                                    <div
                                                                        style={{
                                                                            maxWidth: 300,
                                                                            wordBreak:
                                                                                "break-all",
                                                                        }}
                                                                    >
                                                                        {
                                                                            message.stream
                                                                        }
                                                                    </div>
                                                                }
                                                            >
                                                                <div
                                                                    className={classNames(
                                                                        "full-parent-width",
                                                                        Classes.TEXT_OVERFLOW_ELLIPSIS
                                                                    )}
                                                                    style={{
                                                                        lineHeight:
                                                                            "22px",
                                                                        width: `${
                                                                            tableWidth -
                                                                            66 -
                                                                            180
                                                                        }px`,
                                                                    }}
                                                                >
                                                                    {
                                                                        message.stream
                                                                    }
                                                                </div>
                                                            </Tooltip>
                                                        </td>
                                                        <td>
                                                            <div
                                                                style={{
                                                                    ...CELL_CONTENT_STYLES,
                                                                    width: 100,
                                                                    paddingRight: 9,
                                                                    justifyContent:
                                                                        "end",
                                                                    textAlign:
                                                                        Alignment.END,
                                                                }}
                                                            >
                                                                <Timestamp
                                                                    boundary={
                                                                        elementRef.current
                                                                    }
                                                                    placement="bottom"
                                                                    epoch={
                                                                        message.timestamp
                                                                    }
                                                                />
                                                            </div>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </HTMLTable>
                                    )}
                                </AutoSizer>
                            ) : (
                                <Tree
                                    onNodeCollapse={onNodeCollapse}
                                    onNodeExpand={onNodeExpand}
                                    contents={treeContents}
                                    onNodeClick={onNodeClick}
                                />
                            ))}
                    </div>
                </Allotment.Pane>
                <Allotment.Pane
                    minSize={MIN_ALLOTMENT_PANE_SIZE}
                    visible={!_.isEqual(visibleSection, "stream_flows")}
                >
                    {_.isEqual(visibleSection, "agents") && (
                        <AgentLogs
                            containerId={containerId}
                            setContainerId={setContainerId}
                        />
                    )}
                    {_.isEqual(visibleSection, "messages") &&
                        _.isInteger(focusIndex) &&
                        focusIndex >= 0 &&
                        focusIndex < _.size(messages) && (
                            <MessageViewer
                                sessionId={sessionId}
                                message={messages[focusIndex]}
                            />
                        )}
                </Allotment.Pane>
            </Allotment>
        </div>
    );
}
export default withAutoSizer(DebuggerContainer);
