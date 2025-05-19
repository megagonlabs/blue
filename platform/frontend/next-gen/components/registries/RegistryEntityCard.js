import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Card,
    Classes,
    Colors,
    hideContextMenu,
    Intent,
    Menu,
    MenuItem,
    showContextMenu,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faDocker } from "@fortawesome/free-brands-svg-icons";
import { faBrowsers } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
    DOCKER_CONTAINER_STATUS_LOOKUP,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "../constants";
import { FAIcon } from "../FAIcon";
import HorizontalScrollable from "../HorizontalScrollable";
import EntityDisplayName from "./EntityDisplayName";
import RegistryEntityContainer from "./RegistryEntityContainer";
import RegistryEntityIcon from "./RegistryEntityIcon";
export default function RegistryEntityCard({ entity }) {
    const type = _.get(entity, "type", null);
    const categories = _.get(entity, "properties.categories", []);
    const containerStatus = _.get(entity, "container.status", "not exist");
    const [extra, setExtra] = useState(null);
    const darkMode = useAppStore((state) => state.dark_mode);
    useEffect(() => {
        if (_.includes(["agent", "operator"], type)) {
            setExtra(_.toString(_.get(entity, "properties.image")));
        } else if (_.isEqual("source", type)) {
            let protocol = _.get(entity, "properties.connection.protocol");
            let host = _.get(entity, "properties.connection.host");
            let port = _.get(entity, "properties.connection.port");
            setExtra(`${protocol}://${host}:${port}`);
        } else {
            setExtra(null);
        }
    }, [entity.properties]);
    const handleClose = useCallback(() => {
        hideContextMenu();
    }, []);
    const addContainer = useGridStore((state) => state.addContainer);
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
            style={{ position: "relative", cursor: "context-menu" }}
            onContextMenu={handleContextMenu}
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
                    content={_.get(entity, "icon", null)}
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
                    style={{ fontWeight: 600 }}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                >
                    <EntityDisplayName entity={entity} />
                </div>
                {_.isEqual(type, "agent") && (
                    <div
                        className={Classes.TEXT_DISABLED}
                        style={_.get(
                            DOCKER_CONTAINER_STATUS_LOOKUP,
                            [containerStatus, "style"],
                            null
                        )}
                    >
                        <FAIcon icon={faDocker} style={{ marginRight: 5 }} />
                        container:&nbsp;{containerStatus}
                    </div>
                )}
            </div>
            <div
                className={classNames(
                    "multiline-ellipsis-2",
                    Classes.TEXT_MUTED
                )}
                style={{ height: 36, marginTop: 10 }}
            >
                {entity.description}
            </div>
            {!_.isEmpty(categories) && (
                <div style={{ height: 20, marginTop: 10 }}>
                    <HorizontalScrollable
                        backgroundColor={
                            darkMode ? Colors.DARK_GRAY2 : Colors.WHITE
                        }
                    >
                        <div style={{ display: "inline-flex", gap: 10 }}>
                            {categories.map((category, index) => (
                                <Tag
                                    key={index}
                                    style={{ display: "inline-table" }}
                                    minimal
                                >
                                    {category}
                                </Tag>
                            ))}
                        </div>
                    </HorizontalScrollable>
                </div>
            )}
            {!_.isEmpty(extra) && (
                <Tag minimal intent={Intent.PRIMARY} style={{ marginTop: 10 }}>
                    {extra}
                </Tag>
            )}
        </Card>
    );
}
