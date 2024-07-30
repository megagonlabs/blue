import { ENTITY_ICON_40 } from "@/components/constant";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
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
    faCheck,
    faCircleA,
    faClone,
    faListDropdown,
    faPen,
    faPlay,
    faTrash,
    faXmarkLarge,
} from "@fortawesome/pro-duotone-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import axios from "axios";
import _ from "lodash";
import Image from "next/image";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
import { AuthContext } from "../contexts/auth-context";
import EntityIconEditor from "../EntityIcon/EntityIconEditor";
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
    const { permissions } = useContext(AuthContext);
    const containerStatus = _.get(entity, "container.status", "not exist");
    const deployAgent = () => {
        if (!router.isReady) {
            return;
        }
        axios
            .post(`/containers/agents/agent/${entity.name}`)
            .then(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `${entity.name} ${entity.type} deployed`,
                });
            })
            .catch((error) => {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `${error.name}: ${error.message}`,
                });
            });
    };
    const duplicateEntity = () => {
        if (!router.isReady) {
            return;
        }
        let params = _.cloneDeep(_.get(router, "query.pathParams", []));
        params.pop();
        router.push(`/${params.join("/")}/new?entity=${entity.name}`);
    };
    const deleteEntity = () => {
        if (!router.isReady) {
            return;
        }
        axios
            .delete(router.asPath)
            .then(() => {
                let params = _.cloneDeep(_.get(router, "query.pathParams", []));
                if (["agent", "data"].includes(_.nth(params, -2))) {
                    // keep /agent, /data
                    params.pop();
                } else {
                    params.splice(params.length - 2, 2);
                }
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `${entity.name} ${entity.type} deleted`,
                });
                router.push(`/${params.join("/")}`);
            })
            .catch((error) => {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `${error.name}: ${error.message}`,
                });
            });
    };
    const [isIconEditorOpen, setIsIconEditorOpen] = useState(false);
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
                                }}
                            >
                                {_.isEmpty(entity.icon) ? (
                                    faIcon({ icon: faCircleA, size: 20 })
                                ) : _.startsWith(entity.icon, "data:image/") ? (
                                    <Image
                                        width={40}
                                        height={40}
                                        src={entity.icon}
                                        alt=""
                                    />
                                ) : (
                                    <FontAwesomeIcon
                                        color={entity.icon[1]}
                                        style={{ height: 20, width: 20 }}
                                        icon={["fad", entity.icon[0]]}
                                    />
                                )}
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
                                width: "calc(100% - 112.16px - 82.7px)",
                                padding: "15px 20px 5px 10px",
                            }}
                        >
                            {entity.name}
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
                                width: "calc(100% - 112.16px - 82.7px)",
                                padding: "0px 20px 5px 10px",
                            }}
                        >
                            {entity.type}
                        </div>
                    </div>
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
                            <ButtonGroup large>
                                <Popover
                                    placement="bottom"
                                    content={
                                        <div style={{ padding: 15 }}>
                                            <Button
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
                                            minimal
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
                                    large
                                    disabled={jsonError}
                                    intent={Intent.SUCCESS}
                                    text="Save"
                                    onClick={saveEntity}
                                    icon={faIcon({ icon: faCheck })}
                                />
                            </ButtonGroup>
                        ) : (
                            <ButtonGroup
                                large
                                minimal
                                className={loading ? Classes.SKELETON : null}
                            >
                                <Popover
                                    minimal
                                    placement="bottom-end"
                                    content={
                                        <Menu large>
                                            {_.isFunction(setEdit) ? (
                                                <MenuItem
                                                    onClick={() => {
                                                        setEdit(true);
                                                    }}
                                                    intent={Intent.PRIMARY}
                                                    icon={faIcon({
                                                        icon: faPen,
                                                    })}
                                                    text="Edit"
                                                />
                                            ) : null}
                                            {_.includes(
                                                ["agent", "input", "output"],
                                                entity.type
                                            ) ? (
                                                <MenuItem
                                                    icon={faIcon({
                                                        icon: faClone,
                                                    })}
                                                    text="Duplicate"
                                                    onClick={duplicateEntity}
                                                />
                                            ) : null}
                                            {_.isEqual(entity.type, "agent") &&
                                            permissions.canWritePlatformAgents ? (
                                                <MenuItem
                                                    intent={Intent.SUCCESS}
                                                    icon={faIcon({
                                                        icon: faPlay,
                                                    })}
                                                    disabled={_.isEqual(
                                                        containerStatus,
                                                        "running"
                                                    )}
                                                    text="Deploy"
                                                >
                                                    <MenuItem
                                                        intent={Intent.SUCCESS}
                                                        text="Confirm"
                                                        onClick={deployAgent}
                                                    />
                                                </MenuItem>
                                            ) : null}
                                            {_.isFunction(setEdit) ||
                                            _.isEqual(entity.type, "agent") ? (
                                                <MenuDivider />
                                            ) : null}
                                            <MenuItem
                                                intent={Intent.DANGER}
                                                icon={faIcon({ icon: faTrash })}
                                                text="Delete"
                                            >
                                                <MenuItem
                                                    intent={Intent.DANGER}
                                                    text="Confirm"
                                                    onClick={deleteEntity}
                                                />
                                            </MenuItem>
                                        </Menu>
                                    }
                                >
                                    <Button
                                        outlined
                                        text="Actions"
                                        rightIcon={faIcon({
                                            icon: faListDropdown,
                                        })}
                                    />
                                </Popover>
                            </ButtonGroup>
                        )}
                    </div>
                </SectionCard>
            </Section>
        </>
    );
}
