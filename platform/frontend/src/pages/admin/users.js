import AccessDeniedNonIdealState from "@/components/AccessDeniedNonIdealState";
import ActionCheckbox from "@/components/admin/ActionCheckbox";
import RoleConfigurationPopover from "@/components/admin/RoleConfigurationPopover";
import { PROFILE_PICTURE_40, USER_ROLES_LOOKUP } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    Divider,
    NonIdealState,
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
    faRefresh,
    faStamp,
    faUserGroup,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Image from "next/image";
import { useContext, useEffect, useState } from "react";
export default function Users() {
    const [tableKey, setTableKey] = useState(Date.now());
    const [loading, setLoading] = useState(true);
    const [isRoleConfigOpen, setIsRoleConfigOpen] = useState(false);
    const { appState, appActions } = useContext(AppContext);
    const data = _.get(appState, "admin.users", []);
    const fetchUserList = () => {
        setLoading(true);
        axios.get("/accounts/users").then((response) => {
            appActions.admin.setUserList(_.get(response, "data.users", []));
            setLoading(false);
        });
    };
    useEffect(() => {
        appActions.admin.setState({ key: "selectedUsers", value: new Set() });
        fetchUserList();
    }, []);
    const TABLE_CELL_HEIGHT = 55;
    const INIT_COLUMNS = [
        {
            name: <div>&nbsp;</div>,
            key: "checkbox",
            cellRenderer: ({ rowIndex, data }) => (
                <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
                    <ActionCheckbox rowIndex={rowIndex} data={data} />
                </Cell>
            ),
        },
        { name: "UID", key: "uid" },
        {
            name: "Name",
            key: "name",
            cellRenderer: ({ rowIndex, data }) => {
                const picture = _.get(data, [rowIndex, "picture"], "");
                const name = _.get(data, [rowIndex, "name"], "-");
                return (
                    <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
                        <div
                            className="full-parent-width"
                            style={{ position: "relative" }}
                        >
                            <Card
                                className="margin-0"
                                style={{
                                    ...PROFILE_PICTURE_40,
                                    position: "absolute",
                                    top: 7.5,
                                    left: 1,
                                }}
                            >
                                <Image
                                    alt=""
                                    src={picture}
                                    width={40}
                                    height={40}
                                />
                            </Card>
                            <div
                                style={{ paddingLeft: 52 }}
                                className={Classes.TEXT_OVERFLOW_ELLIPSIS}
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
            cellRenderer: ({ rowIndex, data }) => {
                const role = _.get(data, [rowIndex, "role"], "-");
                return (
                    <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
                        {_.get(USER_ROLES_LOOKUP, [role, "text"], role)}
                    </Cell>
                );
            },
        },
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
    if (!permissions.canWritePlatformUsers) {
        return <AccessDeniedNonIdealState />;
    }
    return (
        <>
            <RoleConfigurationPopover
                setIsRoleConfigOpen={setIsRoleConfigOpen}
                isRoleConfigOpen={isRoleConfigOpen}
            />
            <Card interactive style={{ padding: 5, borderRadius: 0 }}>
                <ButtonGroup large minimal>
                    <Tooltip placement="bottom-start" minimal content="Refresh">
                        <Button
                            onClick={fetchUserList}
                            loading={loading}
                            icon={faIcon({ icon: faRefresh })}
                        />
                    </Tooltip>
                    <Divider />
                    <Tooltip
                        placement="bottom"
                        content="Update role(s)"
                        minimal
                    >
                        <Button
                            disabled={
                                _.isEmpty(appState.admin.selectedUsers) ||
                                loading
                            }
                            onClick={() => setIsRoleConfigOpen(true)}
                            icon={faIcon({ icon: faStamp })}
                        />
                    </Tooltip>
                </ButtonGroup>
            </Card>
            {_.isEmpty(data) ? (
                <div
                    className="full-parent-width"
                    style={{
                        position: "absolute",
                        bottom: 0,
                        right: 0,
                        zIndex: 1,
                        height: "calc(100% - 50px)",
                    }}
                >
                    <NonIdealState
                        title="No User"
                        icon={faIcon({ icon: faUserGroup, size: 50 })}
                    />
                </div>
            ) : (
                <div style={{ height: "calc(100% - 50px)" }}>
                    <Table2
                        minColumnWidth={62}
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
                </div>
            )}
        </>
    );
}
