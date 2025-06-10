import { usePlatformStore } from "@/stores/platform-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Divider,
    H6,
    Intent,
    NonIdealState,
    Size,
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
import { useEffect, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import {
    DOCKER_CONTAINER_STATUS_LOOKUP,
    TABLE_CELL_HEIGHT,
} from "../constants";
import { FAIcon } from "../FAIcon";
import { showAxiosErrorToast } from "../helper";
import withAutoSizer from "../hocs/withAutoSizer";
import Timestamp from "../Timestamp";
import { AppToaster } from "../toaster";
import AgentCheckbox from "./AgentCheckbox";
function PlatformAgents({ width, height }) {
    const { list, loading, order, selected, getAgents, setAgentTableOrder } =
        usePlatformStore(
            useShallow((state) => ({
                list: state.agents.list,
                getAgents: state.getAgents,
                order: state.agents.order,
                loading: state.agents.loading,
                selected: state.agents.selected,
                setAgentTableOrder: state.setAgentTableOrder,
            }))
        );
    const [tableKey, setTableKey] = useState(Date.now());
    const [deleting, setDeleting] = useState(false);
    const columns = useMemo(() => {
        return _.sortBy(
            [
                {
                    name: <div>&nbsp;</div>,
                    key: "checkbox",
                    cellRenderer: (rowIndex) => (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            <AgentCheckbox
                                agentName={_.get(
                                    list,
                                    [rowIndex, "agent"],
                                    null
                                )}
                            />
                        </Cell>
                    ),
                },
                {
                    name: "Action",
                    key: "action",
                    cellRenderer: (rowIndex) => (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            <ButtonGroup
                                variant={ButtonVariant.MINIMAL}
                                style={{ marginTop: 5 }}
                            >
                                <Tooltip content="Logs" placement="bottom">
                                    <Button
                                        icon={
                                            <FAIcon
                                                icon={faRectangleTerminal}
                                            />
                                        }
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
                    cellRenderer: (rowIndex) => {
                        const timestamp = _.get(
                            list,
                            [rowIndex, "created_date"],
                            null
                        );
                        return (
                            <Cell
                                style={{
                                    lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                }}
                            >
                                {!_.isEmpty(timestamp) ? (
                                    <Timestamp date={new Date(timestamp)} />
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
                    cellRenderer: (rowIndex) => (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            <Tag intent={Intent.PRIMARY} minimal>
                                {_.get(list, [rowIndex, "image"], "-")}
                            </Tag>
                        </Cell>
                    ),
                },
                {
                    name: "Status",
                    key: "status",
                    cellRenderer: (rowIndex) => {
                        const status = _.get(list, [rowIndex, "status"], "-");
                        return (
                            <Cell
                                style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}
                            >
                                <Tag
                                    intent={_.get(
                                        DOCKER_CONTAINER_STATUS_LOOKUP,
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
            ],
            (column) => {
                return _.get(order, column.key, Infinity);
            }
        );
    }, [list, order]);
    const handleColumnsReordered = (oldIndex, newIndex, length) => {
        if (_.isEqual(oldIndex, newIndex)) return;
        const newColumns = Utils.reorderArray(
            columns,
            oldIndex,
            newIndex,
            length
        );
        let newOrder = {};
        for (let i = 0; i < _.size(newColumns); i++) {
            _.set(newOrder, newColumns[i].key, i);
        }
        setAgentTableOrder(newOrder);
    };
    useEffect(() => {
        setTableKey(Date.now());
    }, [columns]);
    useEffect(() => {
        getAgents();
    }, []);
    const handlePullAgent = () => {
        let promises = [];
        const selectedAgents = _.toArray(selected);
        for (let i = 0; i < _.size(selectedAgents); i++) {
            const agentName = selectedAgents[i];
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .put(`/containers/agents/agent/${agentName}`)
                        .then(() => {
                            resolve(agentName);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(agentName);
                        });
                })
            );
        }
        Promise.allSettled(promises).then((results) => {
            let updated = new Set();
            for (let i = 0; i < _.size(results); i++) {
                if (_.isEqual("fulfilled", results[i].status)) {
                    updated.add(results[i].value);
                    updateAgentTableSelected({
                        id: results[i].value,
                        checked: false,
                    });
                }
            }
            const size = _.size(updated);
            if (size > 0) {
                let message = `Updated ${size} agent${size > 1 ? "s" : ""}`;
                if (_.isEqual(size, 1)) {
                    message = `Updated ${_.first(_.toArray(updated))} agent`;
                }
                AppToaster.show({ message, intent: Intent.SUCCESS });
                removeServiceFromList({ ids: updated });
            }
        });
    };
    const handleDeleteAgent = () => {
        let promises = [];
        const selectedAgents = _.toArray(selected);
        for (let i = 0; i < _.size(selectedAgents); i++) {
            const agentName = selectedAgents[i];
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(`/containers/agents/agent/${agentName}`)
                        .then(() => {
                            resolve(agentName);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(agentName);
                        });
                })
            );
        }
        setDeleting(true);
        Promise.allSettled(promises)
            .then((results) => {
                let deleted = new Set();
                for (let i = 0; i < _.size(results); i++) {
                    if (_.isEqual("fulfilled", results[i].status)) {
                        deleted.add(results[i].value);
                        updateAgentTableSelected({
                            id: results[i].value,
                            checked: false,
                        });
                    }
                }
                const size = _.size(deleted);
                if (size > 0) {
                    let message = `Deleted ${size} agent${size > 1 ? "s" : ""}`;
                    if (_.isEqual(size, 1)) {
                        message = `Stopped ${_.first(
                            _.toArray(deleted)
                        )} agent`;
                    }
                    AppToaster.show({ message, intent: Intent.SUCCESS });
                    removeServiceFromList({ ids: deleted });
                }
            })
            .finally(() => {
                setDeleting(false);
            });
    };
    return (
        <div style={{ width, height, position: "relative" }}>
            {_.isEmpty(list) ? (
                <NonIdealState
                    title="No Agent"
                    icon={<FAIcon icon={faCircleA} size={50} />}
                />
            ) : (
                <>
                    <div style={{ padding: 10 }}>
                        <ButtonGroup
                            size={Size.LARGE}
                            variant={ButtonVariant.MINIMAL}
                        >
                            <Button
                                onClick={getAgents}
                                loading={loading}
                                icon={<FAIcon icon={faRefresh} />}
                            />
                            <Divider />
                            <H6
                                style={{
                                    lineHeight: "40px",
                                    margin: "0px 10px 0px",
                                }}
                            >
                                Docker
                            </H6>
                            <Tooltip content="Pull" placement="bottom">
                                <Button
                                    onClick={handlePullAgent}
                                    icon={<FAIcon icon={faArrowDownToLine} />}
                                    disabled={_.isEmpty(selected) || deleting}
                                    intent={Intent.PRIMARY}
                                />
                            </Tooltip>
                            <Divider />
                            <Tooltip content="Delete" placement="bottom">
                                <Button
                                    onClick={handleDeleteAgent}
                                    icon={<FAIcon icon={faTrash} />}
                                    disabled={_.isEmpty(selected)}
                                    loading={deleting}
                                    intent={Intent.DANGER}
                                />
                            </Tooltip>
                        </ButtonGroup>
                    </div>
                    <div style={{ width, height: height - 60 }}>
                        <Table2
                            key={tableKey}
                            loadingOptions={
                                loading
                                    ? [
                                          TableLoadingOption.CELLS,
                                          TableLoadingOption.ROW_HEADERS,
                                      ]
                                    : []
                            }
                            onColumnsReordered={handleColumnsReordered}
                            enableColumnReordering
                            numFrozenColumns={1}
                            numRows={_.size(list)}
                            enableRowResizing={false}
                            defaultRowHeight={TABLE_CELL_HEIGHT}
                            rowHeaderCellRenderer={(rowIndex) => (
                                <RowHeaderCell
                                    name={
                                        <div
                                            style={{
                                                textAlign: "center",
                                                lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                            }}
                                        >
                                            {rowIndex + 1}
                                        </div>
                                    }
                                />
                            )}
                        >
                            {columns.map((column, index) => {
                                const { name, key, cellRenderer } = column;
                                const defaultCellRenderer = (rowIndex) => (
                                    <Cell
                                        style={{
                                            lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                        }}
                                    >
                                        {_.get(list, [rowIndex, key], "-")}
                                    </Cell>
                                );
                                const columnHeaderCellRenderer = () => (
                                    <ColumnHeaderCell
                                        name={name}
                                        menuRenderer={null}
                                    />
                                );
                                return (
                                    <Column
                                        key={index}
                                        name={name}
                                        cellRenderer={
                                            _.isFunction(cellRenderer)
                                                ? cellRenderer
                                                : defaultCellRenderer
                                        }
                                        columnHeaderCellRenderer={
                                            columnHeaderCellRenderer
                                        }
                                    />
                                );
                            })}
                        </Table2>
                    </div>
                </>
            )}
        </div>
    );
}
export default withAutoSizer(PlatformAgents);
