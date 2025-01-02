import {
    Classes,
    Colors,
    Section,
    SectionCard,
    Switch,
} from "@blueprintjs/core";
import { faCheck, faXmarkLarge } from "@fortawesome/pro-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";
import { faIcon } from "../icon";
export default function EntityGeneral({ general, setGeneral, edit, loading }) {
    const systemAgent = _.get(general, "system_agent", false);
    const { user } = useContext(AuthContext);
    const userRole = _.get(user, "role", null);
    return (
        <Section compact collapsible title="General" style={{ marginTop: 20 }}>
            <SectionCard>
                <div style={{ display: "flex", alignItems: "center" }}>
                    {edit && _.isEqual(userRole, "admin") ? (
                        <Switch
                            checked={systemAgent}
                            className={classNames({
                                "margin-0": true,
                                [Classes.SKELETON]: loading,
                            })}
                            large
                            onChange={(event) => {
                                setGeneral({
                                    ...general,
                                    system_agent: event.target.checked,
                                });
                            }}
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
                    <div style={{ marginLeft: 15 }}>
                        <div>System Agent</div>
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
