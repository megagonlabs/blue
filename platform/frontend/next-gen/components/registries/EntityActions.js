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
import _ from "lodash";
import { useMemo } from "react";
import { useShallow } from "zustand/react/shallow";
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
}) {
    const { type, properties } = entity;
    const { user, permissions } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            permissions: state.permissions,
        }))
    );
    const own = _.isEqual(_.get(entity, "created_by", null), user.uid);
    const canEditEntity = useMemo(() => {
        // write_all
        const TYPE_PERMISSION_KEY = {
            agent: "agent_registry",
            input: "agent_registry",
            output: "agent_registry",
            database: "data_registry",
            source: "data_registry",
            model: "model_registry",
            operator: "operator_registry",
        };
        const writeAll = _.includes(
            _.get(user, ["permissions", TYPE_PERMISSION_KEY[type]], []),
            "write_all"
        );
        return own || writeAll;
    }, [user, permissions]);
    const canDuplicateEntity = useMemo(() => {
        const duplicateAgent =
            _.includes(["agent", "agent_group"], type) &&
            permissions.canWriteAgentRegistry;
        const duplicateData =
            _.isEqual("source", type) && permissions.canWriteDataRegistry;
        const duplicateOperator =
            _.isEqual("operator", type) && permissions.canWriteOperatorRegistry;
        const duplicateModel =
            _.isEqual("model", type) && permissions.canWriteModelRegistry;
        return (
            duplicateAgent ||
            duplicateData ||
            duplicateOperator ||
            duplicateModel
        );
    }, [permissions]);
    const canSyncData =
        _.includes(["source", "database", "collection"], type) &&
        _.isFunction(onSynchronize);
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
