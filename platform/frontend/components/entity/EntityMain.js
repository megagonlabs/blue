import {
    Button,
    ButtonGroup,
    Classes,
    Intent,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import { faPen, faTrash } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import { useRouter } from "next/router";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
export default function EntityMain({ entity }) {
    const router = useRouter();
    const deleteEntity = () => {
        if (!router.isReady) return;
        axios
            .delete(router.asPath)
            .then(() => {
                let path = router.asPath;
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
        <Section style={{ position: "relative" }}>
            <SectionCard>
                <div style={{ display: "flex" }}>
                    <div className={Classes.TEXT_MUTED} style={{ width: 52.7 }}>
                        Name
                    </div>
                    <div
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{ width: "calc(100% - 152.7px)" }}
                    >
                        {entity.name}
                    </div>
                </div>
                <div style={{ display: "flex" }}>
                    <div className={Classes.TEXT_MUTED} style={{ width: 52.7 }}>
                        Type
                    </div>
                    <div
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{ width: "calc(100% - 152.7px)" }}
                    >
                        {entity.type}
                    </div>
                </div>
                <ButtonGroup
                    large
                    minimal
                    style={{ position: "absolute", right: 15, top: 18 }}
                >
                    <Tooltip content="Edit" minimal placement="bottom">
                        <Button
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
                                        className={Classes.POPOVER_DISMISS}
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
            </SectionCard>
        </Section>
    );
}
