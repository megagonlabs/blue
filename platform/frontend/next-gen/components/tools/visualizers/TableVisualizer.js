import { TABLE_CELL_HEIGHT } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { Colors, Menu, MenuItem, Size } from "@blueprintjs/core";
import {
    Cell,
    Column,
    ColumnHeaderCell,
    RowHeaderCell,
    Table,
} from "@blueprintjs/table";
import {
    faArrowDownShortWide,
    faArrowDownWideShort,
    faCircleCheck,
    faCircleXmark,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useMemo, useState } from "react";
export default function TableVisualizer({ list }) {
    const [sortConfig, setSortConfig] = useState({
        column: null,
        direction: "asc", // 'asc' or 'desc'
    });
    const columns = useMemo(() => {
        if (_.isEmpty(list)) return [];
        let newColumns = new Set();
        for (let i = 0; i < _.size(list); i++) {
            const keys = _.keys(list[i]);
            for (let j = 0; j < _.size(keys); j++) {
                newColumns.add(keys[j]);
            }
        }
        return _.toArray(newColumns);
    }, [list]);
    const sortedList = useMemo(() => {
        if (!sortConfig.column) {
            return list;
        }
        return _.orderBy(list, [sortConfig.column], [sortConfig.direction]);
    }, [list, sortConfig]);
    const handleSort = (column, direction) => {
        setSortConfig({ column, direction });
    };
    const renderMenu = (column) => {
        return (
            <Menu size={Size.LARGE}>
                <MenuItem
                    icon={<FAIcon icon={faArrowDownShortWide} />}
                    text="Sort Asc"
                    onClick={() => handleSort(column, "asc")}
                    active={
                        sortConfig.column === column &&
                        sortConfig.direction === "asc"
                    }
                />
                <MenuItem
                    icon={<FAIcon icon={faArrowDownWideShort} />}
                    text="Sort Desc"
                    onClick={() => handleSort(column, "desc")}
                    active={
                        sortConfig.column === column &&
                        sortConfig.direction === "desc"
                    }
                />
            </Menu>
        );
    };
    const CellData = ({ data }) => {
        if (_.isBoolean(data)) {
            return (
                <FAIcon
                    style={{
                        marginTop: 12,
                        color: data ? Colors.GREEN3 : Colors.RED3,
                    }}
                    icon={data ? faCircleCheck : faCircleXmark}
                />
            );
        }
        return data;
    };
    return (
        <Table
            cellRendererDependencies={[sortedList]}
            enableRowResizing={false}
            numRows={_.size(list)}
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
            {columns.map((column) => {
                const columnHeaderCellRenderer = () => (
                    <ColumnHeaderCell
                        name={column}
                        menuRenderer={() => renderMenu(column)}
                    />
                );
                return (
                    <Column
                        key={column}
                        name={column}
                        columnHeaderCellRenderer={columnHeaderCellRenderer}
                        cellRenderer={(rowIndex) => {
                            const data = _.get(
                                sortedList,
                                [rowIndex, column],
                                "-"
                            );
                            return (
                                <Cell
                                    style={{
                                        lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                    }}
                                >
                                    <CellData data={data} />
                                </Cell>
                            );
                        }}
                    />
                );
            })}
        </Table>
    );
}
