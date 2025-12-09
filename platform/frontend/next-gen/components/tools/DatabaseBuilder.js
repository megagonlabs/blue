import { insertBetween } from "@/components/helper";
import { useSourceStore } from "@/stores/source-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    CompoundTag,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    NonIdealState,
    Popover,
    Size,
    Tooltip,
    Tree,
} from "@blueprintjs/core";
import {
    faAngleDown,
    faBracketsSquare,
    faFileCsv,
    faFileExport,
    faServer,
    faTable,
    faTableList,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import {
    faBoxMagnifyingGlass,
    faPlay,
} from "@fortawesome/sharp-solid-svg-icons";
import { Allotment } from "allotment";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import TextEditor from "../codemirror/TextEditor";
import {
    ENTITY_TYPE_LOOKUP,
    MIN_ALLOTMENT_PANE_SIZE,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import JSONViewer from "../JSONViewer";
import RegistryEntityIcon from "../registries/RegistryEntityIcon";
import TableVisualizer from "./visualizers/TableVisualizer";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
function convertJSONToCSV(jsonData, headers) {
    if (!jsonData || _.isEmpty(jsonData)) {
        return "";
    }
    let actualHeaders = headers;
    let headerKeys = new Set();
    for (let i = 0; i < _.size(jsonData); i++) {
        const keys = _.keys(jsonData[i]);
        for (let j = 0; j < _.size(keys); j++) {
            headerKeys.add(keys[j]);
        }
    }
    actualHeaders = _.toArray(headerKeys);
    let headerRow = _.join(actualHeaders, ",");
    let dataRows = [];
    for (let i = 0; i < _.size(jsonData); i++) {
        let temp = [];
        for (let j = 0; j < _.size(actualHeaders); j++) {
            let value = _.get(jsonData, [i, actualHeaders[j]]);
            if (_.isNil(value)) {
                value = "";
            } else {
                value = String(value);
                if (/["\n,]/.test(value)) {
                    value = `"${value.replace(/"/g, '""')}"`;
                }
            }
            temp.push(value || "");
        }
        dataRows.push(_.join(temp, ","));
    }
    dataRows = _.join(dataRows, "\n");
    return `${headerRow}\n${dataRows}`;
}
const parseSourceTreeToNodes = (
    data,
    currentPath = "",
    level = 0,
    database = null,
    collection = null
) => {
    const nodes = [];
    const hierarchyLevels = ["database", "collection", "entity"];
    const keys = _.keys(data);
    for (let i = 0; i < _.size(keys); i++) {
        const key = keys[i];
        const id = currentPath ? `${currentPath}.${key}` : key;
        const type = _.get(hierarchyLevels, level, "unknown");
        const icon = <RegistryEntityIcon type={type} maxSize={20} />;
        let node = {
            id,
            label: (
                <div
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{ marginLeft: 8, paddingRight: 4 }}
                >
                    {key}
                </div>
            ),
            icon,
            nodeData: { type, path: id, value: key },
            isExpanded: false,
        };
        if (type === "collection") {
            _.set(node, "nodeData.database", database);
        } else if (type === "entity") {
            _.set(node, "nodeData.database", database);
            _.set(node, "nodeData.collection", collection);
        }
        const childrenData = data[key];
        if (
            childrenData &&
            _.isObject(childrenData) &&
            !_.isEmpty(_.keys(childrenData)) &&
            level < _.size(hierarchyLevels) - 1
        ) {
            node.childNodes = parseSourceTreeToNodes(
                childrenData,
                id,
                level + 1,
                database || (type === "database" ? key : null),
                collection || (type === "collection" ? key : null)
            );
        }
        nodes.push(node);
    }
    return nodes;
};
const COMPOUND_TAG_PROPS = { size: Size.LARGE, minimal: true, fill: true };
function DatabaseBuilder({ width, height }) {
    const { data, getSources } = useSourceStore(
        useShallow((state) => ({
            data: state.sources,
            getSources: state.getSources,
        }))
    );
    const [selectedSource, setSelectedSource] = useState(null);
    useEffect(() => {
        getSources();
    }, []);
    const elementRef = useRef(null);
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(false);
    const [connecting, setConnecting] = useState(false);
    const [sourceTree, setSourceTree] = useState({});
    const [nodes, setNodes] = useState([]);
    useEffect(() => {
        setNodes(parseSourceTreeToNodes(sourceTree));
    }, [sourceTree]);
    const [databaseType, setDatabaseType] = useState(null);
    const [selectedDatabase, setSelectedDatabase] = useState(null);
    const [selectedCollection, setSelectedCollection] = useState(null);
    const { showAxiosErrorToast } = useToaster();
    useEffect(() => {
        if (_.has(selectedSource, "name")) {
            setConnected(false);
            setConnecting(true);
            setNodes([]);
            setSelectedDatabase(null);
            setSelectedCollection(null);
            axios
                .post(
                    `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/data/${selectedSource.name}/connect`
                )
                .then((response) => {
                    setDatabaseType(_.get(response, "data.result.type", null));
                    setSourceTree(
                        _.get(response, "data.result.source_tree", {})
                    );
                    setConnected(true);
                })
                .catch((error) => {
                    showAxiosErrorToast(error);
                    setSelectedSource(null);
                })
                .finally(() => {
                    setConnecting(false);
                });
        }
    }, [selectedSource]);
    const [view, setView] = useState("query-editor");
    const [viewMode, setViewMode] = useState("table");
    const [query, setQuery] = useState("");
    const [queryResults, setQueryResults] = useState(null);
    const setDefaultQuery = (entity) => {
        if (databaseType === "PostgresDBSource") {
            setQuery(`SELECT * FROM ${entity} LIMIT 100;`);
        }
    };
    const runQuery = () => {
        setLoading(true);
        axios
            .post(
                `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/data/${selectedSource.name}/query`,
                {
                    query,
                    database: selectedDatabase,
                    collection: selectedCollection,
                }
            )
            .then((response) => {
                setQueryResults(_.get(response, "data.results", []));
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    const handleExport = (type) => {
        if (type === "csv") {
            const fileContent = convertJSONToCSV(queryResults);
            if (fileContent) {
                const blob = new Blob([fileContent], {
                    type: "text/csv;charset=utf-8;",
                });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.setAttribute("download", "data.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }
    };
    const REQUIRE_DATABASE = !_.includes(
        ["OpenAISource", "NEO4JSource"],
        databaseType
    );
    const REQUIRE_COLLECTION = _.includes(["MongoDBSource"], databaseType);
    const RUN_QUERY_DISABLED =
        !connected ||
        _.isEmpty(query) ||
        (!_.includes(["NEO4JSource"], databaseType) &&
            _.isEmpty(selectedDatabase)) ||
        (!_.includes(["PostgresDBSource"], databaseType) &&
            _.isEmpty(selectedCollection));
    const onNodeExpand = (node, nodePath) => {
        let temp = _.cloneDeep(nodes);
        _.set(
            temp,
            [...insertBetween(nodePath, "childNodes"), "isExpanded"],
            true
        );
        setNodes(temp);
    };
    const onNodeCollapse = (node, nodePath) => {
        let temp = _.cloneDeep(nodes);
        _.set(
            temp,
            [...insertBetween(nodePath, "childNodes"), "isExpanded"],
            true
        );
        setNodes(temp);
    };
    return (
        <div ref={elementRef} style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{ overflowY: "auto", minWidth: 250, maxWidth: 250 }}
                    className="border-right"
                >
                    <div className="border-bottom" style={{ padding: 20 }}>
                        <Popover
                            fill
                            {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                            boundary={elementRef.current}
                            content={
                                <Menu size={Size.LARGE}>
                                    {data.map((source, index) => (
                                        <MenuItem
                                            onClick={() =>
                                                setSelectedSource(
                                                    _.cloneDeep(source)
                                                )
                                            }
                                            key={index}
                                            text={source.name}
                                        />
                                    ))}
                                </Menu>
                            }
                        >
                            <Button
                                loading={connecting}
                                alignText={Alignment.START}
                                ellipsizeText
                                text={
                                    _.isEmpty(selectedSource)
                                        ? "Connect source"
                                        : selectedSource.name
                                }
                                endIcon={<FAIcon icon={faAngleDown} />}
                                intent={Intent.PRIMARY}
                                size={Size.LARGE}
                                variant={ButtonVariant.OUTLINED}
                                icon={<FAIcon icon={faServer} />}
                            />
                        </Popover>
                        <Button
                            style={{ marginTop: 10 }}
                            onClick={() => {
                                setView("query-editor");
                            }}
                            size={Size.LARGE}
                            active={view === "query-editor"}
                            alignText={Alignment.START}
                            fill
                            variant={ButtonVariant.MINIMAL}
                            icon={<FAIcon icon={faBoxMagnifyingGlass} />}
                            text="Query Editor"
                        />
                    </div>
                    <div className="border-bottom" style={{ padding: 10 }}>
                        <CompoundTag
                            {...COMPOUND_TAG_PROPS}
                            leftContent="Database"
                            icon={
                                <FAIcon
                                    icon={ENTITY_TYPE_LOOKUP["database"].icon}
                                />
                            }
                            intent={
                                _.isEmpty(selectedDatabase)
                                    ? REQUIRE_DATABASE
                                        ? Intent.DANGER
                                        : Intent.NONE
                                    : Intent.SUCCESS
                            }
                        >
                            <div
                                style={{ width: 88.17 }}
                                className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            >
                                {_.isEmpty(selectedDatabase)
                                    ? "-"
                                    : selectedDatabase}
                            </div>
                        </CompoundTag>
                        <CompoundTag
                            {...COMPOUND_TAG_PROPS}
                            style={{ marginTop: 10 }}
                            leftContent="Collection"
                            icon={
                                <FAIcon
                                    icon={ENTITY_TYPE_LOOKUP["collection"].icon}
                                />
                            }
                            intent={
                                _.isEmpty(selectedCollection)
                                    ? REQUIRE_COLLECTION
                                        ? Intent.DANGER
                                        : Intent.NONE
                                    : Intent.SUCCESS
                            }
                        >
                            <div
                                style={{ width: 88.17 }}
                                className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            >
                                {_.isEmpty(selectedCollection)
                                    ? "-"
                                    : selectedCollection}
                            </div>
                        </CompoundTag>
                    </div>
                    <div
                        className={connecting ? Classes.SKELETON : null}
                        style={{
                            height: "calc(100% - 222px)",
                            overflowY: "auto",
                            borderRadius: 0,
                        }}
                    >
                        <Tree
                            contents={nodes}
                            onNodeClick={(node) => {
                                const { type, value, database, collection } =
                                    node.nodeData;
                                if (database) {
                                    setSelectedDatabase(database);
                                }
                                if (collection) {
                                    setSelectedCollection(collection);
                                }
                                if (type === "database") {
                                    setSelectedDatabase(value);
                                } else if (type === "collection") {
                                    setSelectedCollection(value);
                                } else if (type === "entity") {
                                    setDefaultQuery(value);
                                }
                            }}
                            onNodeDoubleClick={(node) => {
                                const { type, value, database, collection } =
                                    node.nodeData;
                                if (database) {
                                    setSelectedDatabase(database);
                                }
                                if (collection) {
                                    setSelectedCollection(collection);
                                }
                                if (type === "entity") {
                                    setDefaultQuery(value);
                                    setTimeout(() => {
                                        runQuery();
                                    }, 0);
                                }
                            }}
                            onNodeExpand={onNodeExpand}
                            onNodeCollapse={onNodeCollapse}
                        />
                    </div>
                </div>
                <div
                    className="full-parent-dimension"
                    style={{
                        overflowY: "auto",
                        overflowX: "hidden",
                        display: "flex",
                        flexDirection: "column",
                    }}
                >
                    <Allotment>
                        <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                            <Allotment vertical defaultSizes={[100, 400]}>
                                <Allotment.Pane minSize={100}>
                                    <TextEditor
                                        useMinimap={false}
                                        textObject={query}
                                        setBack={(query) => {
                                            setQuery(query);
                                        }}
                                    />
                                </Allotment.Pane>
                                <Allotment.Pane minSize={200}>
                                    <div
                                        className="border-bottom"
                                        style={{
                                            padding: 10,
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "space-between",
                                            borderColor:
                                                !_.isNull(queryResults) &&
                                                viewMode === "table"
                                                    ? "transparent"
                                                    : null,
                                        }}
                                    >
                                        <ButtonGroup
                                            size={Size.LARGE}
                                            variant={ButtonVariant.MINIMAL}
                                        >
                                            <Tooltip
                                                content="Run query"
                                                placement="bottom"
                                            >
                                                <Button
                                                    disabled={
                                                        RUN_QUERY_DISABLED
                                                    }
                                                    loading={loading}
                                                    icon={
                                                        <FAIcon icon={faPlay} />
                                                    }
                                                    intent={Intent.SUCCESS}
                                                    onClick={runQuery}
                                                />
                                            </Tooltip>
                                            <Popover
                                                {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                                                boundary={elementRef.current}
                                                minimal
                                                placement="right-start"
                                                content={
                                                    <Menu size={Size.LARGE}>
                                                        <MenuDivider title="Download as" />
                                                        <MenuItem
                                                            icon={
                                                                <FAIcon
                                                                    icon={
                                                                        faFileCsv
                                                                    }
                                                                />
                                                            }
                                                            text="Comma Separated Values (.csv)"
                                                            onClick={() => {
                                                                handleExport(
                                                                    "csv"
                                                                );
                                                            }}
                                                        />
                                                    </Menu>
                                                }
                                            >
                                                <Tooltip
                                                    content="Export"
                                                    placement="bottom"
                                                >
                                                    <Button
                                                        disabled={_.isEmpty(
                                                            queryResults
                                                        )}
                                                        icon={
                                                            <FAIcon
                                                                icon={
                                                                    faFileExport
                                                                }
                                                            />
                                                        }
                                                    />
                                                </Tooltip>
                                            </Popover>
                                        </ButtonGroup>
                                        <ButtonGroup
                                            size={Size.LARGE}
                                            variant={ButtonVariant.MINIMAL}
                                        >
                                            <Tooltip
                                                content="Table View"
                                                placement="bottom"
                                            >
                                                <Button
                                                    onClick={() => {
                                                        setViewMode("table");
                                                    }}
                                                    active={
                                                        viewMode === "table"
                                                    }
                                                    icon={
                                                        <FAIcon
                                                            icon={faTable}
                                                        />
                                                    }
                                                />
                                            </Tooltip>
                                            <Tooltip
                                                content="JSON View"
                                                {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                                                boundary={elementRef.current}
                                            >
                                                <Button
                                                    onClick={() => {
                                                        setViewMode("json");
                                                    }}
                                                    active={viewMode === "json"}
                                                    icon={
                                                        <FAIcon
                                                            icon={
                                                                faBracketsSquare
                                                            }
                                                        />
                                                    }
                                                />
                                            </Tooltip>
                                        </ButtonGroup>
                                    </div>
                                    <div
                                        className="full-parent-dimension"
                                        style={{
                                            maxHeight: "calc(100% - 61px)",
                                        }}
                                    >
                                        {_.isNull(queryResults) && (
                                            <NonIdealState
                                                title="Run a query to see results"
                                                icon={
                                                    <FAIcon
                                                        size={50}
                                                        icon={faTableList}
                                                    />
                                                }
                                            />
                                        )}
                                        {!_.isNull(queryResults) &&
                                            viewMode === "table" && (
                                                <TableVisualizer
                                                    list={queryResults}
                                                />
                                            )}
                                        {!_.isNull(queryResults) &&
                                            viewMode === "json" && (
                                                <div
                                                    className="full-parent-height"
                                                    style={{
                                                        overflowY: "auto",
                                                        padding: "12px 16px",
                                                    }}
                                                >
                                                    <JSONViewer
                                                        json={queryResults}
                                                    />
                                                </div>
                                            )}
                                    </div>
                                </Allotment.Pane>
                            </Allotment>
                        </Allotment.Pane>
                    </Allotment>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(DatabaseBuilder);
