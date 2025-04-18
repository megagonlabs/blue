import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Callout,
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
import { FAIcon } from "../FAIcon";
import SessionContainer from "./SessionContainer";
import SessionDisplayName from "./SessionDisplayName";
import SessionMemberStack from "./SessionMemberStack";
import UserAvatar from "./UserAvatar";
export default function SessionCard({ sessionId }) {
    const darkMode = useAppStore((state) => state.darkMode);
    const sessions = useSessionStore((state) => state.sessions);
    const details = _.get(sessions, [sessionId, "details"], {});
    const owner = _.get(details, "created_by");
    const description = _.get(details, "description", "");
    const messages = _.get(sessions, [sessionId, "messages"], []);
    const handleClose = useCallback(() => {
        hideContextMenu();
    }, []);
    const addContainer = useGridStore((state) => state.addContainer);
    const addSessionContainer = () =>
        addContainer(
            <SessionDisplayName sessionId={sessionId} />,
            <SessionContainer sessionId={sessionId} />
        );
    const menu = useMemo(
        () => (
            <Menu size={Size.LARGE} onClick={handleClose}>
                <MenuItem
                    icon={<FAIcon icon={faBrowsers} />}
                    text="Open in new window"
                    onClick={addSessionContainer}
                />
            </Menu>
        ),
        [handleClose]
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
                targetOffset: {
                    left: event.clientX,
                    top: event.clientY,
                },
            });
        },
        [handleClose, menu, darkMode]
    );
    return (
        <Card
            onContextMenu={handleContextMenu}
            className="full-parent-dimension"
            style={{ position: "relative", cursor: "context-menu" }}
        >
            <div style={{ position: "absolute", left: 20, top: 20 }}>
                <UserAvatar userId={owner} />
            </div>
            <div
                style={{
                    marginLeft: 50,
                    display: "flex",
                    flexDirection: "column",
                    height: 40,
                    justifyContent: "space-between",
                }}
            >
                <div style={{ fontWeight: 600 }}>
                    <SessionDisplayName sessionId={sessionId} />
                </div>
                <div
                    className={classNames(
                        Classes.TEXT_MUTED,
                        Classes.TEXT_OVERFLOW_ELLIPSIS
                    )}
                >
                    {!_.isEmpty(description) ? description : sessionId}
                </div>
            </div>
            {!_.isEmpty(messages) && (
                <Callout
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{
                        marginTop: 10,
                        width: "fit-content",
                        maxWidth: "100%",
                    }}
                >
                    message
                </Callout>
            )}
            <SessionMemberStack
                sessionId={sessionId}
                style={{ marginTop: 10 }}
            />
        </Card>
    );
}
