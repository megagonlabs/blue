import AccessDeniedNonIdealState from "@/components/AccessDeniedNonIdealState";
import AdminAgentListCheckbox from "@/components/admin/AdminAgentListCheckbox";
import DockerContainerLogs from "@/components/admin/DockerContainerLogs";
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
    Classes,
    Divider,
    Drawer,
    H4,
    Intent,
    NonIdealState,
    Popover,
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
    faArrowDownToLine,
    faCircleA,
    faRectangleTerminal,
    faRefresh,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import ReactTimeAgo from "react-time-ago";
export default function Agents() {
    const { appState, appActions } = useContext(AppContext);
    const [tableKey, setTableKey] = useState(Date.now());
    const [loading, setLoading] = useState(true);
    const data = _.get(appState, "admin.agents", []);
    const [showLogs, setShowLogs] = useState(false);
    const [containerId, setContainerId] = useState(null);
    const selectedAgents = _.toArray(appState.admin.selectedAgents);
    const updateSelectedAgents = async () => {
        let tasks = [];
        for (let i = 0; i < _.size(selectedAgents); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    const agent = selectedAgents[i];
                    axios
                        .put(`/containers/agents/agent/${agent}`)
                        .then(() => {
                            resolve(agent);
                        })
                        .catch((error) => {
                            axiosErrorToast(error);
                            reject(agent);
                        });
                })
            );
        }
        const result = await Promise.allSettled(tasks);
        let updatedAgents = new Set();
        for (let i = 0; i < _.size(result); i++) {
            if (_.isEqual(result[i].status, "fulfilled")) {
                updatedAgents.add(result[i].value);
            }
        }
        if (!_.isEmpty(updatedAgents)) {
            const size = _.size(updatedAgents);
            let message = `Updated ${size} agents`;
            if (_.isEqual(size, 1)) {
                message = `Updated ${_.toArray(updatedAgents)[0]} agent`;
            }
            AppToaster.show({ intent: Intent.SUCCESS, message });
        }
    };
    const stopSelectedAgents = async () => {
        let tasks = [];
        for (let i = 0; i < _.size(selectedAgents); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    const agent = selectedAgents[i];
                    axios
                        .delete(`/containers/agents/agent/${agent}`)
                        .then(() => {
                            resolve(agent);
                        })
                        .catch((error) => {
                            axiosErrorToast(error);
                            reject(agent);
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
            if (_.isEqual(size, 1)) {
                message = `Stopped ${_.toArray(stoppedAgents)[0]} agent`;
            }
            AppToaster.show({ intent: Intent.SUCCESS, message });
        }
    };
    const fetchContainerList = () => {
        setLoading(true);
        axios.get("/containers/agents").then((response) => {
            appActions.admin.setAgentList(_.get(response, "data.results", []));
            setLoading(false);
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
                    <Tooltip placement="bottom" minimal content="Pull">
                        <Button
                            intent={Intent.PRIMARY}
                            onClick={updateSelectedAgents}
                            disabled={
                                _.isEmpty(appState.admin.selectedAgents) ||
                                loading
                            }
                            icon={faIcon({ icon: faArrowDownToLine })}
                        />
                    </Tooltip>
                    <Divider />
                    <Popover
                        placement="bottom"
                        content={
                            <div style={{ padding: 15 }}>
                                <Button
                                    onClick={stopSelectedAgents}
                                    className={Classes.POPOVER_DISMISS}
                                    text="Confirm"
                                    intent={Intent.DANGER}
                                />
                            </div>
                        }
                    >
                        <Tooltip placement="bottom" minimal content="Delete">
                            <Button
                                intent={Intent.DANGER}
                                disabled={
                                    _.isEmpty(appState.admin.selectedAgents) ||
                                    loading
                                }
                                icon={faIcon({ icon: faTrash })}
                            />
                        </Tooltip>
                    </Popover>
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
