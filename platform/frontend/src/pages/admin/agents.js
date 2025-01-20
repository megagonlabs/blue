import AccessDeniedNonIdealState from "@/components/AccessDeniedNonIdealState";
import AdminAgentListCheckbox from "@/components/admin/AdminAgentListCheckbox";
import { CONTAINER_STATUS_INDICATOR } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { axiosErrorToast } from "@/components/helper";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Divider,
    Drawer,
    H4,
    Intent,
    NonIdealState,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    Cell,
    Column,
    ColumnHeaderCell,
    RowHeaderCell,
    Table2,
    TableLoadingOption,
    Utils,
} from "@blueprintjs/table";
import {
    faCircleA,
    faRectangleTerminal,
    faRefresh,
    faStop,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import ReactTimeAgo from "react-time-ago";
import DockerContainerLogs from "./DockerContainerLogs";
export default function Agents() {
    const { appState } = useContext(AppContext);
    const [tableKey, setTableKey] = useState(Date.now());
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState([]);
    const [showLogs, setShowLogs] = useState(false);
    const [containerId, setContainerId] = useState(null);
    const stopSelectedAgents = async () => {
        const selectedAgents = _.toArray(appState.admin.selectedAgents);
        let tasks = [];
        for (let i = 0; i < _.size(selectedAgents); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(`/containers/container/${selectedAgents[i]}`)
                        .then(() => {
                            resolve(selectedAgents[i]);
                        })
                        .catch((error) => {
                            axiosErrorToast(error);
                            reject(selectedAgents[i]);
                        });
                })
            );
        }
        const result = await Promise.allSettled(tasks);
        let stoppedAgents = new Set();
        for (let i = 0; i < _.size(result); i++) {
            if (_.isEqual(result[i].status, "fulfilled")) {
                stoppedAgents.add(result[i].value);
            }
        }
        if (!_.isEmpty(stoppedAgents)) {
            const size = _.size(stoppedAgents);
            let message = `Stopped ${size} agents`;
            if (size == 1) {
                message = `Stopped ${_.toArray(stoppedAgents)[0]} agent`;
            }
            AppToaster.show({ intent: Intent.SUCCESS, message });
        }
    };
    const fetchContainerList = () => {
        setLoading(true);
        axios.get("/containers/agents").then((response) => {
            setData(_.get(response, "data.results", []));
            setLoading(false);
            setData([
                {
                    id: "f731181d8a589e8bf1839b65b8a7d6a1e5b840af6bef6370919b30fd18f6a21c",
                    hostname: "blue_agent_default_AGENTICEMPLOYER",
                    created_date: "2025-01-09T18:05:52.790822196Z",
                    image: "megagonlabs/blue-agent-agentic_employer:latest",
                    status: "running",
                    agent: "AGENTICEMPLOYER",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "b9cc5775fa8b6e7b1bc27e7bb9757d1505fc0703453e7a97b063c0fed8f7a014",
                    hostname: "blue_agent_default_DOCUMENTER",
                    created_date: "2025-01-09T18:05:42.382900595Z",
                    image: "megagonlabs/blue-agent-documenter",
                    status: "running",
                    agent: "DOCUMENTER",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "2ce41dce2efc71bb714c7b9a729ce20ffaaff99e476a939563921d21a2f7612d",
                    hostname: "blue_agent_default_VISUALIZER",
                    created_date: "2025-01-09T18:05:34.259392626Z",
                    image: "megagonlabs/blue-agent-visualizer",
                    status: "running",
                    agent: "VISUALIZER",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "8e4c7fe01322a3f95d5b3f6381c9e029d7a88bcde691a99c255da8d8b402d7bb",
                    hostname: "blue_agent_default_QUERYEXECUTOR",
                    created_date: "2025-01-09T18:04:23.359397918Z",
                    image: "blue-agent-query_executor:latest",
                    status: "running",
                    agent: "QUERYEXECUTOR",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "2bc25336fe06dd681912a2265ee8a85745980cfa14d52757501b2c217bc27c7c",
                    hostname: "blue_agent_default_CLUSTERER",
                    created_date: "2025-01-09T18:04:14.795135261Z",
                    image: "megagonlabs/blue-agent-clusterer:latest",
                    status: "running",
                    agent: "CLUSTERER",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "dbf065682c50b35fa0d2010d50c6d353172d504da0a70e180be2d3f1f169c273",
                    hostname: "blue_agent_default_SUMMARIZER",
                    created_date: "2025-01-09T18:04:00.754362896Z",
                    image: "megagonlabs/blue-agent-summarizer:latest",
                    status: "running",
                    agent: "SUMMARIZER",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "564b40d8d6aedd6e5b825f5bbbb80128c14a092d4cbf03ab5b47b3a223212388",
                    hostname: "blue_agent_default_NL2SQL-E2E",
                    created_date: "2025-01-09T18:03:49.693576173Z",
                    image: "megagonlabs/blue-agent-nl2sql-e2e:latest",
                    status: "running",
                    agent: "NL2SQL-E2E",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "d92a9c7acf31eb1909531caf4a690b8bba4350fd9a309bb82688791cdad03176",
                    hostname: "blue_agent_default_OPENAI",
                    created_date: "2025-01-09T18:03:41.978240598Z",
                    image: "megagonlabs/blue-agent-openai:latest",
                    status: "running",
                    agent: "OPENAI",
                    registry: "default",
                    platform: "employer",
                },
                {
                    id: "170f3b1753589bab452105ca588912f60c9ec30d30518f6d9b724afab4a8697b",
                    hostname: "blue_agent_default_COORDINATOR",
                    created_date: "2025-01-09T18:03:34.644495549Z",
                    image: "megagonlabs/blue-agent-coordinator:latest",
                    status: "running",
                    agent: "COORDINATOR",
                    registry: "default",
                    platform: "employer",
                },
            ]);
        });
    };
    useEffect(() => {
        fetchContainerList();
    }, []);
    const TABLE_CELL_HEIGHT = 40;
    const CELL_STYLE = {
        lineHeight: `${TABLE_CELL_HEIGHT - 1}px`,
    };
    const INIT_COLUMNS = [
        {
            name: <div>&nbsp;</div>,
            key: "checkbox",
            cellRenderer: ({ rowIndex, data }) => (
                <Cell style={CELL_STYLE}>
                    <AdminAgentListCheckbox rowIndex={rowIndex} data={data} />
                </Cell>
            ),
        },
        {
            name: "Actions",
            key: "actions",
            cellRenderer: ({ rowIndex, data }) => (
                <Cell style={CELL_STYLE}>
                    <ButtonGroup minimal style={{ marginTop: 4.5 }}>
                        <Tooltip
                            openOnTargetFocus={false}
                            content="Logs"
                            placement="bottom"
                            minimal
                        >
                            <Button
                                onClick={() => {
                                    setShowLogs(true);
                                    setContainerId(
                                        _.get(data, [rowIndex, "id"], null)
                                    );
                                }}
                                icon={faIcon({ icon: faRectangleTerminal })}
                            />
                        </Tooltip>
                    </ButtonGroup>
                </Cell>
            ),
        },
        { name: "ID", key: "id" },
        { name: "Hostname", key: "hostname" },
        {
            name: "Created At",
            key: "created_date",
            cellRenderer: ({ rowIndex, data }) => {
                const timestamp = _.get(data, [rowIndex, "created_date"], null);
                return (
                    <Cell style={CELL_STYLE}>
                        {!_.isEmpty(timestamp) ? (
                            <ReactTimeAgo
                                date={new Date(timestamp)}
                                locale="en-US"
                            />
                        ) : (
                            "-"
                        )}
                    </Cell>
                );
            },
        },
        {
            name: "Image",
            key: "image",
            cellRenderer: ({ rowIndex, data }) => (
                <Cell style={CELL_STYLE}>
                    <Tag intent={Intent.PRIMARY} minimal>
                        {_.get(data, [rowIndex, "image"], "-")}
                    </Tag>
                </Cell>
            ),
        },
        {
            name: "Status",
            key: "status",
            cellRenderer: ({ rowIndex, data }) => {
                const status = _.get(data, [rowIndex, "status"], "-");
                return (
                    <Cell style={CELL_STYLE}>
                        <Tag
                            intent={_.get(
                                CONTAINER_STATUS_INDICATOR,
                                [status, "intent"],
                                null
                            )}
                            minimal
                        >
                            {_.capitalize(status)}
                        </Tag>
                    </Cell>
                );
            },
        },
        { name: "Agent", key: "agent" },
        { name: "Registry", key: "registry" },
    ];
    const [columns, setColumns] = useState(INIT_COLUMNS);
    useEffect(() => {
        setTableKey(Date.now());
    }, [data, columns]);
    const handleColumnsReordered = (oldIndex, newIndex, length) => {
        if (_.isEqual(oldIndex, newIndex)) return;
        const nextChildren = Utils.reorderArray(
            columns,
            oldIndex,
            newIndex,
            length
        );
        setColumns(nextChildren);
    };
    const { permissions } = useContext(AuthContext);
    if (!permissions.canReadPlatformAgents) {
        return <AccessDeniedNonIdealState />;
    }
    return (
        <>
            <Card
                interactive
                style={{
                    padding: 5,
                    borderRadius: 0,
                    position: "relative",
                    zIndex: 1,
                    cursor: "default",
                }}
            >
                <ButtonGroup large minimal>
                    <Button
                        disabled
                        style={{ cursor: "default" }}
                        text={<H4 className="margin-0">Agents</H4>}
                    />
                    <Tooltip placement="bottom" minimal content="Refresh">
                        <Button
                            onClick={fetchContainerList}
                            loading={loading}
                            icon={faIcon({ icon: faRefresh })}
                        />
                    </Tooltip>
                    <Divider />
                    <Tooltip placement="bottom" minimal content="Stop">
                        <Button
                            intent={Intent.DANGER}
                            onClick={stopSelectedAgents}
                            disabled={
                                _.isEmpty(appState.admin.selectedAgents) ||
                                loading
                            }
                            icon={faIcon({ icon: faStop })}
                        />
                    </Tooltip>
                </ButtonGroup>
            </Card>
            <div style={{ height: "calc(100% - 50px)" }}>
                {_.isEmpty(data) ? (
                    <div
                        className="full-parent-width"
                        style={{
                            position: "absolute",
                            bottom: 0,
                            right: 0,
                            height: "calc(100% - 50px)",
                        }}
                    >
                        <NonIdealState
                            title="No Agent"
                            icon={faIcon({ icon: faCircleA, size: 50 })}
                        />
                    </div>
                ) : (
                    <Table2
                        loadingOptions={
                            loading
                                ? [
                                      TableLoadingOption.CELLS,
                                      TableLoadingOption.ROW_HEADERS,
                                  ]
                                : []
                        }
                        key={tableKey}
                        enableRowResizing={false}
                        numRows={data.length}
                        enableColumnReordering
                        onColumnsReordered={handleColumnsReordered}
                        rowHeaderCellRenderer={(rowIndex) => (
                            <RowHeaderCell
                                name={
                                    <div
                                        style={{
                                            textAlign: "center",
                                            lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                            paddingLeft: 5,
                                            paddingRight: 5,
                                        }}
                                    >
                                        {rowIndex + 1}
                                    </div>
                                }
                            />
                        )}
                        defaultRowHeight={TABLE_CELL_HEIGHT}
                    >
                        {columns.map((col, index) => {
                            const { name, key, cellRenderer } = col;
                            const defaultCellRenderer = (rowIndex) => (
                                <Cell
                                    style={{
                                        lineHeight: `${
                                            TABLE_CELL_HEIGHT - 1
                                        }px`,
                                    }}
                                >
                                    {_.get(data, [rowIndex, key], "-")}
                                </Cell>
                            );
                            const menuRenderer = null;
                            const columnHeaderCellRenderer = () => (
                                <ColumnHeaderCell
                                    name={
                                        <span style={{ fontWeight: 600 }}>
                                            {name}
                                        </span>
                                    }
                                    menuRenderer={menuRenderer}
                                />
                            );
                            return (
                                <Column
                                    cellRenderer={(rowIndex) =>
                                        _.isFunction(cellRenderer)
                                            ? cellRenderer.call(null, {
                                                  rowIndex,
                                                  data,
                                              })
                                            : defaultCellRenderer.call(
                                                  null,
                                                  rowIndex
                                              )
                                    }
                                    columnHeaderCellRenderer={
                                        columnHeaderCellRenderer
                                    }
                                    key={`${key}-${index}`}
                                    name={name}
                                />
                            );
                        })}
                    </Table2>
                )}
            </div>
            <Drawer
                title="Logs"
                onClose={() => {
                    setShowLogs(false);
                }}
                isOpen={showLogs}
            >
                <div
                    className="full-parent-height"
                    style={{ padding: 20, maxHeight: "calc(100% - 40px)" }}
                >
                    <DockerContainerLogs containerId={containerId} />
                </div>
            </Drawer>
        </>
    );
}
