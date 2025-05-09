import { FAIcon } from "@/components/FAIcon";
import { Classes, EditableText, EntityTitle, H3 } from "@blueprintjs/core";
import { faQuoteLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
export default function EntityDescription({
    entity,
    isEditing,
    updateEntity,
    loading,
}) {
    const description = _.get(entity, "description", null);
    return (
        <>
            <div style={{ marginBottom: 10 }}>
                <EntityTitle
                    icon={<FAIcon icon={faQuoteLeft} size={25} />}
                    heading={H3}
                    title="Description"
                />
            </div>
            <div className={loading ? Classes.SKELETON : null}>
                {isEditing ? (
                    <EditableText
                        alwaysRenderInput
                        multiline
                        minLines={2}
                        onChange={(value) => {
                            updateEntity({ path: "description", value });
                        }}
                        value={description}
                    />
                ) : !_.isEmpty(description) ? (
                    description
                ) : (
                    "-"
                )}
            </div>
        </>
    );
}
