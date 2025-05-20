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
    Overlay2,
    Size,
} from "@blueprintjs/core";
import { faPlus, faSearch } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect, useState } from "react";
import NewEntity from "../NewEntity";
import RegistryEntityCard from "../RegistryEntityCard";
import RegistryEntityContainer from "../RegistryEntityContainer";
function OperatorList({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const operators = useOperatorStore((state) => state.operators);
    const getOperators = useOperatorStore((state) => state.getOperators);
    const addContainer = useGridStore((state) => state.addContainer);
    const [showNewEntity, setShowNewEntity] = useState(false);
    useEffect(() => {
        getOperators();
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
                    <NewEntity callback={callback} type="operator" />
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
                    <Button
                        onClick={() => {
                            setShowNewEntity(true);
                        }}
                        size={Size.LARGE}
                        fill
                        variant={ButtonVariant.MINIMAL}
                        text="Add operator"
                        icon={<FAIcon icon={faPlus} />}
                    />
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(OperatorList);
