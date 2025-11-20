import {
    HEX_TRANSPARENCY,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "@/components/constants";
import { CardListCallout } from "@/components/ux/CardListCallout";
import { useAgentStore } from "@/stores/agent-store";
import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonVariant,
    Colors,
    ControlGroup,
    InputGroup,
    Intent,
    Overlay2,
    Radio,
    RadioGroup,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faSearch } from "@fortawesome/pro-solid-svg-icons";
import {
    faBarsFilter,
    faEraser,
    faPlus,
    faRefresh,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _, { debounce } from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../../FAIcon";
import withAutoSizer from "../../hocs/withAutoSizer";
import FilterPane from "../FilterPane";
import NewEntity from "../NewEntity";
import RegistryEntityCard from "../RegistryEntityCard";
import RegistryEntityContainer from "../RegistryEntityContainer";
import SearchResultCard from "../SearchResultCard";
function AgentList({ width, height }) {
    const { agents, getAgents, filter, setFilterValue, search } = useAgentStore(
        useShallow((state) => ({
            agents: state.agents,
            getAgents: state.getAgents,
            filter: state.filter,
            search: state.search,
            setFilterValue: state.setFilterValue,
        }))
    );
    const [showFilter, setShowFilter] = useState(false);
    const { permissions } = useAuthStore(
        useShallow((state) => ({
            permissions: state.permissions,
        }))
    );
    const darkMode = useAppStore((state) => state.dark_mode);
    const [showNewEntity, setShowNewEntity] = useState(false);
    const { addContainer } = useGridStore(
        useShallow((state) => ({ addContainer: state.addContainer }))
    );
    useEffect(() => {
        getAgents();
    }, [getAgents]);
    const debounced = useCallback(debounce(getAgents, 800), [getAgents]);
    useEffect(() => {
        debounced();
    }, [filter]);
    const callback = (entity) => {
        setShowNewEntity(false);
        addContainer({
            content: <RegistryEntityContainer entity={entity} />,
        });
    };
    const elementRef = useRef(null);
    return (
        <div ref={elementRef} style={{ width, height }}>
            {showFilter && (
                <div
                    className="full-parent-dimension"
                    onClick={() => {
                        setShowFilter(false);
                    }}
                    style={{
                        position: "absolute",
                        zIndex: 1,
                        maxHeight: "calc(100% - 45px)",
                        backgroundColor: `${Colors.BLACK}${HEX_TRANSPARENCY[70]}`,
                    }}
                />
            )}
            <Overlay2
                onClose={() => {
                    setShowNewEntity(false);
                }}
                isOpen={showNewEntity}
                usePortal={false}
                enforceFocus={false}
                transitionDuration={0}
            >
                <div
                    className="custom-card center-center"
                    style={{
                        width: 800,
                        padding: 20,
                        overflowY: "auto",
                        height: "calc(100% - 40px)",
                        maxWidth: "calc(100% - 40px)",
                    }}
                >
                    <NewEntity callback={callback} type="agent" />
                </div>
            </Overlay2>
            <div
                className="full-parent-dimension"
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                    backgroundColor: darkMode ? Colors.BLACK : null,
                }}
            >
                <FilterPane
                    showFilter={showFilter}
                    setShowFilter={setShowFilter}
                >
                    <RadioGroup
                        style={{ marginTop: 20 }}
                        selectedValue={_.get(
                            filter,
                            "searchType",
                            "approximate"
                        )}
                        onChange={(event) => {
                            setFilterValue({
                                key: "searchType",
                                value: event.currentTarget.value,
                            });
                        }}
                    >
                        <Radio
                            size={Size.LARGE}
                            label="Hybrid"
                            value="hybrid"
                        />
                        <Radio
                            size={Size.LARGE}
                            label="Approximate"
                            value="approximate"
                        />
                    </RadioGroup>
                    <RadioGroup
                        label="Type"
                        style={{ marginTop: 20 }}
                        selectedValue={_.get(filter, "type", "")}
                        onChange={(event) => {
                            setFilterValue({
                                key: "type",
                                value: event.currentTarget.value,
                            });
                        }}
                    >
                        <Radio size={Size.LARGE} label="All" value="" />
                        <Radio size={Size.LARGE} label="Agent" value="agent" />
                        <Radio size={Size.LARGE} label="Input" value="input" />
                        <Radio
                            size={Size.LARGE}
                            label="Output"
                            value="output"
                        />
                    </RadioGroup>
                </FilterPane>
                <ControlGroup>
                    <Button
                        size={Size.LARGE}
                        icon={<FAIcon icon={faRefresh} />}
                        variant={ButtonVariant.MINIMAL}
                        onClick={getAgents}
                    />
                    <Tooltip
                        openOnTargetFocus={false}
                        placement="bottom"
                        content="Filter"
                    >
                        <Button
                            onClick={() => {
                                setShowFilter(true);
                            }}
                            size={Size.LARGE}
                            icon={<FAIcon icon={faBarsFilter} />}
                            variant={ButtonVariant.OUTLINED}
                            intent={Intent.PRIMARY}
                        />
                    </Tooltip>
                    <div style={{ width: 257, maxWidth: "calc(100% - 84px)" }}>
                        <InputGroup
                            fill
                            rightElement={
                                !_.isEmpty(_.get(filter, "keywords", "")) && (
                                    <Tooltip
                                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                                        boundary={elementRef.current}
                                        content="Clear search"
                                    >
                                        <Button
                                            onClick={() => {
                                                setFilterValue({
                                                    key: "keywords",
                                                    value: "",
                                                });
                                            }}
                                            variant={ButtonVariant.MINIMAL}
                                            icon={<FAIcon icon={faEraser} />}
                                        />
                                    </Tooltip>
                                )
                            }
                            value={_.get(filter, "keywords", "")}
                            onValueChange={(value) => {
                                setFilterValue({ key: "keywords", value });
                            }}
                            leftIcon={<FAIcon icon={faSearch} />}
                            size={Size.LARGE}
                        />
                    </div>
                </ControlGroup>
                <div style={{ marginTop: 20 }}>
                    <CardListCallout />
                </div>
                <div
                    style={{ marginTop: 20 }}
                    className="responsive-grid-container"
                >
                    {permissions.canWriteAgentRegistry && (
                        <Button
                            onClick={() => {
                                setShowNewEntity(true);
                            }}
                            icon={<FAIcon icon={faPlus} />}
                            size={Size.LARGE}
                            fill
                            variant={ButtonVariant.MINIMAL}
                            text="Add agent"
                        />
                    )}
                    {agents.map((agent, index) => (
                        <div key={index} className="grid-item">
                            {search ? (
                                <SearchResultCard entity={agent} />
                            ) : (
                                <RegistryEntityCard entity={agent} />
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(AgentList);
