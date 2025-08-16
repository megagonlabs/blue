import JSONEditor from "@/components/codemirror/JSONEditor";
import { ENTITY_MAIN_INFO_PROPERTY_KEYS } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import { Classes, EntityTitle, H3, Pre } from "@blueprintjs/core";
import { faBracketsCurly } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
export default function EntityProperties({
    entity,
    isEditing,
    updateEntity,
    loading,
}) {
    const properties = _.omit(
        _.get(entity, "properties", {}),
        ENTITY_MAIN_INFO_PROPERTY_KEYS
    );
    return (
        <>
            <div style={{ marginBottom: 10 }}>
                <EntityTitle
                    icon={<FAIcon icon={faBracketsCurly} size={25} />}
                    heading={H3}
                    title="Properties"
                />
            </div>
            <div
                className={classNames({
                    "custom-card": isEditing,
                    [Classes.SKELETON]: loading,
                })}
            >
                {isEditing ? (
                    <JSONEditor
                        jsonObject={properties}
                        setBack={(object) => {
                            updateEntity({ path: "properties", value: object });
                        }}
                    />
                ) : (
                    <Pre className="margin-0" style={{ overflow: "hidden" }}>
                        <JSONViewer json={properties} />
                    </Pre>
                )}
            </div>
        </>
    );
}
