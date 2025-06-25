import { useAppStore } from "@/stores/app-store";
import { usePlatformStore } from "@/stores/platform-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Colors,
    Size,
} from "@blueprintjs/core";
import {
    faIdCardClip,
    faInboxFull,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useState } from "react";
import { useGridContainerContext } from "../contexts/GridContainerContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import AuthenticationConfigurations from "./configurations/AuthenticationConfigurations";
import SessionConfigurations from "./configurations/SessionConfigurations";
const SECTIONS = [
    { icon: faInboxFull, text: "Sessions" },
    { icon: faIdCardClip, text: "Authentication" },
];
function PlatformConfigurations({ width, height }) {
    const { gridContainerId } = useGridContainerContext();
    const darkMode = useAppStore((state) => state.dark_mode);
    const getConfigurations = usePlatformStore(
        (state) => state.getConfigurations
    );
    useState(() => {
        getConfigurations();
    }, []);
    return (
        <div style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{
                        padding: 10,
                        overflowY: "auto",
                        minWidth: 182,
                    }}
                    className="border-right"
                >
                    <ButtonGroup
                        className="full-parent-width"
                        vertical
                        size={Size.LARGE}
                        alignText={Alignment.START}
                        variant={ButtonVariant.MINIMAL}
                    >
                        {SECTIONS.map((section, index) => (
                            <Button
                                key={index}
                                icon={<FAIcon icon={section.icon} />}
                                text={section.text}
                                onClick={() => {
                                    const element = _.first(
                                        document.querySelectorAll(
                                            `.container-${gridContainerId} .setting-container-section-${
                                                index + 1
                                            }`
                                        )
                                    );
                                    if (element) {
                                        element.scrollIntoView({
                                            behavior: "smooth",
                                            block: "nearest",
                                            inline: "nearest",
                                        });
                                    }
                                }}
                            />
                        ))}
                    </ButtonGroup>
                </div>
                <div
                    className={`full-parent-dimension container-${gridContainerId}`}
                    style={{
                        backgroundColor: darkMode ? Colors.BLACK : null,
                        padding: 20,
                        overflowY: "auto",
                        overflowX: "hidden",
                    }}
                >
                    <SessionConfigurations />
                    <div style={{ marginTop: 20 }}>
                        <AuthenticationConfigurations />
                    </div>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(PlatformConfigurations);
