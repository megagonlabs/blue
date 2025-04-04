import { ENTITY_ICON_40, ENTITY_TYPE_LOOKUP } from "@/components/constant";
import { AuthContext } from "@/components/contexts/auth-context";
import EntityIconEditor from "@/components/entity/icon/EntityIconEditor";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    Colors,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowDownToLine,
    faCheck,
    faClone,
    faListDropdown,
    faPen,
    faPlay,
    faRefresh,
    faTrash,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
import { axiosErrorToast } from "../helper";
import EntityIcon from "./EntityIcon";
export default function EntityMain({
    entity,
    updateEntity,
    edit,
    discard,
    setEdit,
    saveEntity,
    loading,
    jsonError,
    enableIcon = false,
}) {
    const router = useRouter();
    const containerStatus = _.get(entity, "container.status", "not exist");
    const deployAgent = () => {
        if (!router.isReady) return;
        axios
            .post(`/containers/agents/agent/${entity.name}`)
            .then(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Deployed ${entity.name} ${entity.type}`,
                });
            })
            .catch((error) => axiosErrorToast(error));
    };
    const routerQueryParams = _.get(router, "query.pathParams", []);
    const routerQueryPath = "/" + routerQueryParams.join("/");
    const duplicateEntity = () => {
        if (!router.isReady) return;
        let params = _.cloneDeep(routerQueryParams);
        params.pop();
        router.push(`/${params.join("/")}/new?entity=${entity.name}`);
    };
    const deleteEntity = () => {
        if (!router.isReady) return;
        axios
            .delete(routerQueryPath)
            .then(() => {
                let params = _.cloneDeep(routerQueryParams);
                if (
                    [
                        "agent",
                        "agent_group",
                        "data",
                        "operator",
                        "model",
                    ].includes(_.nth(params, -2))
                ) {
                    params.pop();
                } else {
                    params.splice(params.length - 2, 2);
                }
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Deleted ${entity.name} ${entity.type}`,
                });
                const lastParam = _.last(params);
                if (_.has(ENTITY_TYPE_LOOKUP, [lastParam, "backtrackCrumb"])) {
                    params[_.size(params) - 1] = _.get(
                        ENTITY_TYPE_LOOKUP,
                        [lastParam, "backtrackCrumb"],
                        lastParam
                    );
                }
                router.push(`/${params.join("/")}`);
            })
            .catch((error) => axiosErrorToast(error));
    };
    const pullImage = () => {
        axios
            .put(`/containers/agents/agent/${entity.name}`)
            .then((response) => {
                AppToaster.show({
                    message: _.get(response, "data.message", "-"),
                    icon: faIcon({ icon: faArrowDownToLine }),
                    intent: Intent.PRIMARY,
                });
            })
            .catch((error) => axiosErrorToast(error));
    };
    const syncData = () => {
        axios
            .put(routerQueryPath + "/sync")
            .then(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Synced ${entity.name} ${entity.type}`,
                });
            })
            .catch((error) => axiosErrorToast(error));
    };
    const [isIconEditorOpen, setIsIconEditorOpen] = useState(false);
    const { user, permissions } = useContext(AuthContext);
    const canEditEntity = (() => {
        // write_own
        const created_by = _.get(entity, "created_by", null);
        if (_.isEqual(created_by, user.uid)) {
            return true;
        }
        // write_all
        const typeToPermissionKey = {
            agent: "agent_registry",
            input: "agent_registry",
            output: "agent_registry",
            database: "data_registry",
            source: "data_registry",
            model: "model_registry",
            operator: "operator_registry",
        };
        const writePermissions = _.get(
            user,
            ["permissions", typeToPermissionKey[entity.type]],
            []
        );
        if (_.includes(writePermissions, "write_all")) {
            return true;
        }
        return false;
    })();
    const canDuplicateEntity = (() => {
        if (
            ["agent", "agent_group"].includes(entity.type) &&
            permissions.canWriteAgentRegistry
        ) {
            return true;
        } else if (
            _.isEqual(entity.type, "source") &&
            permissions.canWriteDataRegistry
        ) {
            return true;
        } else if (
            _.isEqual(entity.type, "operator") &&
            permissions.canWriteOperatorRegistry
        ) {
            return true;
        } else if (
            _.isEqual(entity.type, "model") &&
            permissions.canWriteModelRegistry
        ) {
            return true;
        }
        return false;
    })();
    const isDerivativeAgent = !_.isEqual(entity.scope, "/");
    const canPullImage =
        _.isEqual(entity.type, "agent") &&
        _.has(entity.properties, "image") &&
        !isDerivativeAgent;
    const canDeployAgent =
        _.isEqual(entity.type, "agent") &&
        permissions.canWritePlatformAgents &&
        !_.isEqual(containerStatus, "running") &&
        !isDerivativeAgent;
    const canSyncData = _.includes(
        ["source", "database", "collection"],
        entity.type
    );
    const canDeregister = _.isEqual("database", entity.type);
    const showActionMenu = canEditEntity || canSyncData || canDeregister;
    return (
        <>
            <EntityIconEditor
                entity={entity}
                updateEntity={updateEntity}
                isOpen={isIconEditorOpen}
                setIsIconEditorOpen={setIsIconEditorOpen}
            />
            <Section compact style={{ position: "relative" }}>
                <SectionCard padded={false}>
                    {enableIcon ? (
                        <div
                            style={{
                                position: "absolute",
                                left: 15,
                                top: "50%",
                                height: 40,
                                transform: "translateY(-50%)",
                                msTransform: "translateY(-50%)",
                            }}
                        >
                            <Card
                                onClick={() => {
                                    if (edit) {
                                        setIsIconEditorOpen(true);
                                    }
                                }}
                                style={{
                                    cursor: edit ? "pointer" : null,
                                    ...ENTITY_ICON_40,
                                    backgroundColor: Colors.WHITE,
                                }}
                            >
                                <EntityIcon entity={entity} />
                            </Card>
                        </div>
                    ) : null}
                    <div
                        style={{
                            display: "flex",
                            paddingLeft: enableIcon ? 55 : 0,
                        }}
                    >
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ width: 52.7, margin: "15px 0px 0px 15px" }}
                        >
                            Name
                        </div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                width: `calc(100% - ${
                                    showActionMenu ? 112.16 + 82.7 : 82.7
                                }px)`,
                                padding: `15px ${
                                    showActionMenu ? 20 : 0
                                }px 5px 10px`,
                            }}
                        >
                            {loading ? (
                                <div
                                    style={{ width: 40 }}
                                    className={Classes.SKELETON}
                                >
                                    &nbsp;
                                </div>
                            ) : (
                                entity.name
                            )}
                        </div>
                    </div>
                    <div
                        style={{
                            display: "flex",
                            paddingLeft: enableIcon ? 55 : 0,
                        }}
                    >
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ width: 52.7, margin: "0px 0px 15px 15px" }}
                        >
                            Type
                        </div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                width: `calc(100% - ${
                                    showActionMenu ? 112.16 + 82.7 : 82.7
                                }px)`,
                                padding: `0px ${
                                    showActionMenu ? 20 : 0
                                }px 5px 10px`,
                            }}
                        >
                            {entity.type}
                        </div>
                    </div>
                    {showActionMenu ? (
                        <div
                            style={{
                                position: "absolute",
                                right: 15,
                                top: "50%",
                                transform: "translateY(-50%)",
                                msTransform: "translateY(-50%)",
                            }}
                        >
                            {edit ? (
                                <ButtonGroup size="large">
                                    <Popover
                                        placement="left"
                                        content={
                                            <div style={{ padding: 15 }}>
                                                <Button
                                                    size="large"
                                                    className={
                                                        Classes.POPOVER_DISMISS
                                                    }
                                                    text="Confirm"
                                                    onClick={discard}
                                                    intent={Intent.DANGER}
                                                />
                                            </div>
                                        }
                                    >
                                        <Tooltip
                                            minimal
                                            placement="bottom"
                                            content="Discard"
                                        >
                                            <Button
                                                variant="minimal"
                                                icon={faIcon({
                                                    icon: faXmarkLarge,
                                                })}
                                            />
                                        </Tooltip>
                                    </Popover>
                                    <Button
                                        className={
                                            loading ? Classes.SKELETON : null
                                        }
                                        size="large"
                                        disabled={jsonError}
                                        intent={Intent.SUCCESS}
                                        text="Save"
                                        onClick={saveEntity}
                                        icon={faIcon({ icon: faCheck })}
                                    />
                                </ButtonGroup>
                            ) : (
                                <ButtonGroup
                                    size="large"
                                    variant="minimal"
                                    className={
                                        loading ? Classes.SKELETON : null
                                    }
                                >
                                    <Popover
                                        minimal
                                        placement="bottom-end"
                                        content={
                                            <Menu size="large">
                                                {_.isFunction(setEdit) &&
                                                canEditEntity ? (
                                                    <MenuItem
                                                        onClick={() =>
                                                            setEdit(true)
                                                        }
                                                        intent={Intent.PRIMARY}
                                                        icon={faIcon({
                                                            icon: faPen,
                                                        })}
                                                        text="Edit"
                                                    />
                                                ) : null}
                                                {canDuplicateEntity ? (
                                                    <MenuItem
                                                        icon={faIcon({
                                                            icon: faClone,
                                                        })}
                                                        text="Duplicate"
                                                        onClick={
                                                            duplicateEntity
                                                        }
                                                    />
                                                ) : null}
                                                {canSyncData ? (
                                                    <MenuItem
                                                        intent={Intent.SUCCESS}
                                                        icon={faIcon({
                                                            icon: faRefresh,
                                                        })}
                                                        text="Sync"
                                                        onClick={syncData}
                                                    />
                                                ) : null}
                                                {(canPullImage ||
                                                    canDeployAgent) && (
                                                    <MenuDivider title="Docker" />
                                                )}
                                                {canPullImage && (
                                                    <MenuItem
                                                        icon={faIcon({
                                                            icon: faArrowDownToLine,
                                                        })}
                                                        intent={Intent.PRIMARY}
                                                        onClick={pullImage}
                                                        text="Pull"
                                                    />
                                                )}
                                                {canDeployAgent && (
                                                    <Popover
                                                        placement="left"
                                                        className="full-parent-width"
                                                        content={
                                                            <div
                                                                style={{
                                                                    padding: 15,
                                                                }}
                                                            >
                                                                <Button
                                                                    size="large"
                                                                    onClick={
                                                                        deployAgent
                                                                    }
                                                                    className={
                                                                        Classes.POPOVER_DISMISS
                                                                    }
                                                                    text="Confirm"
                                                                    intent={
                                                                        Intent.SUCCESS
                                                                    }
                                                                />
                                                            </div>
                                                        }
                                                    >
                                                        <MenuItem
                                                            shouldDismissPopover={
                                                                false
                                                            }
                                                            intent={
                                                                Intent.SUCCESS
                                                            }
                                                            icon={faIcon({
                                                                icon: faPlay,
                                                            })}
                                                            text="Deploy"
                                                        />
                                                    </Popover>
                                                )}
                                                {canEditEntity && (
                                                    <>
                                                        <MenuDivider />
                                                        <Popover
                                                            placement="left"
                                                            className="full-parent-width"
                                                            content={
                                                                <div
                                                                    style={{
                                                                        padding: 15,
                                                                    }}
                                                                >
                                                                    <Button
                                                                        size="large"
                                                                        onClick={
                                                                            deleteEntity
                                                                        }
                                                                        className={
                                                                            Classes.POPOVER_DISMISS
                                                                        }
                                                                        text="Confirm"
                                                                        intent={
                                                                            Intent.DANGER
                                                                        }
                                                                    />
                                                                </div>
                                                            }
                                                        >
                                                            <MenuItem
                                                                shouldDismissPopover={
                                                                    false
                                                                }
                                                                intent={
                                                                    Intent.DANGER
                                                                }
                                                                icon={faIcon({
                                                                    icon: faTrash,
                                                                })}
                                                                text="Delete"
                                                            />
                                                        </Popover>
                                                    </>
                                                )}
                                            </Menu>
                                        }
                                    >
                                        <Button
                                            variant="outlined"
                                            text="Actions"
                                            endIcon={faIcon({
                                                icon: faListDropdown,
                                            })}
                                        />
                                    </Popover>
                                </ButtonGroup>
                            )}
                        </div>
                    ) : null}
                </SectionCard>
            </Section>
        </>
    );
}
