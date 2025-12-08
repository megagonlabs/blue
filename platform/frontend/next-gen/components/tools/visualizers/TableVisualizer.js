import { TABLE_CELL_HEIGHT } from "@/components/constants";
import {
    Cell,
    Column,
    RowHeaderCell,
    Table,
    TableLoadingOption,
} from "@blueprintjs/table";
import _ from "lodash";
import { useEffect, useState } from "react";
export default function TableVisualizer({ list }) {
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(false);
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
    return (
        <Table
            cellRendererDependencies={[list]}
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
                return (
                    <Column
                        key={column}
                        name={column}
                        cellRenderer={(rowIndex) => (
                            <Cell
                                style={{ lineHeight: `${TABLE_CELL_HEIGHT}px` }}
                            >
                                {_.get(list, [rowIndex, column], "-")}
                            </Cell>
                        )}
                    />
                );
            })}
        </Table>
    );
}
