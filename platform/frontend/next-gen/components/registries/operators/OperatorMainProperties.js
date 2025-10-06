import { FAIcon } from "@/components/FAIcon";
import { EntityTitle, H3 } from "@blueprintjs/core";
import { faMemo } from "@fortawesome/sharp-duotone-solid-svg-icons";
import Categories from "../attributes/Categories";
export default function OperatorMainProperties({
    isEditing,
    loading,
    properties,
    updateMainProperties,
}) {
    return (
        <div>
            <div style={{ marginBottom: 10 }}>
                <EntityTitle
                    icon={<FAIcon icon={faMemo} size={25} />}
                    heading={H3}
                    title="Main"
                />
            </div>
            <Categories
                updateMainProperties={updateMainProperties}
                isEditing={false}
                properties={properties}
                loading={loading}
            />
        </div>
    );
}
