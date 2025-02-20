import Listens from "@/components/agents/general/Listens";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Classes,
    Colors,
    EditableText,
    FormGroup,
    H5,
    Section,
    SectionCard,
    Switch,
} from "@blueprintjs/core";
import { faCheck, faXmarkLarge } from "@fortawesome/pro-solid-svg-icons";
import { faInfo } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useContext } from "react";
export default function EntityGeneral({
    general,
    setGeneral,
    edit,
    setEdit,
    loading,
}) {
    const systemAgent = _.get(general, "system_agent", false);
    const image = _.toString(_.get(general, "image", ""));
    const displayName = _.toString(_.get(general, "display_name", ""));
    const { user } = useContext(AuthContext);
    const userRole = _.get(user, "role", null);
    return (
        <Section
            compact
            icon={faIcon({ icon: faInfo })}
            title={<H5 className="margin-0">General</H5>}
            style={{ marginTop: 20 }}
        >
            <SectionCard>
                <div style={{ marginBottom: 15, display: "flex", gap: 15 }}>
                    <FormGroup
                        className="margin-0"
                        label={<div className={Classes.TEXT_MUTED}>Image</div>}
                        style={{ width: "50%" }}
                    >
                        <div
                            className={loading && Classes.SKELETON}
                            onDoubleClick={(event) => {
                                setEdit(true);
                                event.stopPropagation();
                            }}
                        >
                            {edit ? (
                                <EditableText
                                    className="full-parent-width"
                                    onChange={(value) =>
                                        setGeneral({ ...general, image: value })
                                    }
                                    value={image}
                                />
                            ) : _.isEmpty(image) ? (
                                "-"
                            ) : (
                                image
                            )}
                        </div>
                    </FormGroup>
                    <FormGroup
                        className="margin-0"
                        label={
                            <div className={Classes.TEXT_MUTED}>
                                Display name
                            </div>
                        }
                        style={{ width: "50%" }}
                        onDoubleClick={(event) => {
                            setEdit(true);
                            event.stopPropagation();
                        }}
                    >
                        <div
                            className={loading && Classes.SKELETON}
                            onDoubleClick={(event) => {
                                setEdit(true);
                                event.stopPropagation();
                            }}
                        >
                            {edit ? (
                                <EditableText
                                    className="full-parent-width"
                                    onChange={(value) =>
                                        setGeneral({
                                            ...general,
                                            display_name: value,
                                        })
                                    }
                                    value={displayName}
                                />
                            ) : _.isEmpty(displayName) ? (
                                "-"
                            ) : (
                                displayName
                            )}
                        </div>
                    </FormGroup>
                </div>
                <div style={{ marginBottom: 15 }}>
                    <Listens
                        edit={edit}
                        general={general}
                        loading={loading}
                        setGeneral={setGeneral}
                    />
                </div>
                <div style={{ display: "flex", alignItems: "center" }}>
                    {edit && _.isEqual(userRole, "admin") ? (
                        <Switch
                            checked={systemAgent}
                            className={classNames({
                                "margin-0": true,
                                [Classes.SKELETON]: loading,
                            })}
                            large
                            onChange={(event) =>
                                setGeneral({
                                    ...general,
                                    system_agent: event.target.checked,
                                })
                            }
                        />
                    ) : (
                        faIcon({
                            icon: systemAgent ? faCheck : faXmarkLarge,
                            className: loading ? Classes.SKELETON : null,
                            style: {
                                color: systemAgent
                                    ? Colors.GREEN3
                                    : Colors.RED3,
                            },
                        })
                    )}
                    <div style={{ marginLeft: edit ? 5 : 15 }}>
                        <div>System agent</div>
                        <div
                            className={classNames(
                                Classes.TEXT_MUTED,
                                Classes.TEXT_SMALL
                            )}
                        >
                            Can only be edited by administrator, and it cannot
                            be removed or stopped.
                        </div>
                    </div>
                </div>
            </SectionCard>
        </Section>
    );
}
