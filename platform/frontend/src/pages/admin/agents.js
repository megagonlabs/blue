import { CONTAINER_STATUS_INDICATOR } from "@/components/constant";
import { Checkbox, Intent, Tag } from "@blueprintjs/core";
import { Cell, Column, ColumnHeaderCell, Table2 } from "@blueprintjs/table";
import _ from "lodash";
import { useEffect, useState } from "react";
export default function Agents() {
    const [tableKey, setTableKey] = useState(Date.now());
    const array = [
        "created",
        "running",
        "paused",
        "restarting",
        "exited",
        "removing",
        "dead",
    ];
    const [data, setData] = useState([
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
        {
            id: Date.now(),
            hostname: Date.now(),
            created_date: Date.now(),
            image: Date.now(),
            status: array[Math.floor(Math.random() * array.length)],
            agent: Date.now(),
            registry: Date.now(),
        },
    ]);
    useEffect(() => {
        setTableKey(Date.now());
    }, [data]);
    const TABLE_CELL_LINE_HEIGHT = "29px";
    const columns = [
        {
            name: "",
            key: "checkbox",
            cellRenderer: (rowIndex) => (
                <Cell style={{ lineHeight: "28px" }}>
                    <Checkbox large />
                </Cell>
            ),
        },
        { name: "ID", key: "id" },
        { name: "Hostname", key: "hostname" },
        { name: "Created At", key: "created_date" },
        {
            name: "Image",
            key: "image",
            cellRenderer: (rowIndex) => (
                <Cell style={{ lineHeight: TABLE_CELL_LINE_HEIGHT }}>
                    <Tag intent={Intent.PRIMARY} minimal>
                        {_.get(data, [rowIndex, "image"], "-")}
                    </Tag>
                </Cell>
            ),
        },
        {
            name: "Status",
            key: "status",
            cellRenderer: (rowIndex) => {
                const status = _.get(data, [rowIndex, "status"], "-");
                return (
                    <Cell style={{ lineHeight: TABLE_CELL_LINE_HEIGHT }}>
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
    ].map((col, index) => {
        const { name, key, cellRenderer } = col;
        const defaultCellRenderer = (rowIndex) => (
            <Cell style={{ lineHeight: TABLE_CELL_LINE_HEIGHT }}>
                {_.get(data, [rowIndex, key], "-")}
            </Cell>
        );
        const menuRenderer = null;
        const columnHeaderCellRenderer = () => (
            <ColumnHeaderCell
                name={<span style={{ fontWeight: 600 }}>{name}</span>}
                menuRenderer={menuRenderer}
            />
        );
        return (
            <Column
                cellRenderer={
                    _.isFunction(cellRenderer)
                        ? cellRenderer
                        : defaultCellRenderer
                }
                columnHeaderCellRenderer={columnHeaderCellRenderer}
                key={key}
                name={name}
            />
        );
    });
    return (
        <div className="full-parent-width full-parent-height">
            <Table2
                key={tableKey}
                enableRowResizing={false}
                numRows={data.length}
                defaultRowHeight={30}
            >
                {columns}
            </Table2>
        </div>
    );
}
