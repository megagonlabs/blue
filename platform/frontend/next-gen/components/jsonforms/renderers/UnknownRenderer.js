import { FAIcon } from "@/components/FAIcon";
import { NonIdealState } from "@blueprintjs/core";
import { faCompassDrafting } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { rankWith } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
const UnknownRenderer = ({ uischema }) => {
    return (
        <NonIdealState
            icon={<FAIcon icon={faCompassDrafting} size={50} />}
            title="No applicable renderer found"
            description={JSON.stringify(uischema)}
        />
    );
};
export default withJsonFormsCellProps(UnknownRenderer);
export const UnknownTester = rankWith(0, () => {
    return true;
});
