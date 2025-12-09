import { TABLE_CELL_HEIGHT } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { Menu, MenuItem, Size } from "@blueprintjs/core";
import {
    Cell,
    Column,
    ColumnHeaderCell,
    RowHeaderCell,
    Table,
    TableLoadingOption,
} from "@blueprintjs/table";
import {
    faArrowDownShortWide,
    faArrowDownWideShort,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useMemo, useState } from "react";
export default function TableVisualizer({ list }) {
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(false);
    const [sortConfig, setSortConfig] = useState({
        column: null,
        direction: "asc", // 'asc' or 'desc'
    });
    useEffect(() => {
        setLoading(true);
        let newColumns = new Set();
        for (let i = 0; i < _.size(list); i++) {
            const keys = _.keys(list[i]);
            for (let j = 0; j < _.size(keys); j++) {
                newColumns.add(keys[j]);
            }
        }
        setColumns(_.toArray(newColumns));
        setLoading(false);
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
    const handleHeaderDoubleClick = (column) => {
        console.log(column);
    };
    return (
        <Table
            cellRendererDependencies={[sortedList]}
            loadingOptions={
                loading
                    ? [
                          TableLoadingOption.CELLS,
                          TableLoadingOption.ROW_HEADERS,
                          TableLoadingOption.COLUMN_HEADERS,
                      ]
                    : []
            }
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
                        cellRenderer={(rowIndex) => (
                            <Cell
                                style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}
                            >
                                {_.get(sortedList, [rowIndex, column], "-")}
                            </Cell>
                        )}
                    />
                );
            })}
        </Table>
    );
}
