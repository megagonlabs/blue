import { useAgentStore } from "@/stores/agent-store";
import { useAuthStore } from "@/stores/auth-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowDownToLine,
    faCheck,
    faClockRotateLeft,
    faClone,
    faEllipsisV,
    faPenLine,
    faPlay,
    faRefresh,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useMemo } from "react";
import { useShallow } from "zustand/react/shallow";
import { ENTITY_TYPE_LOOKUP } from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
export default function EntityActions({
    entity,
    isEditing,
    setIsEditing,
    handleSave,
    handleDiscard,
    loading,
    onDelete,
    onSynchronize,
    onDuplicate,
}) {
    const { name, type, properties, created_by = null } = entity;
    const { user, permissions } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            permissions: state.permissions,
        }))
    );
    const own = _.isEqual(created_by, user.uid);
    const canEditEntity = useMemo(() => {
        // write_all
        const permissionKey = _.get(
            ENTITY_TYPE_LOOKUP,
            [type, "permissionKey"],
            null
        );
        const writeAll = _.includes(
            _.get(user, ["permissions", permissionKey], []),
            "write_all"
        );
        return own || writeAll;
    }, [user, permissions]);
    const canDuplicateEntity = useMemo(() => {
        const duplicateAgent =
            _.includes(["agent", "agent_group"], type) &&
            permissions.canWriteAgentRegistry;
        const duplicateData =
            _.isEqual(type, "source") && permissions.canWriteDataRegistry;
        const duplicateOperator =
            _.isEqual(type, "operator") && permissions.canWriteOperatorRegistry;
        const duplicateModel =
            _.isEqual(type, "model") && permissions.canWriteModelRegistry;
        const duplicateServer =
            _.isEqual(type, "server") && permissions.canWriteToolRegistry;
        return (
            (duplicateAgent ||
                duplicateData ||
                duplicateOperator ||
                duplicateModel ||
                duplicateServer) &&
            _.isFunction(onDuplicate)
        );
    }, [permissions, onDuplicate]);
    const canSyncData =
        _.includes(
            ["source", "database", "collection", "server", "tool", "operator"],
            type
        ) && _.isFunction(onSynchronize);
    const canPullImage =
        _.isEqual(type, "agent") &&
        _.has(properties, "image") &&
        !_.isEmpty(_.get(properties, "image"));
    const containerStatus = _.get(entity, "container.status", "not exist");
    const canDeployAgent = useMemo(() => {
        // write_all
        const writeAll = _.includes(
            _.get(user, "permissions.platform_agents", []),
            "write_all"
        );
        return (
            _.isEqual(type, "agent") &&
            (own || writeAll) &&
            !_.isEqual(containerStatus, "running") &&
            canPullImage
        );
    }, [user, permissions, containerStatus]);
    const { appToaster, showAxiosErrorToast } = useToaster();
    const { getAgents } = useAgentStore(
        useShallow((state) => ({ getAgents: state.getAgents }))
    );
    const onDeploy = () => {
        axios
            .post(`/containers/agents/agent/${name}`)
            .then(() => {
                appToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Deployed ${name} ${type}`,
                });
                setTimeout(() => {
                    getAgents();
                }, 800);
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            });
    };
    const onPull = () => {
        axios
            .put(`/containers/agents/agent/${name}`)
            .then((response) => {
                appToaster.show({
                    message: _.get(response, "data.message", "-"),
                    icon: <FAIcon icon={faArrowDownToLine} />,
                    intent: Intent.PRIMARY,
                });
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            });
    };
    const showActionMenu = _.some([
        canEditEntity,
        canDuplicateEntity,
        canSyncData,
        canPullImage,
        canDeployAgent,
    ]);
    if (!showActionMenu) {
        return null;
    }
    if (isEditing) {
        return (
            <ButtonGroup size={Size.LARGE}>
                {_.isFunction(handleDiscard) && (
                    <Popover
                        placement="bottom"
                        content={
                            <div style={{ padding: 10 }}>
                                <Button
                                    text="Discard"
                                    onClick={handleDiscard}
                                />
                            </div>
                        }
                    >
                        <Tooltip content="Discard" placement="bottom">
                            <Button
                                disabled={loading}
                                variant={ButtonVariant.MINIMAL}
                                icon={<FAIcon icon={faClockRotateLeft} />}
                            />
                        </Tooltip>
                    </Popover>
                )}
                <Button
                    disabled={loading}
                    text="Save"
                    intent={Intent.SUCCESS}
                    onClick={handleSave}
                    icon={<FAIcon icon={faCheck} />}
                />
            </ButtonGroup>
        );
    }
    return (
        <Popover
            minimal
            placement="bottom-end"
            content={
                <Menu size={Size.LARGE}>
                    {canEditEntity && (
                        <MenuItem
                            intent={Intent.PRIMARY}
                            text="Edit"
                            onClick={() => {
                                setIsEditing(true);
                            }}
                            icon={<FAIcon icon={faPenLine} />}
                        />
                    )}
                    {canDuplicateEntity && (
                        <MenuItem
                            text="Duplicate"
                            icon={<FAIcon icon={faClone} />}
                            onClick={onDuplicate}
                        />
                    )}
                    {canSyncData && (
                        <MenuItem
                            intent={Intent.SUCCESS}
                            icon={<FAIcon icon={faRefresh} />}
                            text="Synchronize"
                            onClick={onSynchronize}
                        />
                    )}
                    {(canPullImage || canDeployAgent) && (
                        <MenuDivider title="Docker" />
                    )}
                    {canPullImage && (
                        <MenuItem
                            onClick={onPull}
                            intent={Intent.PRIMARY}
                            icon={<FAIcon icon={faArrowDownToLine} />}
                            text="Pull"
                        />
                    )}
                    {canDeployAgent && (
                        <Popover
                            className="full-parent-width"
                            placement="left"
                            content={
                                <div style={{ padding: 10 }}>
                                    <Button
                                        className={Classes.POPOVER_DISMISS}
                                        intent={Intent.SUCCESS}
                                        onClick={onDeploy}
                                        text="Confirm"
                                    />
                                </div>
                            }
                        >
                            <MenuItem
                                shouldDismissPopover={false}
                                intent={Intent.SUCCESS}
                                icon={<FAIcon icon={faPlay} />}
                                text="Deploy"
                            />
                        </Popover>
                    )}
                    {canEditEntity && (
                        <>
                            <MenuDivider />
                            <Popover
                                className="full-parent-width"
                                placement="left"
                                content={
                                    <div style={{ padding: 10 }}>
                                        <Button
                                            onClick={onDelete}
                                            className={Classes.POPOVER_DISMISS}
                                            intent={Intent.DANGER}
                                            text="Confirm"
                                        />
                                    </div>
                                }
                            >
                                <MenuItem
                                    shouldDismissPopover={false}
                                    intent={Intent.DANGER}
                                    icon={<FAIcon icon={faTrash} />}
                                    text="Delete"
                                />
                            </Popover>
                        </>
                    )}
                </Menu>
            }
        >
            <Tooltip>
                <Button
                    disabled={loading}
                    intent={Intent.PRIMARY}
                    size={Size.LARGE}
                    icon={<FAIcon icon={faEllipsisV} />}
                />
            </Tooltip>
        </Popover>
    );
}
