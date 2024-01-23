import {
    Button,
    ButtonGroup,
    Classes,
    Divider,
    Intent,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCheck,
    faPen,
    faPlay,
    faTrash,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
export default function EntityMain({
    entity,
    edit,
    setEdit,
    saveEntity,
    loading,
    jsonError,
}) {
    const router = useRouter();
    const deleteEntity = () => {
        if (!router.isReady) return;
        axios
            .delete(router.asPath)
            .then(() => {
                let path = router.asPath;
                // intended duplicate lines
                path = path.substring(0, path.lastIndexOf("/"));
                path = path.substring(0, path.lastIndexOf("/"));
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `${entity.name} ${entity.type} deleted`,
                });
                router.push(path);
            })
            .catch((error) => {
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `${error.name}: ${error.message}`,
                });
            });
    };
    return (
        <Section compact style={{ position: "relative" }}>
            <SectionCard padded={false}>
                <div style={{ display: "flex" }}>
                    <div
                        className={Classes.TEXT_MUTED}
                        style={{ width: 52.7, margin: "20px 0px 0px 20px" }}
                    >
                        Name
                    </div>
                    <div
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{
                            width: "calc(100% - 178.66px)",
                            padding: "20px 10px 10px 10px",
                        }}
                    >
                        {entity.name}
                    </div>
                </div>
                <div style={{ display: "flex" }}>
                    <div
                        className={Classes.TEXT_MUTED}
                        style={{ width: 52.7, margin: "0px 0px 20px 20px" }}
                    >
                        Type
                    </div>
                    <div
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{
                            width: "calc(100% - 178.66px)",
                            padding: "0px 10px 20px 10px",
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
                        <Button
                            className={loading ? Classes.SKELETON : null}
                            large
                            disabled={jsonError}
                            intent={Intent.SUCCESS}
                            text="Save"
                            onClick={saveEntity}
                            icon={faIcon({ icon: faCheck })}
                        />
                    ) : (
                        <ButtonGroup
                            large
                            minimal
                            className={loading ? Classes.SKELETON : null}
                        >
                            {_.isEqual(entity.type, "agent") ? (
                                <>
                                    <Tooltip
                                        content="Try"
                                        minimal
                                        placement="bottom"
                                    >
                                        <Button
                                            disabled
                                            intent={Intent.SUCCESS}
                                            icon={faIcon({ icon: faPlay })}
                                        />
                                    </Tooltip>
                                    <Divider />
                                </>
                            ) : null}

                            <Tooltip content="Edit" minimal placement="bottom">
                                <Button
                                    disabled={!_.isFunction(setEdit)}
                                    onClick={() => setEdit(true)}
                                    intent={Intent.PRIMARY}
                                    icon={faIcon({ icon: faPen })}
                                />
                            </Tooltip>
                            <Popover
                                placement="bottom-end"
                                content={
                                    <div style={{ padding: 10 }}>
                                        <ButtonGroup large minimal>
                                            <Button
                                                className={
                                                    Classes.POPOVER_DISMISS
                                                }
                                                text="Cancel"
                                            />
                                            <Button
                                                onClick={deleteEntity}
                                                intent={Intent.DANGER}
                                                text="Delete"
                                            />
                                        </ButtonGroup>
                                    </div>
                                }
                            >
                                <Tooltip
                                    content="Delete"
                                    minimal
                                    placement="bottom-end"
                                >
                                    <Button
                                        intent={Intent.DANGER}
                                        icon={faIcon({ icon: faTrash })}
                                    />
                                </Tooltip>
                            </Popover>
                        </ButtonGroup>
                    )}
                </div>
            </SectionCard>
        </Section>
    );
}
