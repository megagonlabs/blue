import AccessDeniedNonIdealState from "@/components/AccessDeniedNonIdealState";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import Pagination from "@/components/registry/Pagination";
import RegistryList from "@/components/registry/RegistryList";
import {
    Button,
    Checkbox,
    Classes,
    ControlGroup,
    Divider,
    H4,
    InputGroup,
    Intent,
    Popover,
    Radio,
    RadioGroup,
    Tag,
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faSearch,
    faTimes,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useMemo, useState } from "react";
export default function Model() {
    const { appState, appActions } = useContext(AppContext);
    const { filter } = appState.model;
    const [hybrid, setHybrid] = useState(filter.hybrid);
    const [approximate, setApproximate] = useState(filter.approximate);
    const [type, setType] = useState(filter.type);
    const [keywords, setKeywords] = useState(filter.keywords);
    const [page, setPage] = useState(filter.page);
    const [pageSize, setPageSize] = useState(filter.page_size);
    const modelRegistryName = appState.model.registryName;
    const debounceOnKeywordsChange = useMemo(
        () =>
            _.debounce(
                ({
                    registryName,
                    hybrid,
                    approximate,
                    keywords,
                    type,
                    page,
                    pageSize,
                }) => {
                    appActions.model.setState({ key: "loading", value: true });
                    if (_.isEmpty(keywords)) {
                        appActions.model.getList(modelRegistryName);
                    } else {
                        appActions.model.searchList({
                            registryName: registryName,
                            hybrid: hybrid,
                            approximate: approximate,
                            keywords: keywords,
                            type: type,
                            page: page,
                            pageSize: pageSize,
                        });
                    }
                },
                300
            ),
        [] // eslint-disable-line react-hooks/exhaustive-deps
    );
    useEffect(() => {
        debounceOnKeywordsChange({
            registryName: modelRegistryName,
            hybrid,
            approximate,
            keywords,
            type,
            page,
            pageSize,
        });
    }, [hybrid, approximate, type, page, pageSize]); // eslint-disable-line react-hooks/exhaustive-deps
    const { permissions } = useContext(AuthContext);
    if (!permissions.canReadModelRegistry) {
        return <AccessDeniedNonIdealState />;
    }
    return (
        <>
            <div style={{ padding: "20px 20px 10px 20px", display: "flex" }}>
                <H4 style={{ margin: "0px 10px 0px 0px" }}>Model Registry</H4>
                <Tag minimal intent={Intent.PRIMARY}>
                    {modelRegistryName}
                </Tag>
            </div>
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    width: "100%",
                    padding: "0px 20px 10px 20px",
                }}
            >
                <div
                    style={{
                        maxWidth: 690,
                        width: "calc(100% - 224px - 40px)",
                    }}
                >
                    <ControlGroup fill>
                        <InputGroup
                            id="model-registry-search-input"
                            placeholder="Search models"
                            className={
                                appState.model.loading ? Classes.SKELETON : null
                            }
                            size="large"
                            fill
                            value={keywords}
                            leftIcon={faIcon({ icon: faSearch })}
                            onChange={(event) => {
                                setKeywords(event.target.value);
                            }}
                            rightElement={
                                !_.isEmpty(keywords) ||
                                appState.model.search ? (
                                    <Button
                                        variant="minimal"
                                        onClick={() => {
                                            setKeywords("");
                                            setPage(0);
                                            setPageSize(10);
                                            appActions.model.setState({
                                                key: "loading",
                                                value: true,
                                            });
                                            appActions.model.getList(
                                                modelRegistryName
                                            );
                                        }}
                                        icon={faIcon({ icon: faTimes })}
                                    />
                                ) : null
                            }
                            onKeyDown={(event) => {
                                if (_.isEqual(event.key, "Enter")) {
                                    debounceOnKeywordsChange({
                                        registryName: modelRegistryName,
                                        hybrid,
                                        approximate,
                                        keywords: event.target.value,
                                        type,
                                        page,
                                        pageSize,
                                    });
                                }
                            }}
                        />
                        <Popover
                            minimal
                            placement="bottom-end"
                            content={
                                <div
                                    style={{
                                        padding: "15px 15px 5px",
                                        maxWidth: 500,
                                    }}
                                >
                                    <Checkbox
                                        className={
                                            appState.model.loading
                                                ? Classes.SKELETON
                                                : null
                                        }
                                        inline
                                        size="large"
                                        checked={hybrid}
                                        label="Hybrid"
                                        onChange={(event) => {
                                            if (event.target.checked) {
                                                setApproximate(false);
                                            }
                                            setHybrid(event.target.checked);
                                        }}
                                    />
                                    <Checkbox
                                        className={
                                            appState.model.loading
                                                ? Classes.SKELETON
                                                : null
                                        }
                                        inline
                                        size="large"
                                        checked={approximate}
                                        label="Approximate"
                                        onChange={(event) => {
                                            if (event.target.checked) {
                                                setHybrid(false);
                                            }
                                            setApproximate(
                                                event.target.checked
                                            );
                                        }}
                                    />
                                    <Divider />
                                    <RadioGroup
                                        selectedValue={type}
                                        inline
                                        label="Type"
                                        onChange={(event) => {
                                            setType(event.currentTarget.value);
                                        }}
                                    >
                                        {[
                                            { value: "", text: "All" },
                                            { value: "model", text: "Model" },
                                        ].map(({ value, text }, index) => (
                                            <Radio
                                                key={index}
                                                className={
                                                    appState.model.loading
                                                        ? Classes.SKELETON
                                                        : null
                                                }
                                                size="large"
                                                value={value}
                                                label={text}
                                            />
                                        ))}
                                    </RadioGroup>
                                </div>
                            }
                        >
                            <Button
                                className={
                                    appState.model.loading
                                        ? Classes.SKELETON
                                        : null
                                }
                                size="large"
                                variant="outlined"
                                intent={Intent.PRIMARY}
                                text="Filter"
                                endIcon={faIcon({ icon: faBarsFilter })}
                            />
                        </Popover>
                    </ControlGroup>
                </div>
                {appState.model.search ? (
                    <Pagination
                        page={page}
                        setPage={setPage}
                        pageSize={pageSize}
                        setPageSize={setPageSize}
                        type="model"
                    />
                ) : null}
            </div>
            <div style={{ height: "calc(100% - 101px)" }}>
                <H4 style={{ margin: "0px 0px 10px 20px" }}>
                    {appState.model.search ? "Search Results" : "Contents"}
                </H4>
                <div style={{ height: "calc(100% - 31px)", overflowY: "auto" }}>
                    <RegistryList type="model" />
                </div>
            </div>
        </>
    );
}
