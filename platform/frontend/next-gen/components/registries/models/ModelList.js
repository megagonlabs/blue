import { FAIcon } from "@/components/FAIcon";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import { useAppStore } from "@/stores/app-store";
import { useModelStore } from "@/stores/model-store";
import { Colors, ControlGroup, InputGroup, Size } from "@blueprintjs/core";
import { faSearch } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect } from "react";
import RegistryEntityCard from "../RegistryEntityCard";
function ModelList({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const models = useModelStore((state) => state.models);
    const getModels = useModelStore((state) => state.getModels);
    useEffect(() => {
        getModels();
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
                    {models.map((model, index) => (
                        <div key={index} className="grid-item">
                            <RegistryEntityCard entity={model} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(ModelList);
