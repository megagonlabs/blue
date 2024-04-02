import { Callout, Colors, Intent } from "@blueprintjs/core";
import { rankWith } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
const UnknownRenderer = ({ uischema }) => {
    return (
        <div
            style={{
                backgroundColor: Colors.WHITE,
                border: `2px dashed ${Colors.RED3}`,
                borderRadius: 2,
                overflow: "hidden",
                whiteSpace: "wrap",
            }}
        >
            <Callout icon={null} intent={Intent.DANGER}>
                No applicable renderer found for "{_.get(uischema, "type", "-")}
                ".
            </Callout>
        </div>
    );
};
export default withJsonFormsCellProps(UnknownRenderer);
export const UnknownTester = rankWith(0, () => true);
