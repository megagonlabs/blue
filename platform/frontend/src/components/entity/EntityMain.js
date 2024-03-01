import {
    Button,
    ButtonGroup,
    Classes,
    Intent,
    Menu,
    MenuItem,
    Popover,
    Section,
    SectionCard,
} from "@blueprintjs/core";
import {
    faCheck,
    faClone,
    faListDropdown,
    faPen,
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
                let params = _.cloneDeep(_.get(router, "query.params", []));
                params.splice(params.length - 2, 2);
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
                            width: "calc(100% - 110.16px - 87.7px)",
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
                            width: "calc(100% - 110.16px - 87.7px)",
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
                                                icon={faIcon({ icon: faPen })}
                                                text="Edit"
                                            />
                                        ) : null}
                                        {_.isEqual(entity.type, "agent") ? (
                                            <MenuItem
                                                icon={faIcon({ icon: faClone })}
                                                text="Duplicate"
                                                onClick={() => {
                                                    if (!router.isReady) return;
                                                    let params = _.cloneDeep(
                                                        _.get(
                                                            router,
                                                            "query.params",
                                                            []
                                                        )
                                                    );
                                                    params.splice(
                                                        params.length - 2,
                                                        2
                                                    );
                                                    router.push(
                                                        `/${params.join(
                                                            "/"
                                                        )}/new?entity=${
                                                            entity.name
                                                        }`
                                                    );
                                                }}
                                            />
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
                                    rightIcon={faIcon({ icon: faListDropdown })}
                                />
                            </Popover>
                        </ButtonGroup>
                    )}
                </div>
            </SectionCard>
        </Section>
    );
}
