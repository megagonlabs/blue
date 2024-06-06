import { CONTAINER_STATUS_INDICATOR } from "@/components/constant";
import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Checkbox,
    Divider,
    Intent,
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
import { faRefresh, faStop } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
import ReactTimeAgo from "react-time-ago";
export default function Agents() {
    const [tableKey, setTableKey] = useState(Date.now());
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);
    useEffect(() => {
        setTableKey(Date.now());
    }, [data]);
    const fetchContainerList = () => {
        setLoading(true);
        axios.get("/platform/agents").then((response) => {
            setData(_.get(response, "data.results", []));
            setLoading(false);
        });
    };
    useEffect(() => {
        fetchContainerList();
    }, []);
    const TABLE_CELL_HEIGHT = 40;
    const columns = [
        {
            name: "",
            key: "checkbox",
            cellRenderer: () => (
                <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
                    <Checkbox large className="margin-0" />
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
                    <Divider />
                    <Tooltip placement="bottom" minimal content="Refresh">
                        <Button
                            intent={Intent.PRIMARY}
                            onClick={fetchContainerList}
                            icon={faIcon({ icon: faRefresh })}
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div style={{ height: "calc(100% - 50px)" }}>
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
                    {columns}
                </Table2>
            </div>
        </>
    );
}
