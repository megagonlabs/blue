import { AppContext } from "@/components/app-context";
import { faIcon } from "@/components/icon";
import RegistryList from "@/components/registry/RegistryList";
import {
    Button,
    Checkbox,
    ControlGroup,
    Divider,
    H4,
    InputGroup,
    Popover,
    Radio,
    RadioGroup,
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faSearch,
    faTimes,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useContext, useEffect, useState } from "react";
export default function Agents() {
    const { appState, appActions } = useContext(AppContext);
    const [hybrid, setHybrid] = useState(appState.agent.filter.hybrid);
    const [approximate, setApproximate] = useState(
        appState.agent.filter.approximate
    );
    const [type, setType] = useState(appState.agent.filter.type);
    const [keywords, setKeywords] = useState(appState.agent.filter.keywords);
    useEffect(() => {
        if (appState.agent.search) return;
        appActions.agent.getList();
    }, []);
    const debounceOnKeywordsChange = useCallback(
        _.debounce(({ registryName, hybrid, approximate, keywords, type }) => {
            if (_.isEmpty(keywords)) {
                appActions.agent.getList();
            } else {
                appActions.agent.searchList({
                    registryName: registryName,
                    hybrid: hybrid,
                    approximate: approximate,
                    keywords: keywords,
                    type: type,
                    page: 0,
                    pageSize: 10,
                });
            }
        }, 500),
        []
    );
    useEffect(() => {
        debounceOnKeywordsChange({
            registryName: appState.agent.registryName,
            hybrid,
            approximate,
            keywords,
            type,
        });
    }, [hybrid, approximate, type]);
    return (
        <>
            <div style={{ padding: "20px 20px 10px 20px" }}>
                <H4 style={{ margin: "0px 20px 0px 0px" }}>Agents Registry</H4>
            </div>
            <div style={{ padding: "0px 20px 10px 20px", maxWidth: 690 }}>
                <ControlGroup fill>
                    <InputGroup
                        large
                        fill
                        value={keywords}
                        leftIcon={faIcon({ icon: faSearch })}
                        onChange={(event) => {
                            setKeywords(event.target.value);
                        }}
                        rightElement={
                            !_.isEmpty(keywords) && appState.agent.search ? (
                                <Button
                                    minimal
                                    onClick={() => {
                                        setKeywords("");
                                        debounceOnKeywordsChange({
                                            registryName:
                                                appState.agent.registryName,
                                            hybrid,
                                            approximate,
                                            keywords: "",
                                            type,
                                        });
                                    }}
                                    icon={faIcon({ icon: faTimes })}
                                />
                            ) : null
                        }
                        onKeyDown={(event) => {
                            if (_.isEqual(event.key, "Enter")) {
                                debounceOnKeywordsChange({
                                    registryName: appState.agent.registryName,
                                    hybrid,
                                    approximate,
                                    keywords: event.target.value,
                                    type,
                                });
                            }
                        }}
                    />
                    <Popover
                        minimal
                        placement="bottom-end"
                        content={
                            <div style={{ padding: "20px 20px 10px" }}>
                                <Checkbox
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
                                    inline
                                    large
                                    checked={approximate}
                                    label="Approximate"
                                    onChange={(event) => {
                                        if (event.target.checked) {
                                            setHybrid(false);
                                        }
                                        setApproximate(event.target.checked);
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
                                    <Radio large value="agent" label="Agent" />
                                    <Radio large value="input" label="Input" />
                                    <Radio
                                        large
                                        value="output"
                                        label="Output"
                                    />
                                </RadioGroup>
                            </div>
                        }
                    >
                        <Button
                            large
                            outlined
                            text="Filter"
                            rightIcon={faIcon({ icon: faBarsFilter })}
                        />
                    </Popover>
                </ControlGroup>
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
