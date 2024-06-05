import { CONTAINER_STATUS_INDICATOR } from "@/components/constant";
import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Checkbox,
    Intent,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { Cell, Column, ColumnHeaderCell, Table2 } from "@blueprintjs/table";
import { faStop } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
import ReactTimeAgo from "react-time-ago";
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
    useEffect(() => {
        axios.get("/platform/agents").then((response) => {
            setData(_.get(response, "data.results", []));
        });
    }, []);
    const TABLE_CELL_HEIGHT = 40;
    const columns = [
        {
            name: <span>&nbsp;</span>,
            key: "checkbox",
            cellRenderer: () => (
                <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 2}px` }}>
                    <Checkbox large />
                </Cell>
            ),
        },
        { name: "ID", key: "id" },
        { name: "Hostname", key: "hostname" },
        {
            name: "Created At",
            key: "created_date",
            cellRenderer: (rowIndex) => {
                const timestamp = _.get(data, [rowIndex, "created_date"], null);
                return (
                    <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
                        {!_.isEmpty(timestamp) ? (
                            <ReactTimeAgo
                                date={new Date(timestamp)}
                                locale="en-US"
                            />
                        ) : null}
                    </Cell>
                );
            },
        },
        {
            name: "Image",
            key: "image",
            cellRenderer: (rowIndex) => (
                <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
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
                    <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
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
            <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
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
                key={`${key}-${index}`}
                name={name}
            />
        );
    });
    return (
        <>
            <div style={{ padding: 5, height: 50 }}>
                <ButtonGroup large minimal>
                    <Tooltip placement="bottom-start" minimal content="Stop">
                        <Button disabled icon={faIcon({ icon: faStop })} />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div style={{ height: "calc(100% - 50px)" }}>
                <Table2
                    key={tableKey}
                    enableRowResizing={false}
                    enableColumnReordering
                    numRows={data.length}
                    defaultRowHeight={TABLE_CELL_HEIGHT}
                >
                    {columns}
                </Table2>
            </div>
        </>
    );
}
