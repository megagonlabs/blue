import {
    HEX_TRANSPARENCY,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useToolStore } from "@/stores/tool-store";
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
import {
    faBarsFilter,
    faEraser,
    faPlus,
    faSearch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _, { debounce } from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import FilterPane from "../FilterPane";
import NewEntity from "../NewEntity";
import RegistryEntityCard from "../RegistryEntityCard";
import RegistryEntityContainer from "../RegistryEntityContainer";
import SearchResultCard from "../SearchResultCard";
function ToolList({ width, height }) {
    const { tools, getTools, filter, setFilterValue, search } = useToolStore(
        useShallow((state) => ({
            tools: state.tools,
            getTools: state.getTools,
            filter: state.filter,
            search: state.search,
            setFilterValue: state.setFilterValue,
        }))
    );
    const [showFilter, setShowFilter] = useState(false);
    const darkMode = useAppStore((state) => state.dark_mode);
    const [showNewEntity, setShowNewEntity] = useState(false);
    const addContainer = useGridStore((state) => state.addContainer);
    useEffect(() => {
        getTools();
    }, []);
    const debounced = useCallback(debounce(getTools, 800), [getTools]);
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
                    <NewEntity callback={callback} type="server" />
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
                </FilterPane>
                <ControlGroup>
                    <Button
                        onClick={() => {
                            setShowFilter(true);
                        }}
                        size={Size.LARGE}
                        icon={<FAIcon icon={faBarsFilter} />}
                        variant={ButtonVariant.OUTLINED}
                        intent={Intent.PRIMARY}
                        text="Filter"
                    />
                    <InputGroup
                        rightElement={
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
                        }
                        value={_.get(filter, "keywords", "")}
                        onValueChange={(value) => {
                            setFilterValue({ key: "keywords", value });
                        }}
                        leftIcon={<FAIcon icon={faSearch} />}
                        size={Size.LARGE}
                    />
                </ControlGroup>
                <div
                    style={{ marginTop: 20 }}
                    className="responsive-grid-container"
                >
                    {tools.map((server, index) => (
                        <div key={index} className="grid-item">
                            {search ? (
                                <SearchResultCard entity={server} />
                            ) : (
                                <RegistryEntityCard entity={server} />
                            )}
                        </div>
                    ))}
                    <Button
                        onClick={() => {
                            setShowNewEntity(true);
                        }}
                        icon={<FAIcon icon={faPlus} />}
                        size={Size.LARGE}
                        fill
                        variant={ButtonVariant.MINIMAL}
                        text="Add server"
                    />
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(ToolList);
