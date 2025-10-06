import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Callout,
    Classes,
    Colors,
    hideContextMenu,
    Intent,
    Menu,
    MenuItem,
    showContextMenu,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faBrowsers,
    faComments,
    faThumbTack,
    faThumbTackSlash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useCallback, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import { useGridContainerContext } from "../contexts/GridContainerContext";
import { useToaster } from "../contexts/ToasterContext";
import SessionContainer from "./SessionContainer";
import SessionDisplayName from "./SessionDisplayName";
import SessionMemberStack from "./SessionMemberStack";
import UserAvatar from "./UserAvatar";
import MessageContent from "./messages/MessageContent";
export default function SessionCard({ sessionId }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { details, messages, streams } = useSessionStore(
        useShallow((state) => ({
            details: _.get(state, ["sessions", sessionId, "details"], {}),
            messages: _.get(state, ["sessions", sessionId, "messages"], {}),
            streams: _.get(state, ["sessions", sessionId, "streams"], {}),
        }))
    );
    const owner = _.get(details, "created_by");
    const { gridContainerId } = useGridContainerContext();
    const description = _.get(details, "description", "");
    const { addContainer, replaceContainer } = useGridStore(
        useShallow((state) => ({
            addContainer: state.addContainer,
            replaceContainer: state.replaceContainer,
        }))
    );
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
                            icon: faComments,
                            title: <SessionDisplayName sessionId={sessionId} />,
                            content: <SessionContainer sessionId={sessionId} />,
                        });
                    }}
                />
            </Menu>
        ),
        [handleClose, sessionId, addContainer]
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
        [handleClose, darkMode, menu]
    );
    const filteredMessages = messages.filter((message) => {
        const stream = _.get(message, "stream", null);
        if (
            _.get(message, "metadata.ags.WORKSPACE_ONLY") ||
            _.endsWith(stream, "PROGRESS:STREAM")
        ) {
            return false;
        }
        return true;
    });
    const user = useAuthStore((state) => state.user);
    const pinned = _.get(details, ["pinned", owner], false);
    const [loading, setLoading] = useState(false);
    const lastMessage = useMemo(() => {
        if (!_.isEmpty(filteredMessages)) {
            const last = _.last(filteredMessages);
            const uid = _.get(last, "metadata.id", null);
            const createdBy = _.get(last, "metadata.created_by", null);
            const isUser = _.isEqual(createdBy, "USER");
            return {
                contentType: _.get(last, "contentType", null),
                streamData: _.get(streams, [last.stream, "data"], []),
                own: isUser && _.isEqual(user.uid, uid),
            };
        }
        return null;
    }, [user, filteredMessages]);
    const setSessionDetails = useSessionStore(
        (state) => state.setSessionDetails
    );
    const { appToaster } = useToaster();
    const handlePinSession = () => {
        setLoading(true);
        axios
            .put(`/sessions/session/${sessionId}/${pinned ? "un" : ""}pin`)
            .then(() => {
                setSessionDetails({
                    sessionId,
                    fields: [{ path: ["pinned", user.uid], value: !pinned }],
                });
                appToaster.show({
                    icon: (
                        <FAIcon
                            icon={pinned ? faThumbTackSlash : faThumbTack}
                            size={pinned ? 18 : 16}
                        />
                    ),
                    message: `Session "${sessionId}" ${
                        pinned ? "un" : ""
                    }pinned`,
                });
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <div
            onContextMenu={handleContextMenu}
            className="full-parent-dimension session-list-card interactive-card-border"
            style={{
                padding: 20,
                borderRadius: 2,
                position: "relative",
                cursor: "context-menu",
                backgroundColor: darkMode
                    ? Colors.DARK_GRAY1
                    : Colors.LIGHT_GRAY5,
            }}
            onDoubleClick={() => {
                replaceContainer({
                    id: gridContainerId,
                    icon: faComments,
                    title: <SessionDisplayName sessionId={sessionId} />,
                    content: <SessionContainer sessionId={sessionId} />,
                });
            }}
        >
            <div
                className="full-parent-height session-card-actions"
                style={{
                    position: "absolute",
                    maxHeight: "calc(100% - 2px)",
                    maxWidth: "calc(100% - 2px)",
                    display: "none",
                    right: 1,
                    top: 1,
                    width: 200,
                    zIndex: 1,
                    padding: 20,
                    background: darkMode
                        ? "linear-gradient(to left, rgba(37,42,49,1) 0%, rgba(37,42,49,1) 100px, rgba(255,255,255,0) 99%, rgba(255,255,255,0) 100%)"
                        : "linear-gradient(to left, rgba(255,255,255,1) 0%, rgba(255,255,255,1) 100px, rgba(255,255,255,0) 99%, rgba(255,255,255,0) 100%)",
                }}
            >
                <ButtonGroup
                    className="vertical-center"
                    style={{ right: 19 }}
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                >
                    <Tooltip
                        content={pinned ? "Unpin" : "Pin"}
                        placement="left"
                    >
                        <Button
                            loading={loading}
                            onClick={handlePinSession}
                            onDoubleClick={(event) => {
                                event.stopPropagation();
                            }}
                            icon={
                                <FAIcon
                                    icon={
                                        pinned ? faThumbTackSlash : faThumbTack
                                    }
                                    size={pinned ? 18 : 16}
                                />
                            }
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
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
                <div
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{ fontWeight: 600 }}
                >
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
            {!_.isEmpty(lastMessage) && (
                <Callout
                    icon={null}
                    intent={lastMessage.own ? Intent.PRIMARY : null}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{
                        marginTop: 10,
                        width: "fit-content",
                        maxWidth: "100%",
                    }}
                >
                    <MessageContent
                        isPreview={true}
                        contentType={lastMessage.contentType}
                        streamData={lastMessage.streamData}
                    />
                </Callout>
            )}
            <SessionMemberStack
                sessionId={sessionId}
                style={{ marginTop: 10 }}
            />
        </div>
    );
}
