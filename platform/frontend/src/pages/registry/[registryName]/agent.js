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
import { useCallback, useContext, useEffect, useState } from "react";
export default function Agent() {
    const { appState, appActions } = useContext(AppContext);
    const { filter } = appState.agent;
    const [hybrid, setHybrid] = useState(filter.hybrid);
    const [approximate, setApproximate] = useState(filter.approximate);
    const [type, setType] = useState(filter.type);
    const [keywords, setKeywords] = useState(filter.keywords);
    const [page, setPage] = useState(filter.page);
    const [pageSize, setPageSize] = useState(filter.page_size);
    const agentRegistryName = process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME;
    const debounceOnKeywordsChange = useCallback(
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
                appActions.agent.setState({ key: "loading", value: true });
                if (_.isEmpty(keywords)) {
                    appActions.agent.getList(agentRegistryName);
                } else {
                    appActions.agent.searchList({
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
        []
    );
    useEffect(() => {
        debounceOnKeywordsChange({
            registryName: agentRegistryName,
            hybrid,
            approximate,
            keywords,
            type,
            page,
            pageSize,
        });
    }, [hybrid, approximate, type, page, pageSize]);
    const { permissions } = useContext(AuthContext);
    if (!permissions.canReadAgentRegistry) {
        return <AccessDeniedNonIdealState />;
    }
    return (
        <>
            <div style={{ padding: "20px 20px 10px 20px", display: "flex" }}>
                <H4 style={{ margin: "0px 10px 0px 0px" }}>Agents Registry</H4>
                <Tag minimal intent={Intent.PRIMARY}>
                    {agentRegistryName}
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
                        width: "calc(100% - 250px - 40px)",
                    }}
                >
                    <ControlGroup fill>
                        <InputGroup
                            id="agent-registry-search-input"
                            placeholder="Search agents"
                            className={
                                appState.agent.loading ? Classes.SKELETON : null
                            }
                            large
                            fill
                            value={keywords}
                            leftIcon={faIcon({ icon: faSearch })}
                            onChange={(event) => {
                                setKeywords(event.target.value);
                            }}
                            rightElement={
                                !_.isEmpty(keywords) ||
                                appState.agent.search ? (
                                    <Button
                                        minimal
                                        onClick={() => {
                                            setKeywords("");
                                            setPage(0);
                                            setPageSize(10);
                                            appActions.agent.setState({
                                                key: "loading",
                                                value: true,
                                            });
                                            appActions.agent.getList(
                                                agentRegistryName
                                            );
                                        }}
                                        icon={faIcon({ icon: faTimes })}
                                    />
                                ) : null
                            }
                            onKeyDown={(event) => {
                                if (_.isEqual(event.key, "Enter")) {
                                    debounceOnKeywordsChange({
                                        registryName: agentRegistryName,
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
                                        padding: "20px 20px 10px",
                                        maxWidth: 500,
                                    }}
                                >
                                    <Checkbox
                                        className={
                                            appState.agent.loading
                                                ? Classes.SKELETON
                                                : null
                                        }
                                        inline
                                        large
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
                                            appState.agent.loading
                                                ? Classes.SKELETON
                                                : null
                                        }
                                        inline
                                        large
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
                                            { value: "agent", text: "Agent" },
                                            { value: "input", text: "Input" },
                                            { value: "output", text: "Output" },
                                        ].map(({ value, text }, index) => {
                                            return (
                                                <Radio
                                                    key={index}
                                                    className={
                                                        appState.agent.loading
                                                            ? Classes.SKELETON
                                                            : null
                                                    }
                                                    large
                                                    value={value}
                                                    label={text}
                                                />
                                            );
                                        })}
                                    </RadioGroup>
                                </div>
                            }
                        >
                            <Button
                                className={
                                    appState.agent.loading
                                        ? Classes.SKELETON
                                        : null
                                }
                                large
                                outlined
                                text="Filter"
                                rightIcon={faIcon({ icon: faBarsFilter })}
                            />
                        </Popover>
                    </ControlGroup>
                </div>
                {appState.agent.search ? (
                    <Pagination
                        page={page}
                        setPage={setPage}
                        pageSize={pageSize}
                        setPageSize={setPageSize}
                        type="agent"
                    />
                ) : null}
            </div>
            <div style={{ height: "calc(100% - 101px)" }}>
                <H4 style={{ margin: "0px 0px 10px 20px" }}>
                    {appState.agent.search ? "Search Results" : "Contents"}
                </H4>
                <div style={{ height: "calc(100% - 31px)", overflowY: "auto" }}>
                    <RegistryList type="agent" />
                </div>
            </div>
        </>
    );
}
