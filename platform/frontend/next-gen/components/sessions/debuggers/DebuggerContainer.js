import { MIN_ALLOTMENT_PANE_SIZE } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { insertBetween } from "@/components/helper";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import Timestamp from "@/components/Timestamp";
import { useAppStore } from "@/stores/app-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    HTMLTable,
    Intent,
    Tag,
    Tooltip,
    Tree,
} from "@blueprintjs/core";
import {
    faFolder,
    faFolderOpen,
    faFolderTree,
    faList,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { Allotment } from "allotment";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useMemo, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { useShallow } from "zustand/react/shallow";
import MessageViewer from "./MessageViewer";
const FOLDER_CLOSED_ICON = (
    <FAIcon icon={faFolder} style={{ marginRight: 7 }} />
);
const FOLDER_OPEN_ICON = (
    <FAIcon icon={faFolderOpen} size={18} style={{ marginRight: 7 }} />
);
function parseRedisStreamKeysToTree(messageMap, keys) {
    const tree = [];
    const nodeMap = {};
    for (let i = 0; i < _.size(keys); i++) {
        const key = keys[i];
        const parts = key.split(":");
        let currentPath = "";
        let parentId = null;
        for (let j = 0; j < parts.length; j++) {
            const part = parts[j];
            const id = currentPath ? `${currentPath}:${part}` : part;
            const label = part;
            let existingNode = nodeMap[id];
            if (!existingNode) {
                existingNode = {
                    id: id,
                    label: label,
                    childNodes: [],
                    icon: FOLDER_CLOSED_ICON,
                };
                if (_.includes(["STREAM"], part)) {
                    _.set(
                        existingNode,
                        "secondaryLabel",
                        <Tag minimal intent={Intent.PRIMARY}>
                            {messageMap[id].contentType}
                        </Tag>
                    );
                }
                nodeMap[id] = existingNode;
                if (!_.isNull(parentId)) {
                    const parentNode = nodeMap[parentId];
                    if (parentNode) {
                        parentNode.childNodes.push(existingNode);
                        parentNode.hasCaret = true;
                    }
                } else {
                    tree.push(existingNode);
                }
            }
            currentPath = id;
            parentId = id;
        }
        // after processing all parts of the key, ensure the final node is a leaf
        if (nodeMap[currentPath]) {
            delete nodeMap[currentPath].childNodes; // remove childNodes if it's a leaf
            delete nodeMap[currentPath].hasCaret;
            delete nodeMap[currentPath].icon;
        }
    }
    return tree;
}
function DebuggerContainer({ width, height, sessionId }) {
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], {}),
        }))
    );
    const { messages } = session;
    const darkMode = useAppStore((state) => state.dark_mode);
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const [focusStream, setFocusStream] = useState(null);
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
    const [treeContents, setTreeContents] = useState([]);
    useEffect(() => {
        let streams = [];
        let messageMap = {};
        for (let i = 0; i < _.size(messages); i++) {
            const stream = messages[i].stream;
            streams.push(stream);
            messageMap[stream] = { contentType: messages[i].contentType };
        }
        setTreeContents(parseRedisStreamKeysToTree(messageMap, streams));
    }, [messages]);
    const onNodeClick = (node, nodePath, e) => {
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
    const onNodeExpand = (node, nodePath, e) => {
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
    const onNodeCollapse = (node, nodePath, e) => {
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
                        style={{ padding: 10, textAlign: "end" }}
                    >
                        <ButtonGroup variant={ButtonVariant.MINIMAL}>
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
                    </div>
                    <div
                        className="full-parent-dimension"
                        style={{
                            overflowY: "auto",
                            maxHeight: "calc(100% - 51px)",
                        }}
                    >
                        {_.isEqual(viewType, "list") ? (
                            <AutoSizer>
                                {({ width: tableWidth }) => (
                                    <HTMLTable
                                        interactive
                                        striped
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
                                        <tbody style={{ overflowY: "auto" }}>
                                            {messages.map((message, index) => (
                                                <tr
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
                                                                popoverBoundary
                                                            }
                                                            content={
                                                                <div
                                                                    style={{
                                                                        width: 300,
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
                                                                {message.stream}
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
                                                                    popoverBoundary
                                                                }
                                                                placement="bottom"
                                                                date={
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
                        )}
                    </div>
                </Allotment.Pane>
                <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                    {_.isInteger(focusIndex) &&
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
