import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Card,
    Classes,
    hideContextMenu,
    Menu,
    MenuItem,
    showContextMenu,
    Size,
} from "@blueprintjs/core";
import { faBrowsers } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useCallback, useMemo } from "react";
import { REGISTRY_ENTITY_ICON_WRAPPER_STYLES } from "../constants";
import { FAIcon } from "../FAIcon";
import RegistryEntityContainer from "./RegistryEntityContainer";
import RegistryEntityIcon from "./RegistryEntityIcon";
export default function SearchResultCard({ entity }) {
    const addContainer = useGridStore((state) => state.addContainer);
    const darkMode = useAppStore((state) => state.dark_mode);
    const handleClose = useCallback(() => {
        hideContextMenu();
    }, []);
    const menu = useMemo(
        () => (
            <Menu size={Size.LARGE} onClick={handleClose}>
                <MenuItem
                    icon={<FAIcon icon={faBrowsers} />}
                    text="Open in new window"
                    onClick={() => {
                        addContainer({
                            content: (
                                <RegistryEntityContainer entity={entity} />
                            ),
                        });
                    }}
                />
            </Menu>
        ),
        [handleClose, entity]
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
    return (
        <Card
            className="full-parent-dimension"
            style={{
                padding: 20,
                position: "relative",
                cursor: "context-menu",
            }}
            onContextMenu={handleContextMenu}
        >
            <div
                className="custom-card"
                style={{
                    ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                    position: "absolute",
                    left: 20,
                    top: 20,
                }}
            >
                <RegistryEntityIcon type={entity.type} />
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
                    style={{ fontWeight: 600 }}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                >
                    {entity.name}
                </div>
                <div className={Classes.TEXT_DISABLED}>{entity.score}</div>
            </div>
            {!_.includes(["model", "operator"], entity.type) && (
                <div
                    style={{ marginTop: 10 }}
                    className={classNames(Classes.TEXT_OVERFLOW_ELLIPSIS)}
                >
                    {entity.scope}
                </div>
            )}
        </Card>
    );
}
