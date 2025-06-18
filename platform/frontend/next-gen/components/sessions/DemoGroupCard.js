import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Card,
    Classes,
    hideContextMenu,
    Intent,
    Menu,
    MenuItem,
    showContextMenu,
    Size,
} from "@blueprintjs/core";
import {
    faBrowsers,
    faHourglassStart,
    faPen,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useCallback, useMemo } from "react";
import { FAIcon } from "../FAIcon";
import { REGISTRY_ENTITY_ICON_WRAPPER_STYLES } from "../constants";
import EntityDisplayName from "../registries/EntityDisplayName";
import RegistryEntityContainer from "../registries/RegistryEntityContainer";
import RegistryEntityIcon from "../registries/RegistryEntityIcon";
import { AppToaster } from "../toaster";
export default function DemoGroupCard({ agentGroup }) {
    const type = _.get(agentGroup, "type", null);
    const addContainer = useGridStore((state) => state.addContainer);
    const darkMode = useAppStore((state) => state.dark_mode);
    const handleClose = useCallback(() => {
        hideContextMenu();
    }, []);
    const menu = useMemo(
        () => (
            <Menu size={Size.LARGE} onClick={handleClose}>
                <MenuItem
                    intent={Intent.PRIMARY}
                    icon={<FAIcon icon={faPen} />}
                    onClick={() => {
                        addContainer({
                            content: (
                                <RegistryEntityContainer entity={agentGroup} />
                            ),
                        });
                    }}
                    labelElement={<FAIcon icon={faBrowsers} />}
                    text="Edit"
                />
            </Menu>
        ),
        [handleClose, agentGroup]
    );
    const handleContextMenu = useCallback(
        (event) => {
            // ensure `preventDefault` is called just before `showContextMenu` and in the same event handler to prevent the
            // default browser context menu from hiding your custom context menu
            event.preventDefault();
            showContextMenu({
                isDarkTheme: darkMode,
                content: menu,
                onClose: handleClose,
                targetOffset: { left: event.clientX, top: event.clientY },
            });
        },
        [handleClose, menu, darkMode]
    );
    const createNewSession = useSessionStore((state) => state.createNewSession);
    const launchAgentGroupSession = () => {
        createNewSession(agentGroup.name);
        AppToaster.show({
            message: (
                <div>
                    Launching <EntityDisplayName entity={agentGroup} />
                </div>
            ),
            icon: <FAIcon icon={faHourglassStart} />,
        });
    };
    return (
        <Card
            className="full-parent-dimension interactive-card-border"
            style={{ position: "relative", cursor: "context-menu" }}
            onContextMenu={handleContextMenu}
            onClick={launchAgentGroupSession}
        >
            <div
                className="padding-0 overflow-hidden custom-card"
                style={{
                    ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                    position: "absolute",
                    left: 20,
                    top: 20,
                }}
            >
                <RegistryEntityIcon
                    type={type}
                    content={_.get(agentGroup, "icon", null)}
                />
            </div>
            <div
                style={{
                    marginLeft: 60,
                    display: "flex",
                    flexDirection: "column",
                    height: 40,
                    justifyContent: "space-between",
                }}
            >
                <div
                    style={{ fontWeight: 600, lineHeight: "40px" }}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                >
                    <EntityDisplayName entity={agentGroup} />
                </div>
            </div>
            <div
                className={classNames(
                    "multiline-ellipsis-2",
                    Classes.TEXT_MUTED
                )}
                style={{ height: 36, marginTop: 10 }}
            >
                {agentGroup.description}
            </div>
        </Card>
    );
}
