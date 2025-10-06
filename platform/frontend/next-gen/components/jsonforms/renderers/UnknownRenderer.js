import { FAIcon } from "@/components/FAIcon";
import { NonIdealState } from "@blueprintjs/core";
import { faFileCircleQuestion } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { rankWith } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
const UnknownRenderer = ({ uischema }) => {
    return (
        <div className="custom-card" style={{ padding: 20 }}>
            <NonIdealState
                icon={<FAIcon icon={faFileCircleQuestion} size={50} />}
                title="No applicable renderer found"
                description={JSON.stringify(uischema)}
            />
        </div>
    );
};
export default withJsonFormsCellProps(UnknownRenderer);
export const UnknownTester = rankWith(0, () => {
    return true;
});
