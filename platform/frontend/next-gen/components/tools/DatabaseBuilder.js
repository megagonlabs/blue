import { useAppStore } from "@/stores/app-store";
import { useSourceStore } from "@/stores/source-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    EntityTitle,
    H5,
    Intent,
    Menu,
    MenuItem,
    NonIdealState,
    Popover,
    Size,
    TextArea,
    Tooltip,
} from "@blueprintjs/core";
import { faBoxMagnifyingGlass, faPlay } from "@fortawesome/pro-solid-svg-icons";
import {
    faArrowLeft,
    faServer,
    faTable,
    faTableList,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import {
    ENTITY_TYPE_LOOKUP,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import TableVisualizer from "./visualizers/TableVisualizer";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
function DatabaseBuilder({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { data, getSources } = useSourceStore(
        useShallow((state) => ({
            data: state.sources,
            getSources: state.getSources,
        }))
    );
    const [selectedSource, setSelectedSource] = useState(null);
    useEffect(() => {
        getSources();
    }, []);
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(false);
    const [sourceTree, setSourceTree] = useState({});
    const [selectedDatabase, setSelectedDatabase] = useState(null);
    const [selectedCollection, setSelectedCollection] = useState(null);
    const { showAxiosErrorToast } = useToaster();
    useEffect(() => {
        if (_.has(selectedSource, "name")) {
            setConnected(false);
            setLoading(true);
            setSelectedDatabase(null);
            setSelectedCollection(null);
            axios
                .post(
                    `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/data/${selectedSource.name}/connect`
                )
                .then((response) => {
                    setSourceTree(_.get(response, "data.result", {}));
                    setConnected(true);
                })
                .catch((error) => {
                    showAxiosErrorToast(error);
                })
                .finally(() => {
                    setLoading(false);
                });
        }
    }, [selectedSource]);
    const [view, setView] = useState("query-editor");
    const [viewMode, setViewMode] = useState("table");
    const [query, setQuery] = useState("");
    const [queryResults, setQueryResults] = useState(null);
    const runQuery = () => {
        setLoading(true);
        axios
            .post(
                `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/data/${selectedSource.name}/query`,
                {
                    query,
                    database: selectedDatabase,
                    collection: selectedCollection,
                }
            )
            .then((response) => {
                setQueryResults(_.get(response, "data.results", []));
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <div ref={elementRef} style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{
                        overflowY: "auto",
                        minWidth: 226,
                        maxWidth: 226,
                    }}
                    className="border-right"
                >
                    <div
                        className="border-bottom"
                        style={{
                            padding: 10,
                            gap: 10,
                            display: "flex",
                            alignItems: "center",
                        }}
                    >
                        <Popover
                            {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                            boundary={popoverBoundary}
                            placement="bottom"
                            content={
                                <Menu size={Size.LARGE}>
                                    {data.map((source, index) => (
                                        <MenuItem
                                            onClick={() =>
                                                setSelectedSource(
                                                    _.cloneDeep(source)
                                                )
                                            }
                                            key={index}
                                            text={source.name}
                                        />
                                    ))}
                                </Menu>
                            }
                        >
                            <Tooltip
                                {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                                boundary={popoverBoundary}
                                content="Connect"
                                placement="bottom"
                            >
                                <Button
                                    intent={Intent.PRIMARY}
                                    size={Size.LARGE}
                                    variant={ButtonVariant.MINIMAL}
                                    icon={<FAIcon icon={faServer} />}
                                />
                            </Tooltip>
                        </Popover>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ paddingRight: 12 }}
                        >
                            {_.isEmpty(selectedSource) ? (
                                <EntityTitle
                                    ellipsize
                                    heading={H5}
                                    icon={<FAIcon icon={faArrowLeft} />}
                                    title="Select a source"
                                />
                            ) : (
                                <H5
                                    className={classNames(
                                        "margin-0",
                                        Classes.TEXT_OVERFLOW_ELLIPSIS
                                    )}
                                >
                                    {selectedSource.name}
                                </H5>
                            )}
                        </div>
                    </div>
                    <div style={{ padding: 10 }}>
                        <Menu
                            size={Size.LARGE}
                            style={{
                                padding: 0,
                                marginBottom: 10,
                                backgroundColor: "transparent",
                            }}
                        >
                            <Button
                                className="pointer-events-none"
                                alignText={Alignment.START}
                                variant={ButtonVariant.MINIMAL}
                                text={<H5 className="margin-0">Views</H5>}
                            />
                            <Button
                                onClick={() => {
                                    setView("query-editor");
                                }}
                                active={_.isEqual(view, "query-editor")}
                                alignText={Alignment.START}
                                fill
                                variant={ButtonVariant.MINIMAL}
                                icon={<FAIcon icon={faBoxMagnifyingGlass} />}
                                text="Query Editor"
                            />
                        </Menu>
                        <Menu
                            size={Size.LARGE}
                            style={{
                                padding: 0,
                                marginBottom: 10,
                                backgroundColor: "transparent",
                            }}
                        >
                            <Button
                                className="pointer-events-none"
                                alignText={Alignment.START}
                                variant={ButtonVariant.MINIMAL}
                                text={<H5 className="margin-0">Databases</H5>}
                            />
                            {_.keys(sourceTree).map((database, index) => (
                                <Button
                                    key={index}
                                    text={database}
                                    fill
                                    active={_.isEqual(
                                        selectedDatabase,
                                        database
                                    )}
                                    onClick={() => {
                                        setSelectedDatabase(database);
                                        setSelectedCollection(null);
                                    }}
                                    icon={
                                        <FAIcon
                                            icon={
                                                ENTITY_TYPE_LOOKUP["database"]
                                                    .icon
                                            }
                                        />
                                    }
                                    alignText={Alignment.START}
                                    variant={ButtonVariant.MINIMAL}
                                />
                            ))}
                        </Menu>
                        <Menu
                            size={Size.LARGE}
                            style={{
                                padding: 0,
                                backgroundColor: "transparent",
                            }}
                        >
                            <Button
                                className="pointer-events-none"
                                alignText={Alignment.START}
                                variant={ButtonVariant.MINIMAL}
                                text={<H5 className="margin-0">Collections</H5>}
                            />
                            {_.get(sourceTree, selectedDatabase, []).map(
                                (collection, index) => (
                                    <Button
                                        key={index}
                                        text={collection}
                                        fill
                                        active={_.isEqual(
                                            selectedCollection,
                                            collection
                                        )}
                                        onClick={() => {
                                            setSelectedCollection(collection);
                                        }}
                                        icon={
                                            <FAIcon
                                                icon={
                                                    ENTITY_TYPE_LOOKUP[
                                                        "collection"
                                                    ].icon
                                                }
                                            />
                                        }
                                        alignText={Alignment.START}
                                        variant={ButtonVariant.MINIMAL}
                                    />
                                )
                            )}
                        </Menu>
                    </div>
                </div>
                <div
                    className="full-parent-dimension"
                    style={{
                        backgroundColor: darkMode ? Colors.BLACK : null,
                        overflowY: "auto",
                        overflowX: "hidden",
                        display: "flex",
                        flexDirection: "column",
                    }}
                >
                    <div className="border-bottom" style={{ padding: 20 }}>
                        <TextArea
                            value={query}
                            onChange={(event) => {
                                setQuery(event.target.value);
                            }}
                            fill
                            style={{
                                marginBottom: 10,
                                resize: "vertical",
                                minHeight: 120,
                            }}
                        />
                        <Button
                            disabled={!connected}
                            loading={loading}
                            icon={<FAIcon icon={faPlay} />}
                            intent={Intent.SUCCESS}
                            size={Size.LARGE}
                            onClick={runQuery}
                            text="Run Query"
                        />
                    </div>
                    <div className="border-bottom" style={{ padding: 10 }}>
                        <ButtonGroup
                            size={Size.LARGE}
                            variant={ButtonVariant.MINIMAL}
                        >
                            <Tooltip content="Table" placement="bottom">
                                <Button
                                    onClick={() => {
                                        setViewMode("table");
                                    }}
                                    active={_.isEqual(viewMode, "table")}
                                    icon={<FAIcon icon={faTable} />}
                                />
                            </Tooltip>
                        </ButtonGroup>
                    </div>
                    <div style={{ flex: 1, overflow: "auto" }}>
                        {_.isNull(queryResults) && (
                            <NonIdealState
                                title="Run a query to see results"
                                icon={<FAIcon size={50} icon={faTableList} />}
                            />
                        )}
                        {_.isEqual(viewMode, "table") && (
                            <TableVisualizer list={queryResults} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(DatabaseBuilder);
