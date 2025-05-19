import { FAIcon } from "@/components/FAIcon";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useModelStore } from "@/stores/model-store";
import {
    Button,
    ButtonVariant,
    Colors,
    ControlGroup,
    InputGroup,
    Size,
} from "@blueprintjs/core";
import { faPlus, faSearch } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect } from "react";
import RegistryEntityCard from "../RegistryEntityCard";
import RegistryEntityContainer from "../RegistryEntityContainer";
function ModelList({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const models = useModelStore((state) => state.models);
    const getModels = useModelStore((state) => state.getModels);
    const addContainer = useGridStore((state) => state.addContainer);
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
                    <Button
                        onClick={() => {
                            addContainer({
                                content: (
                                    <RegistryEntityContainer
                                        entity={{ scope: "/", type: "model" }}
                                        create={true}
                                    />
                                ),
                            });
                        }}
                        size={Size.LARGE}
                        fill
                        variant={ButtonVariant.MINIMAL}
                        text="Add model"
                        icon={<FAIcon icon={faPlus} />}
                    />
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(ModelList);
