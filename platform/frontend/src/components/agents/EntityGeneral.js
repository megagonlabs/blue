import { Checkbox, Classes, Section, SectionCard } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
export default function EntityGeneral({
    entity,
    edit,
    updateEntity,
    setEdit,
    loading = false,
}) {
    return (
        <Section compact collapsible title="General" style={{ marginTop: 20 }}>
            <SectionCard>
                <div style={{ display: "flex", alignItems: "center" }}>
                    <Checkbox
                        checked={_.get(
                            entity,
                            "properties.system_agent",
                            false
                        )}
                        className="margin-0"
                        large
                        onChange={(event) => {
                            updateEntity({
                                path: "properties",
                                value: {
                                    ...entity.properties,
                                    system_agent: event.target.checked,
                                },
                            });
                        }}
                    />
                    <div>
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
