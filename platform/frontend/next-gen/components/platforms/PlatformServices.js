import { usePlatformStore } from "@/stores/platform-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Divider,
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
    Table,
    TableLoadingOption,
    Utils,
} from "@blueprintjs/table";
import {
    faBellConcierge,
    faRefresh,
    faStop,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import {
    DOCKER_CONTAINER_STATUS_LOOKUP,
    TABLE_CELL_HEIGHT,
} from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import Timestamp from "../Timestamp";
import ServiceCheckbox from "./ServiceCheckbox";
function PlatformServices({ width, height }) {
    const {
        list,
        loading,
        order,
        getServices,
        selected,
        setServiceTableOrder,
        updateServiceTableSelected,
        removeServiceFromList,
    } = usePlatformStore(
        useShallow((state) => ({
            list: state.services.list,
            getServices: state.getServices,
            order: state.services.order,
            loading: state.services.loading,
            selected: state.services.selected,
            setServiceTableOrder: state.setServiceTableOrder,
            updateServiceTableSelected: state.updateServiceTableSelected,
            removeServiceFromList: state.removeServiceFromList,
        }))
    );
    const [tableKey, setTableKey] = useState(Date.now());
    const [deleting, setDeleting] = useState(false);
    const { appToaster, showAxiosErrorToast } = useToaster();
    const handleStopService = () => {
        let promises = [];
        const selectedServices = _.toArray(selected);
        for (let i = 0; i < _.size(selectedServices); i++) {
            const serviceName = selectedServices[i];
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(`/containers/services/service/${serviceName}}`)
                        .then(() => {
                            resolve(serviceName);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(serviceName);
                        });
                })
            );
        }
        setDeleting(true);
        Promise.allSettled(promises)
            .then((results) => {
                let stopped = new Set();
                for (let i = 0; i < _.size(results); i++) {
                    if (_.isEqual(results[i].status, "fulfilled")) {
                        stopped.add(results[i].value);
                        updateServiceTableSelected({
                            id: results[i].value,
                            checked: false,
                        });
                    }
                }
                const size = _.size(stopped);
                if (size > 0) {
                    let message = `Stopped ${size} service${
                        size > 1 ? "s" : ""
                    }`;
                    if (_.isEqual(size, 1)) {
                        message = `Stopped ${_.first(
                            _.toArray(stopped)
                        )} service`;
                    }
                    appToaster.show({ message, intent: Intent.SUCCESS });
                    removeServiceFromList({ ids: stopped });
                }
            })
            .finally(() => {
                setDeleting(false);
            });
    };
    const columns = useMemo(() => {
        return _.sortBy(
            [
                {
                    name: <div>&nbsp;</div>,
                    key: "checkbox",
                    cellRenderer: (rowIndex) => (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            <ServiceCheckbox
                                serviceName={_.get(
                                    list,
                                    [rowIndex, "service"],
                                    null
                                )}
                            />
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
                                    <Timestamp epoch={timestamp} />
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
                { name: "Service", key: "service" },
                { name: "Platform", key: "platform" },
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
        setServiceTableOrder(newOrder);
    };
    useEffect(() => {
        setTableKey(Date.now());
    }, [columns]);
    useEffect(() => {
        getServices();
    }, [getServices]);
    return (
        <div style={{ width, height, position: "relative" }}>
            <div
                className={classNames({ "border-bottom": _.isEmpty(list) })}
                style={{ padding: 10, height: 61 }}
            >
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Button
                        onClick={getServices}
                        loading={loading}
                        icon={<FAIcon icon={faRefresh} />}
                    />
                    <Divider />
                    <Tooltip content="Stop" placement="bottom">
                        <Button
                            onClick={handleStopService}
                            loading={deleting}
                            disabled={_.isEmpty(selected)}
                            intent={Intent.DANGER}
                            icon={<FAIcon icon={faStop} />}
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div style={{ width, height: height - 60 }}>
                {_.isEmpty(list) ? (
                    <NonIdealState
                        title="No Service"
                        icon={<FAIcon icon={faBellConcierge} size={50} />}
                    />
                ) : (
                    <Table
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
                    </Table>
                )}
            </div>
        </div>
    );
}
export default withAutoSizer(PlatformServices);
