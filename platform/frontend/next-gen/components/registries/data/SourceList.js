import { FAIcon } from "@/components/FAIcon";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import { useAppStore } from "@/stores/app-store";
import { useSourceStore } from "@/stores/source-store";
import {
    Button,
    ButtonVariant,
    Colors,
    ControlGroup,
    InputGroup,
    Intent,
    Radio,
    RadioGroup,
    Size,
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faSearch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect, useState } from "react";
import FilterPane from "../FilterPane";
import RegistryEntityCard from "../RegistryEntityCard";
function SourceList({ width, height }) {
    const [showFilter, setShowFilter] = useState(false);
    const darkMode = useAppStore((state) => state.dark_mode);
    const data = useSourceStore((state) => state.sources);
    const getSources = useSourceStore((state) => state.getSources);
    useEffect(() => {
        getSources();
    }, []);
    return (
        <div style={{ width, height }}>
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
                    <RadioGroup label="Type" style={{ marginTop: 20 }}>
                        <Radio size={Size.LARGE} label="All" />
                        <Radio size={Size.LARGE} label="Source" />
                        <Radio size={Size.LARGE} label="Database" />
                        <Radio size={Size.LARGE} label="Collection" />
                        <Radio size={Size.LARGE} label="Entity" />
                        <Radio size={Size.LARGE} label="Relation" />
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
                        leftIcon={<FAIcon icon={faSearch} />}
                        size={Size.LARGE}
                    />
                </ControlGroup>
                <div
                    style={{ marginTop: 20 }}
                    className="responsive-grid-container"
                >
                    {data.map((source, index) => (
                        <div key={index} className="grid-item">
                            <RegistryEntityCard entity={source} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(SourceList);
