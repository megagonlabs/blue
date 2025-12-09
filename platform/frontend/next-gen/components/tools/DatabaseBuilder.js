import { useSourceStore } from "@/stores/source-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    NonIdealState,
    Popover,
    Size,
    Tag,
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
    const [sourceTree, setSourceTree] = useState({});
    const [nodes, setNodes] = useState([]);
    const parseSourceTreeToNodes = (data, currentPath = "", level = 0) => {
        const nodes = [];
        const hierarchyLevels = ["database", "collection", "entity"];
        const keys = _.keys(data);
        for (let i = 0; i < _.size(keys); i++) {
            const key = keys[i];
            const id = currentPath ? `${currentPath}.${key}` : key;
            const type = _.get(hierarchyLevels, level, "unknown");
            const icon = <RegistryEntityIcon type={type} maxSize={20} />;
            const node = {
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
                isExpanded: true,
            };
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
                    level + 1
                );
            }
            nodes.push(node);
        }
        return nodes;
    };
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
            setLoading(true);
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
                    setSelectedDatabase(null);
                    setSelectedCollection(null);
                })
                .catch((error) => {
                    showAxiosErrorToast(error);
                })
                .finally(() => {
                    setLoading(false);
                });
        }
    }, [selectedSource]);
    const [view, setView] = useState("query-editor");
    const [viewMode, setViewMode] = useState("table");
    const [query, setQuery] = useState("");
    const [queryResults, setQueryResults] = useState(null);
    const setDefaultQuery = (entity) => {
        if (_.isEqual(databaseType, "PostgresDBSource")) {
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
        if (_.isEqual(type, "csv")) {
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
    return (
        <div ref={elementRef} style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{ overflowY: "auto", minWidth: 250 }}
                    className="border-right"
                >
                    <div className="border-bottom" style={{ padding: 10 }}>
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
                                alignText={Alignment.START}
                                ellipsizeText
                                text={
                                    _.isEmpty(selectedSource)
                                        ? "Connect"
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
                            active={_.isEqual(view, "query-editor")}
                            alignText={Alignment.START}
                            fill
                            variant={ButtonVariant.MINIMAL}
                            icon={<FAIcon icon={faBoxMagnifyingGlass} />}
                            text="Query Editor"
                        />
                    </div>
                    <div
                        style={{
                            height: "calc(100% - 111px)",
                            overflowY: "auto",
                            borderRadius: 0,
                        }}
                    >
                        <div
                            style={{
                                padding: 10,
                                gap: 10,
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <Tag
                                icon={
                                    <FAIcon
                                        icon={
                                            ENTITY_TYPE_LOOKUP["database"].icon
                                        }
                                    />
                                }
                                minimal
                                size={Size.LARGE}
                                intent={
                                    _.isEmpty(selectedDatabase)
                                        ? Intent.DANGER
                                        : Intent.SUCCESS
                                }
                            >
                                {_.isEmpty(selectedDatabase)
                                    ? "Database"
                                    : selectedDatabase}
                            </Tag>
                            <Tag
                                icon={
                                    <FAIcon
                                        icon={
                                            ENTITY_TYPE_LOOKUP["collection"]
                                                .icon
                                        }
                                    />
                                }
                                minimal
                                size={Size.LARGE}
                                intent={
                                    _.includes(
                                        ["PostgresDBSource"],
                                        databaseType
                                    )
                                        ? Intent.NONE
                                        : _.isEmpty(selectedCollection)
                                        ? Intent.DANGER
                                        : Intent.SUCCESS
                                }
                            >
                                {_.isEmpty(selectedCollection)
                                    ? "Collection"
                                    : selectedCollection}
                            </Tag>
                        </div>
                        <Tree
                            contents={nodes}
                            onNodeClick={(node) => {
                                const { type, value } = node.nodeData;
                                if (_.isEqual(type, "database")) {
                                    setSelectedDatabase(value);
                                } else if (_.isEqual(type, "collection")) {
                                    setSelectedCollection(value);
                                } else if (_.isEqual(type, "entity")) {
                                    setDefaultQuery(value);
                                }
                            }}
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
                                                _.isEqual(viewMode, "table")
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
                                                        !connected ||
                                                        _.isEmpty(query)
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
                                                    active={_.isEqual(
                                                        viewMode,
                                                        "table"
                                                    )}
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
                                                    active={_.isEqual(
                                                        viewMode,
                                                        "json"
                                                    )}
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
                                            _.isEqual(viewMode, "table") && (
                                                <TableVisualizer
                                                    list={queryResults}
                                                />
                                            )}
                                        {!_.isNull(queryResults) &&
                                            _.isEqual(viewMode, "json") && (
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
