import { useAgentStore } from "@/stores/agent-store";
import { useAppStore } from "@/stores/app-store";
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
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faPlus,
    faSearch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect, useState } from "react";
import { FAIcon } from "../../FAIcon";
import withAutoSizer from "../../hocs/withAutoSizer";
import FilterPane from "../FilterPane";
import NewEntity from "../NewEntity";
import RegistryEntityCard from "../RegistryEntityCard";
import RegistryEntityContainer from "../RegistryEntityContainer";
function AgentList({ width, height }) {
    const agents = useAgentStore((state) => state.agents);
    const getAgents = useAgentStore((state) => state.getAgents);
    const [showFilter, setShowFilter] = useState(false);
    const darkMode = useAppStore((state) => state.dark_mode);
    const [showNewEntity, setShowNewEntity] = useState(false);
    const addContainer = useGridStore((state) => state.addContainer);
    useEffect(() => {
        getAgents();
    }, []);
    const callback = (entity) => {
        setShowNewEntity(false);
        addContainer({
            content: <RegistryEntityContainer entity={entity} />,
        });
    };
    return (
        <div style={{ width, height }}>
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
                    <RadioGroup label="Type" style={{ marginTop: 20 }}>
                        <Radio size={Size.LARGE} label="All" />
                        <Radio size={Size.LARGE} label="Agent" />
                        <Radio size={Size.LARGE} label="Input" />
                        <Radio size={Size.LARGE} label="Output" />
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
                    {agents.map((agent, index) => (
                        <div key={index} className="grid-item">
                            <RegistryEntityCard entity={agent} />
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
                        text="Add agent"
                    />
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(AgentList);
