import { FAIcon } from "@/components/FAIcon";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import { useAppStore } from "@/stores/app-store";
import { useOperatorStore } from "@/stores/operator-store";
import { Colors, ControlGroup, InputGroup, Size } from "@blueprintjs/core";
import { faSearch } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect } from "react";
import RegistryEntityCard from "../RegistryEntityCard";
function OperatorList({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const operators = useOperatorStore((state) => state.operators);
    const getOperators = useOperatorStore((state) => state.getOperators);
    useEffect(() => {
        getOperators();
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
                <ControlGroup>
                    <InputGroup
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
                            <RegistryEntityCard entity={operator} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(OperatorList);
