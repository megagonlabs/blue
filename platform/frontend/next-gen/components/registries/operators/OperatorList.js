import {
    HEX_TRANSPARENCY,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useOperatorStore } from "@/stores/operator-store";
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
function OperatorList({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const [showFilter, setShowFilter] = useState(false);
    const { operators, getOperators, filter, setFilterValue, search } =
        useOperatorStore(
            useShallow((state) => ({
                operators: state.operators,
                getOperators: state.getOperators,
                filter: state.filter,
                search: state.search,
                setFilterValue: state.setFilterValue,
            }))
        );
    const addContainer = useGridStore((state) => state.addContainer);
    const [showNewEntity, setShowNewEntity] = useState(false);
    useEffect(() => {
        getOperators();
    }, [getOperators]);
    const debounced = useCallback(debounce(getOperators, 800), [getOperators]);
    useEffect(() => {
        debounced();
    }, [filter, debounced]);
    const callback = (entity) => {
        setShowNewEntity(false);
        addContainer({
            content: (
                <RegistryEntityContainer entity={entity} registry="operator" />
            ),
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
                    <NewEntity
                        callback={callback}
                        type="server"
                        registry="operator"
                    />
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
                    {operators.map((operator, index) => (
                        <div key={index} className="grid-item">
                            {search ? (
                                <SearchResultCard entity={operator} />
                            ) : (
                                <RegistryEntityCard
                                    entity={operator}
                                    registry="operator"
                                />
                            )}
                        </div>
                    ))}
                    <Button
                        onClick={() => {
                            setShowNewEntity(true);
                        }}
                        size={Size.LARGE}
                        fill
                        variant={ButtonVariant.MINIMAL}
                        text="Add server"
                        icon={<FAIcon icon={faPlus} />}
                    />
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(OperatorList);
