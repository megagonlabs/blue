import { AppContext } from "@/components/app-context";
import { faIcon } from "@/components/icon";
import RegistryList from "@/components/registry/RegistryList";
import {
    Button,
    Checkbox,
    ControlGroup,
    Divider,
    H4,
    HTMLSelect,
    InputGroup,
    Popover,
    Radio,
    RadioGroup,
} from "@blueprintjs/core";
import { faBarsFilter, faSearch } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useContext, useEffect, useState } from "react";
export default function Agents() {
    const { appState, appActions } = useContext(AppContext);
    const [hybrid, setHybrid] = useState(true);
    const [approximate, setApproximate] = useState(false);
    const [type, setType] = useState("agent");
    const [keywords, setKeywords] = useState("");
    useEffect(() => {
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
            <div
                style={{
                    padding: "20px 20px 10px 20px",
                    display: "flex",
                    alignItems: "center",
                }}
            >
                <H4 style={{ margin: "0px 20px 0px 0px" }}>Agents Registry</H4>
                <HTMLSelect minimal value={appState.data.registryName}>
                    <option value="">default</option>
                </HTMLSelect>
            </div>
            <div
                style={{
                    padding: "0px 20px 10px 20px",
                    maxWidth: 690,
                }}
            >
                <ControlGroup fill>
                    <InputGroup
                        large
                        fill
                        value={keywords}
                        onChange={(event) => {
                            setKeywords(event.target.value);
                        }}
                        leftIcon={faIcon({ icon: faSearch })}
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
            <div
                style={{
                    height: "calc(100% - 110px)",
                    overflowY: "auto",
                }}
            >
                <RegistryList type="agent" />
            </div>
        </>
    );
}
