import { useDedupStore } from "@/stores/dedup-store";
import { usePlatformStore } from "@/stores/platform-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Divider,
    Intent,
    Overlay2,
    Size,
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
import { faRefresh, faStamp } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { TABLE_CELL_HEIGHT, USER_ROLES_LOOKUP } from "../constants";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import UserAvatar from "../sessions/UserAvatar";
import UserCheckbox from "./UserCheckbox";
import UserRoleConfiguration from "./UserRoleConfiguration";
function PlatformUsers({ width, height }) {
    const { list, getUsers, loading, setUserTableOrder, order, selected } =
        usePlatformStore(
            useShallow((state) => ({
                list: state.users.list,
                order: state.users.order,
                selected: state.users.selected,
                getUsers: state.getUsers,
                loading: state.users.loading,
                setUserTableOrder: state.setUserTableOrder,
            }))
        );
    const getUserProfileById = useDedupStore(
        (state) => state.getUserProfileById
    );
    const columns = useMemo(() => {
        return _.sortBy(
            [
                {
                    name: <div>&nbsp;</div>,
                    key: "checkbox",
                    cellRenderer: (rowIndex) => (
                        <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}>
                            <UserCheckbox
                                uid={_.get(list, [rowIndex, "uid"], null)}
                            />
                        </Cell>
                    ),
                },
                { name: "UID", key: "uid" },
                {
                    name: "Name",
                    key: "name",
                    cellRenderer: (rowIndex) => {
                        const uid = _.get(list, [rowIndex, "uid"], null);
                        getUserProfileById(uid);
                        const name = _.get(list, [rowIndex, "name"], "-");
                        return (
                            <Cell
                                style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}
                            >
                                <div
                                    className="full-parent-width"
                                    style={{
                                        display: "flex",
                                        gap: 10,
                                        alignItems: "center",
                                    }}
                                >
                                    <div style={{ width: 25 }}>
                                        <UserAvatar userId={uid} size={25} />
                                    </div>
                                    <div
                                        className={
                                            Classes.TEXT_OVERFLOW_ELLIPSIS
                                        }
                                    >
                                        {name}
                                    </div>
                                </div>
                            </Cell>
                        );
                    },
                },
                { name: "Email", key: "email" },
                {
                    name: "Role",
                    key: "role",
                    cellRenderer: (rowIndex) => {
                        const role = _.get(list, [rowIndex, "role"], "-");
                        return (
                            <Cell
                                style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}
                            >
                                {_.get(USER_ROLES_LOOKUP, [role, "text"], role)}
                            </Cell>
                        );
                    },
                },
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
        setUserTableOrder(newOrder);
    };
    useEffect(() => {
        getUsers();
    }, []);
    const [tableKey, setTableKey] = useState(Date.now());
    useEffect(() => {
        setTableKey(Date.now());
    }, [columns]);
    const [showUserRoleConfiguration, setShowUserRoleConfiguration] =
        useState(false);
    return (
        <div style={{ width, height, position: "relative" }}>
            <Overlay2
                onClose={() => {
                    setShowUserRoleConfiguration(false);
                }}
                isOpen={showUserRoleConfiguration}
                usePortal={false}
                enforceFocus={false}
                transitionDuration={0}
            >
                <div
                    className="custom-card center-center"
                    style={{
                        width: 650,
                        height: "calc(100% - 40px)",
                        maxWidth: "calc(100% - 40px)",
                    }}
                >
                    <UserRoleConfiguration
                        setShowUserRoleConfiguration={
                            setShowUserRoleConfiguration
                        }
                    />
                </div>
            </Overlay2>
            <div style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Button
                        loading={loading}
                        onClick={getUsers}
                        icon={<FAIcon icon={faRefresh} />}
                    />
                    <Divider />
                    <Tooltip
                        openOnTargetFocus={false}
                        content={`Update role${
                            _.size(selected) > 1 ? "s" : ""
                        }`}
                        placement="bottom"
                    >
                        <Button
                            onClick={() => {
                                setShowUserRoleConfiguration(true);
                            }}
                            disabled={_.isEmpty(selected)}
                            intent={Intent.SUCCESS}
                            icon={<FAIcon icon={faStamp} />}
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
                            <ColumnHeaderCell name={name} menuRenderer={null} />
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
        </div>
    );
}
export default withAutoSizer(PlatformUsers);
