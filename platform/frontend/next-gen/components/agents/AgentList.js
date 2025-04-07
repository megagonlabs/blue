import { useAgentStore } from "@/stores/agent-store";
import { useAppStore } from "@/stores/app-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    ControlGroup,
    InputGroup,
    Intent,
    Radio,
    RadioGroup,
    Size,
} from "@blueprintjs/core";
import {
    faArrowLeft,
    faBarsFilter,
    faSearch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import RegistryCard from "../registries/RegistryCard";
function AgentList({ width, height }) {
    const agents = useAgentStore((state) => state.agents);
    const getAgents = useAgentStore((state) => state.getAgents);
    const [showFilter, setShowFilter] = useState(false);
    const darkMode = useAppStore((state) => state.darkMode);
    const variants = {
        open: {
            x: 0,
            display: "block",
            transition: { duration: 0.15 },
        },
        closed: {
            x: -162.727,
            transition: { duration: 0.15 },
            display: "none",
        },
        initial: { x: -162.727, opacity: 1, display: "none" },
    };
    useEffect(() => {
        getAgents();
    }, []);
    return (
        <div style={{ width, height }}>
            <div
                className="full-parent-dimension"
                style={{ padding: 20, position: "relative", overflowY: "auto" }}
            >
                <motion.div
                    variants={variants}
                    initial="initial"
                    animate={showFilter ? "open" : "closed"}
                    className="full-parent-height border-right border-raidus-20"
                    style={{
                        position: "fixed",
                        maxHeight: "calc(100% - 45px)",
                        top: 45,
                        left: 0,
                        zIndex: 1,
                        padding: 20,
                        borderBottomLeftRadius: 10,
                        backgroundColor: darkMode
                            ? Colors.DARK_GRAY2
                            : Colors.WHITE,
                        overflowY: "auto",
                    }}
                >
                    <div
                        className={Classes.TEXT_LARGE}
                        style={{
                            lineHeight: "40px",
                            fontWeight: 600,
                            marginBottom: 20,
                        }}
                    >
                        Filter
                    </div>
                    <Button
                        style={{ position: "absolute", top: 20, right: 20 }}
                        icon={<FAIcon icon={faArrowLeft} />}
                        size={Size.LARGE}
                        variant={ButtonVariant.MINIMAL}
                        onClick={() => setShowFilter(false)}
                    />
                    <RadioGroup label="Keyword">
                        <Radio size={Size.LARGE} label="Hybrid" />
                        <Radio size={Size.LARGE} label="Approximate" />
                    </RadioGroup>
                    <RadioGroup label="Type" style={{ marginTop: 20 }}>
                        <Radio size={Size.LARGE} label="All" />
                        <Radio size={Size.LARGE} label="Agent" />
                        <Radio size={Size.LARGE} label="Input" />
                        <Radio size={Size.LARGE} label="Output" />
                    </RadioGroup>
                </motion.div>
                <ControlGroup>
                    <Button
                        onClick={() => setShowFilter(true)}
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
                <div style={{ marginTop: 20 }} className="registry-entity-list">
                    {agents.map((agent) => (
                        <div className="registry-entity-card">
                            <RegistryCard entity={agent} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(AgentList);
